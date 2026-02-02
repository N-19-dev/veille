# veille_tech.py
# Veille techno — filtrage **hebdomadaire** (semaine ISO, Europe/Paris)
# - Récupération RSS/Atom + autodécouverte
# - Extraction (readability)
# - Filtres éditoriaux
# - Classification par mots-clés
# - Dédup / SQLite
# - Export JSON/Markdown dans export/<YYYYwWW> + lien export/latest

import asyncio
import hashlib
import json
import os
import re
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from zoneinfo import ZoneInfo
from urllib.parse import urlparse, urljoin

import aiohttp
import feedparser
import urllib.robotparser as robotparser
import yaml
from aiolimiter import AsyncLimiter
from bs4 import BeautifulSoup
from pydantic import BaseModel
from readability import Document
from tqdm.asyncio import tqdm

# Import du logger structuré et content classifier
from logger import get_logger, MetricsCollector
from content_classifier import detect_content_type
from sentry_init import init_sentry, set_tag, capture_exception

# Initialisation du logger
logger = get_logger("veille_tech", log_file="logs/veille_tech.log", level="INFO")

# Initialisation Sentry (si DSN configuré)
init_sentry(environment="production")

# -----------------------
# Models & Config
# -----------------------

class Category(BaseModel):
    key: str
    title: str
    keywords: List[str]

class Source(BaseModel):
    name: str
    url: str
    type: Optional[str] = None  # 'youtube', 'podcast', or None for regular RSS
    extract_links: bool = False  # True = newsletter, extract individual article URLs

class StorageCfg(BaseModel):
    sqlite_path: str

class CrawlCfg(BaseModel):
    concurrency: int = 8
    per_host_rps: float = 1.0
    timeout_sec: int = 20
    user_agent: str = "VeilleTechBot/1.0 (+https://example.local/veille)"
    lookback_days: int = 7  # pour compat (non utilisé ici)

class ExportCfg(BaseModel):
    out_dir: str = "export"
    make_markdown_digest: bool = True
    max_items_per_cat: int = 50

class NotifyCfg(BaseModel):
    slack_webhook_env: Optional[str] = None

class AppConfig(BaseModel):
    storage: StorageCfg
    crawl: CrawlCfg
    export: ExportCfg
    notify: NotifyCfg
    categories: List[Category]
    sources: List[Source]

# -----------------------
# Storage
# -----------------------

SQL_SCHEMA = """
CREATE TABLE IF NOT EXISTS items(
  id TEXT PRIMARY KEY,
  url TEXT,
  title TEXT,
  summary TEXT,
  content TEXT,
  published_ts INTEGER,
  source_name TEXT,
  category_key TEXT,
  created_ts INTEGER
);
CREATE INDEX IF NOT EXISTS idx_items_cat_pub ON items(category_key, published_ts DESC);
"""

@contextmanager
def db_conn(path: str):
    conn = sqlite3.connect(path)
    try:
        yield conn
    finally:
        conn.commit()
        conn.close()

def ensure_db(path: str):
    with db_conn(path) as conn:
        conn.executescript(SQL_SCHEMA)
        # Migration: ajouter content_type si la colonne n'existe pas
        cursor = conn.execute("PRAGMA table_info(items)")
        columns = [row[1] for row in cursor.fetchall()]
        if "content_type" not in columns:
            logger.info("Migrating database: adding content_type column")
            conn.execute("ALTER TABLE items ADD COLUMN content_type TEXT DEFAULT 'technical'")
            # Créer l'index après avoir ajouté la colonne
            conn.execute("CREATE INDEX IF NOT EXISTS idx_items_content_type ON items(content_type)")

        # Migration: ajouter source_type si la colonne n'existe pas
        cursor = conn.execute("PRAGMA table_info(items)")
        columns = [row[1] for row in cursor.fetchall()]
        if "source_type" not in columns:
            logger.info("Migrating database: adding source_type column")
            conn.execute("ALTER TABLE items ADD COLUMN source_type TEXT DEFAULT 'article'")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_items_source_type ON items(source_type)")

def upsert_item(path: str, item: Dict[str, Any]):
    with db_conn(path) as conn:
        conn.execute("""
            INSERT OR IGNORE INTO items(id, url, title, summary, content, published_ts, source_name, category_key, created_ts, content_type, source_type)
            VALUES (:id, :url, :title, :summary, :content, :published_ts, :source_name, :category_key, :created_ts, :content_type, :source_type)
        """, item)

def query_latest_by_cat(path: str, limit_per_cat: int,
                        min_ts: Optional[int] = None,
                        max_ts: Optional[int] = None) -> Dict[str, List[Dict[str, Any]]]:
    with db_conn(path) as conn:
        cats = [r[0] for r in conn.execute("SELECT DISTINCT category_key FROM items")]
        result: Dict[str, List[Dict[str, Any]]] = {}
        for c in cats:
            if min_ts is not None and max_ts is not None:
                rows = conn.execute("""
                    SELECT url, title, summary, published_ts, source_name, content_type
                    FROM items
                    WHERE category_key=? AND published_ts>=? AND published_ts<?
                    ORDER BY published_ts DESC
                    LIMIT ?
                """, (c, min_ts, max_ts, limit_per_cat)).fetchall()
            elif min_ts is not None:
                rows = conn.execute("""
                    SELECT url, title, summary, published_ts, source_name, content_type
                    FROM items
                    WHERE category_key=? AND published_ts>=?
                    ORDER BY published_ts DESC
                    LIMIT ?
                """, (c, min_ts, limit_per_cat)).fetchall()
            else:
                rows = conn.execute("""
                    SELECT url, title, summary, published_ts, source_name, content_type
                    FROM items
                    WHERE category_key=?
                    ORDER BY published_ts DESC
                    LIMIT ?
                """, (c, limit_per_cat)).fetchall()
            result[c] = [
                dict(url=row[0], title=row[1], summary=row[2], published_ts=row[3], source_name=row[4], content_type=row[5] or 'technical')
                for row in rows
            ]
        return result
    
def to_markdown(groups: Dict[str, List[Dict[str, Any]]],
                categories_by_key: Dict[str, Any],
                header: Optional[str] = None) -> str:
    """
    Rend un digest Markdown à partir des groupes {category_key: [items]}.
    On respecte l'ordre des catégories tel que défini dans la config
    (via categories_by_key), mais on n'affiche que celles qui ont des items.
    """
    lines: List[str] = []
    lines.append(f"# {header}" if header else "# Veille Tech — Digest")

    # Parcourt les catégories dans l'ordre de la config
    for cat_key in categories_by_key.keys():
        items = groups.get(cat_key, [])
        if not items:
            continue
        cat_title = categories_by_key[cat_key].title if hasattr(categories_by_key[cat_key], "title") else cat_key
        lines.append(f"\n## {cat_title}\n")
        for it in items:
            dt = datetime.fromtimestamp(it["published_ts"], tz=timezone.utc).strftime("%Y-%m-%d")
            title = it.get("title", "(sans titre)")
            url = it.get("url", "#")
            src = it.get("source_name", "source")
            summary = (it.get("summary") or "").strip()
            lines.append(f"- [{title}]({url}) — {src} · {dt}")
            if summary:
                snippet = summary[:240] + ("…" if len(summary) > 240 else "")
                lines.append(f"  - {snippet}")
    lines.append("")  # fin avec une ligne vide
    return "\n".join(lines)

# -----------------------
# Robots.txt helper
# -----------------------

class RobotsCache:
    def __init__(self, user_agent: str):
        self.cache: Dict[str, robotparser.RobotFileParser] = {}
        self.ua = user_agent

    async def allowed(self, session: aiohttp.ClientSession, url: str) -> bool:
        host = urlparse(url).netloc
        if host not in self.cache:
            rp = robotparser.RobotFileParser()
            robots_url = f"{urlparse(url).scheme}://{host}/robots.txt"
            try:
                async with session.get(robots_url, timeout=10) as r:
                    if r.status == 200:
                        rp.parse((await r.text()).splitlines())
                    else:
                        rp.default_allow = True
            except Exception:
                rp.default_allow = True
            self.cache[host] = rp
        return self.cache[host].can_fetch(self.ua, url)

# -----------------------
# Weekly window
# -----------------------

def week_bounds(tz_name: str = "Europe/Paris", week_offset: int = 0) -> tuple[int, int, str, str, str]:
    """
    (start_ts_utc, end_ts_utc, label_sem, start_str, end_str)
    start = lundi 00:00 local ; end = lundi suivant 00:00 (excl.)
    label_sem = 'YYYYwWW'
    """
    now_local = datetime.now(ZoneInfo(tz_name))
    monday_local = (now_local - timedelta(days=now_local.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    start_local = monday_local + timedelta(weeks=week_offset)
    end_local = start_local + timedelta(days=7)
    year, week_num, _ = start_local.isocalendar()
    label_sem = f"{year}w{week_num:02d}"
    start_ts = int(start_local.astimezone(timezone.utc).timestamp())
    end_ts = int(end_local.astimezone(timezone.utc).timestamp())
    return start_ts, end_ts, label_sem, start_local.strftime("%Y-%m-%d"), end_local.strftime("%Y-%m-%d")

def within_window(ts: int, start_ts: int, end_ts: int) -> bool:
    return ts is not None and (ts >= start_ts) and (ts < end_ts)

# -----------------------
# Fetching & Parsing
# -----------------------

class Fetcher:
    def __init__(self, cfg: CrawlCfg):
        self.cfg = cfg
        self.limiters: Dict[str, AsyncLimiter] = {}

    def limiter_for(self, url: str) -> AsyncLimiter:
        host = urlparse(url).netloc
        if host not in self.limiters:
            rps = max(self.cfg.per_host_rps, 0.1)
            self.limiters[host] = AsyncLimiter(max_rate=rps, time_period=1)
        return self.limiters[host]

    async def get(self, session: aiohttp.ClientSession, url: str) -> Optional[bytes]:
        limiter = self.limiter_for(url)
        async with limiter:
            try:
                async with session.get(url, timeout=self.cfg.timeout_sec, headers={"User-Agent": self.cfg.user_agent}) as resp:
                    if resp.status == 200:
                        return await resp.read()
                    elif resp.status == 404:
                        logger.warning(f"URL not found (404)", url=url)
                    elif resp.status >= 500:
                        logger.error(f"Server error ({resp.status})", url=url)
                    elif resp.status == 429:
                        logger.warning(f"Rate limited (429)", url=url)
                    else:
                        logger.debug(f"Non-200 status: {resp.status}", url=url)
            except asyncio.TimeoutError:
                logger.warning("Request timeout", url=url, timeout=self.cfg.timeout_sec)
            except aiohttp.ClientConnectorError as e:
                logger.error("Connection error", url=url, error=str(e))
            except aiohttp.ClientError as e:
                logger.error("Client error", url=url, error=str(e))
            except Exception as e:
                logger.error("Unexpected error during fetch", url=url, error=str(e))
        return None

def hash_id(url: str, title: str) -> str:
    h = hashlib.sha256()
    h.update(url.encode("utf-8")); h.update(b"||"); h.update(title.encode("utf-8"))
    return h.hexdigest()

def extract_main_content(html: str, base_url: str) -> str:
    try:
        doc = Document(html)
        content_html = doc.summary()
        soup = BeautifulSoup(content_html, "lxml")
        for tag in soup.find_all(["a", "img"]):
            attr = "href" if tag.name == "a" else "src"
            if tag.has_attr(attr):
                tag[attr] = urljoin(base_url, tag[attr])
        for t in soup(["script", "style"]):
            t.decompose()
        return soup.get_text("\n", strip=True)
    except Exception:
        soup = BeautifulSoup(html, "lxml")
        return soup.get_text("\n", strip=True)

def normalize_ts(entry: Dict[str, Any]) -> Optional[int]:
    for key in ("published_parsed", "updated_parsed", "created_parsed"):
        if key in entry and entry[key]:
            try:
                dt = datetime(*entry[key][:6], tzinfo=timezone.utc)
                return int(dt.timestamp())
            except Exception:
                pass
    for key in ("published", "updated", "created", "date"):
        val = entry.get(key)
        if val:
            try:
                dt = parsedate_to_datetime(val)
                if dt.tzinfo is None: dt = dt.replace(tzinfo=timezone.utc)
                else: dt = dt.astimezone(timezone.utc)
                return int(dt.timestamp())
            except Exception:
                pass
    for tag in entry.get("tags", []) or []:
        for k in ("term", "label"):
            val = tag.get(k)
            if val:
                try:
                    dt = parsedate_to_datetime(val)
                    if dt.tzinfo is None: dt = dt.replace(tzinfo=timezone.utc)
                    else: dt = dt.astimezone(timezone.utc)
                    return int(dt.timestamp())
                except Exception:
                    continue
    return None

def discover_feed_links(html: str, base_url: str) -> List[str]:
    soup = BeautifulSoup(html, "html5lib")
    urls: List[str] = []
    for link in soup.find_all("link", attrs={"rel": ["alternate", "ALTERNATE"]}):
        t = link.get("type", "")
        if "rss" in t.lower() or "atom" in t.lower():
            href = link.get("href")
            if href:
                urls.append(urljoin(base_url, href))
    for a in soup.find_all("a", href=True):
        if any(k in a["href"].lower() for k in ("rss", "atom", "feed")):
            urls.append(urljoin(base_url, a["href"]))
    return list(dict.fromkeys(urls))


def extract_newsletter_urls(content: str) -> List[str]:
    """
    Extrait les URLs des articles mentionnés dans une newsletter.

    Filtre les URLs internes (unsubscribe, settings, etc.) et
    garde uniquement les articles de blogs/tech.
    """
    import re

    # Extraire toutes les URLs
    urls = re.findall(r'https?://[^\s<>"\']+', content)

    # Nettoyer les URLs (enlever ponctuation finale)
    cleaned_urls = []
    for url in urls:
        url = url.rstrip('.,;:)\'"')
        # Filtrer les URLs non-articles
        lower_url = url.lower()

        # Exclure les URLs internes/admin
        exclude_patterns = [
            'unsubscribe', 'subscribe', 'mailto:', 'settings', 'preferences',
            'manage', 'profile', 'account', 'login', 'signup', 'register',
            'twitter.com', 'linkedin.com/in/', 'facebook.com', 'youtube.com/channel',
            'github.com/sponsors', 'patreon.com', 'buymeacoffee', 'ko-fi.com',
            'substack.com/subscribe', 'share', 'utm_', 'ref=', '?source=',
            '.png', '.jpg', '.gif', '.svg', '.pdf', '.mp3', '.mp4',
            'substackcdn.com',  # Image CDN
            'cdn.substack.com',  # CDN assets
            '/image/', '/images/',  # Image paths
        ]

        if any(pattern in lower_url for pattern in exclude_patterns):
            continue

        # Garder uniquement les URLs de blogs/articles (heuristique)
        include_domains = [
            'medium.com', 'dev.to', 'hashnode', 'substack.com',
            'techblog', 'engineering', 'blog', 'article', 'post',
            'openai.com', 'anthropic.com', 'google.com/blog',
            'aws.amazon.com/blogs', 'cloud.google.com/blog',
            'netflix', 'uber', 'airbnb', 'spotify', 'dropbox',
            'databricks.com', 'snowflake.com', 'confluent.io',
            'preset.io', 'dagster.io', 'airbyte.com', 'dbt.com',
        ]

        # Accepter si c'est un domaine connu OU si l'URL contient des patterns d'articles
        is_article = (
            any(domain in lower_url for domain in include_domains) or
            '/blog/' in lower_url or
            '/posts/' in lower_url or
            '/article/' in lower_url or
            '/news/' in lower_url or
            '/index/' in lower_url  # OpenAI style
        )

        if is_article and url not in cleaned_urls:
            cleaned_urls.append(url)

    return cleaned_urls


def extract_source_from_url(url: str) -> dict[str, str] | None:
    """
    Extrait les informations de source depuis une URL d'article.

    Gère les plateformes (Medium, dev.to, Substack) en extrayant
    l'auteur ou la publication spécifique.

    Retourne un dict avec 'name', 'base_url', 'feed_url' (si connu).
    """
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    path = parsed.path

    # Skip les réseaux sociaux et agrégateurs purs
    skip_domains = [
        'github.com', 'reddit.com', 'news.ycombinator.com',
        'twitter.com', 'x.com', 'linkedin.com', 'youtube.com',
        'facebook.com', 'instagram.com',
    ]
    if any(skip in domain for skip in skip_domains):
        return None

    # === PLATEFORMES AVEC FEEDS PAR AUTEUR/PUBLICATION ===

    # Medium: medium.com/publication, medium.com/@author, ou publication.medium.com
    if 'medium.com' in domain:
        # Cas 1: sous-domaine (netflixtechblog.medium.com)
        if domain != 'medium.com' and not domain.startswith('www.'):
            subdomain = domain.replace('.medium.com', '')
            name = subdomain.replace('-', ' ').title()
            feed_url = f"https://{domain}/feed"
            return {
                "name": f"{name} (Medium)",
                "domain": domain,
                "base_url": f"https://{domain}",
                "feed_url": feed_url,
            }
        # Cas 2: medium.com/publication ou medium.com/@author
        parts = [p for p in path.split('/') if p]
        if not parts:
            return None
        pub_or_author = parts[0]  # Ex: "airbnb-engineering" ou "@username"
        if pub_or_author.startswith('@'):
            name = pub_or_author[1:].replace('-', ' ').title()
        else:
            name = pub_or_author.replace('-', ' ').title()
        # Medium RSS: https://medium.com/feed/publication ou /feed/@author
        feed_url = f"https://medium.com/feed/{pub_or_author}"
        return {
            "name": f"{name} (Medium)",
            "domain": f"medium.com/{pub_or_author}",
            "base_url": f"https://medium.com/{pub_or_author}",
            "feed_url": feed_url,
        }

    # Dev.to: dev.to/username
    if 'dev.to' in domain:
        parts = [p for p in path.split('/') if p]
        if not parts:
            return None
        username = parts[0]
        name = username.replace('_', ' ').replace('-', ' ').title()
        # Dev.to RSS: https://dev.to/feed/username
        feed_url = f"https://dev.to/feed/{username}"
        return {
            "name": f"{name} (Dev.to)",
            "domain": f"dev.to/{username}",
            "base_url": f"https://dev.to/{username}",
            "feed_url": feed_url,
        }

    # Substack: author.substack.com
    if 'substack.com' in domain:
        # Extraire le sous-domaine (author.substack.com)
        subdomain = domain.replace('.substack.com', '')
        if subdomain and subdomain != 'www':
            name = subdomain.replace('-', ' ').title()
            feed_url = f"https://{domain}/feed"
            return {
                "name": f"{name} (Substack)",
                "domain": domain,
                "base_url": f"https://{domain}",
                "feed_url": feed_url,
            }
        return None

    # Hashnode: author.hashnode.dev ou hashnode.com/@author
    if 'hashnode' in domain:
        if '.hashnode.dev' in domain:
            subdomain = domain.replace('.hashnode.dev', '')
            name = subdomain.replace('-', ' ').title()
            feed_url = f"https://{domain}/rss.xml"
            return {
                "name": f"{name} (Hashnode)",
                "domain": domain,
                "base_url": f"https://{domain}",
                "feed_url": feed_url,
            }
        return None

    # === SITES CLASSIQUES ===

    # Extraire le nom depuis le domaine
    # netflix.techblog.com -> Netflix Tech Blog
    # engineering.uber.com -> Uber Engineering
    # blog.example.com -> Example Blog

    name_parts = domain.replace('www.', '').split('.')

    # Patterns connus
    if 'techblog' in name_parts[0]:
        # netflixtechblog.com -> Netflix Tech Blog
        company = name_parts[0].replace('techblog', '')
        name = f"{company.title()} Tech Blog" if company else "Tech Blog"
    elif domain.startswith('engineering.') or domain.startswith('eng.'):
        # engineering.uber.com -> Uber Engineering
        name = f"{name_parts[1].title()} Engineering"
    elif domain.startswith('blog.'):
        # blog.cloudflare.com -> Cloudflare Blog
        name = f"{name_parts[1].title()} Blog"
    elif 'engineering' in domain:
        # someengineering.com -> Some Engineering
        company = name_parts[0].replace('engineering', '')
        name = f"{company.title()} Engineering" if company else name_parts[0].title()
    else:
        # example.com/blog -> Example Blog
        name = name_parts[0].title()
        if '/blog' in url.lower():
            name += " Blog"

    # URL de base pour le feed
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    return {
        "name": name,
        "domain": domain,
        "base_url": base_url,
    }


def add_discovered_source(
    source_info: dict[str, str],
    feed_url: str,
    config_path: str = "config.yaml",
    discovered_by: str = "newsletter"
) -> bool:
    """
    Ajoute une nouvelle source découverte à config.yaml et au registre.

    Retourne True si la source a été ajoutée, False si déjà existante.
    """
    # Charger la config actuelle
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # Vérifier si la source existe déjà (par URL ou domaine similaire)
    existing_urls = {s.get('url', '').lower() for s in config.get('sources', [])}
    existing_domains = set()
    for s in config.get('sources', []):
        try:
            existing_domains.add(urlparse(s.get('url', '')).netloc.lower())
        except:
            pass

    domain = source_info.get('domain', '')
    if feed_url.lower() in existing_urls or domain in existing_domains:
        return False

    # Ajouter la nouvelle source
    new_source = {
        "name": source_info['name'],
        "url": feed_url,
    }

    # Trouver la section sources et ajouter à la fin
    config['sources'].append(new_source)

    # Sauvegarder config.yaml
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    # Ajouter au registre des sources découvertes
    discovered_path = Path("export/discovered_sources.json")
    discovered_path.parent.mkdir(parents=True, exist_ok=True)

    discovered = []
    if discovered_path.exists():
        with open(discovered_path, 'r', encoding='utf-8') as f:
            discovered = json.load(f)

    discovered.append({
        "name": source_info['name'],
        "url": feed_url,
        "domain": domain,
        "discovered_by": discovered_by,
        "discovered_at": datetime.now(timezone.utc).isoformat(),
    })

    with open(discovered_path, 'w', encoding='utf-8') as f:
        json.dump(discovered, f, ensure_ascii=False, indent=2)

    logger.info(f"New source discovered and added",
                name=source_info['name'],
                feed=feed_url,
                discovered_by=discovered_by)

    return True


async def discover_and_add_source(
    session: aiohttp.ClientSession,
    article_url: str,
    config_path: str = "config.yaml",
    discovered_by: str = "newsletter"
) -> bool:
    """
    Découvre le feed RSS d'un article et l'ajoute aux sources si nouveau.
    """
    source_info = extract_source_from_url(article_url)
    if not source_info:
        return False

    base_url = source_info['base_url']

    # Si la plateforme fournit déjà le feed URL (Medium, dev.to, Substack...)
    feed_url = source_info.get('feed_url')

    # Essayer de découvrir le feed RSS si pas déjà connu
    common_feed_paths = [
        '/feed', '/feed/', '/rss', '/rss/', '/feed.xml', '/rss.xml',
        '/atom.xml', '/index.xml', '/blog/feed', '/blog/rss',
        '/blog/feed.xml', '/blog/rss.xml', '/feeds/posts/default',
    ]

    # URLs à exclure (pas des feeds)
    excluded_patterns = ['sitemap', 'favicon', 'robots.txt', '.png', '.jpg', '.ico', '.css', '.js']

    def is_valid_feed_url(url: str) -> bool:
        """Vérifie que l'URL ressemble à un feed RSS/Atom."""
        lower = url.lower()
        if any(p in lower for p in excluded_patterns):
            return False
        # Doit contenir des indicateurs de feed
        feed_indicators = ['feed', 'rss', 'atom', '.xml']
        return any(ind in lower for ind in feed_indicators)

    # Si pas de feed_url prédéfini, essayer de le découvrir
    if not feed_url:
        # D'abord essayer de trouver le feed dans la page de l'article
        try:
            async with session.get(article_url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    html = await resp.text()
                    soup = BeautifulSoup(html, 'lxml')
                    # Chercher les liens RSS/Atom avec rel="alternate"
                    for link in soup.find_all('link', rel='alternate'):
                        link_type = (link.get('type') or '').lower()
                        if 'rss' in link_type or 'atom' in link_type:
                            href = link.get('href')
                            if href:
                                candidate = urljoin(article_url, href)
                                if is_valid_feed_url(candidate):
                                    feed_url = candidate
                                    break
        except:
            pass

        # Si pas trouvé, essayer les chemins communs
        if not feed_url:
            for path in common_feed_paths:
                test_url = base_url + path
                try:
                    async with session.head(test_url, timeout=aiohttp.ClientTimeout(total=5), allow_redirects=True) as resp:
                        if resp.status == 200:
                            content_type = resp.headers.get('content-type', '').lower()
                            # Vérifier que c'est un vrai feed XML
                            if ('xml' in content_type or 'rss' in content_type or 'atom' in content_type) and 'html' not in content_type:
                                feed_url = test_url
                                break
                except:
                    continue

    if not feed_url:
        return False

    # Pour les sites classiques, vérifier que l'URL est valide
    if not source_info.get('feed_url') and not is_valid_feed_url(feed_url):
        return False

    # Valider que le feed est parsable
    try:
        async with session.get(feed_url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            if resp.status == 200:
                content = await resp.text()
                parsed = feedparser.parse(content)
                if not parsed.entries and not parsed.feed.get('title'):
                    return False  # Pas un feed valide
    except:
        return False

    # Ajouter la source
    return add_discovered_source(source_info, feed_url, config_path, discovered_by)


# -----------------------
# Classification & Filters
# -----------------------

def classify(title: str, summary: str, categories: List[Category]) -> Optional[str]:
    blob = f"{title} {summary}".lower()
    best_key, best_hits = None, 0
    for c in categories:
        hits = sum(1 for kw in c.keywords if kw.lower() in blob)
        if hits > best_hits:
            best_hits, best_key = hits, c.key
    return best_key if best_hits > 0 else None

def is_editorial_article(url: str, cfg: dict, text: str = "") -> bool:
    c = cfg.get("crawl", {})
    domain = urlparse(url).netloc.lower()
    for bad in c.get("blacklist_domains", []):
        if bad.replace("*","") in domain:
            return False
    wl = c.get("whitelist_domains", [])
    if wl and not any(good in domain for good in wl):
        return False
    path = urlparse(url).path.lower()
    allow_re = c.get("path_allow_regex"); deny_re = c.get("path_deny_regex")
    if deny_re and re.search(deny_re, path): return False
    if allow_re and not re.search(allow_re, path): return False
    min_len = int(c.get("min_text_length", 0))
    if min_len and len(text or "") < min_len: return False
    return True

# -----------------------
# Notification
# -----------------------

async def notify_slack(webhook_url: str, message: str, session: aiohttp.ClientSession):
    """Envoie une notification Slack via webhook."""
    try:
        async with session.post(webhook_url, json={"text": message}) as resp:
            if resp.status == 200:
                logger.info("Slack notification sent successfully")
            else:
                logger.warning(f"Slack notification failed with status {resp.status}")
    except Exception as e:
        logger.error("Failed to send Slack notification", error=str(e))

# -----------------------
# Pipeline
# -----------------------

async def run(config_path: str = "config.yaml"):
    # Initialiser les métriques
    metrics = MetricsCollector()

    logger.info("Starting veille tech pipeline", config=config_path)

    cfg = AppConfig(**yaml.safe_load(Path(config_path).read_text(encoding="utf-8")))
    ensure_db(cfg.storage.sqlite_path)

    fetcher = Fetcher(cfg.crawl)
    robots = RobotsCache(cfg.crawl.user_agent)

    out_root = Path(cfg.export.out_dir); out_root.mkdir(parents=True, exist_ok=True)
    categories_by_key = {c.key: c for c in cfg.categories}

    now_ts = int(datetime.now(tz=timezone.utc).timestamp())
    week_offset = int(os.getenv("WEEK_OFFSET", "0"))
    week_start_ts, week_end_ts, week_label, week_start_str, week_end_str = week_bounds("Europe/Paris", week_offset=week_offset)

    logger.info(f"Processing week {week_label}", start=week_start_str, end=week_end_str, offset=week_offset)

    async with aiohttp.ClientSession(headers={"User-Agent": cfg.crawl.user_agent}) as session:
        # 1) Prépare les feeds
        feed_urls: List[Dict[str, str]] = []

        async def prepare_source(src: Source):
            # Skip robots.txt check for YouTube/Podcast RSS feeds (public feeds meant to be consumed)
            if src.type not in ("youtube", "podcast"):
                if not await robots.allowed(session, src.url): return
            raw = await fetcher.get(session, src.url)
            if not raw: return
            try: text = raw.decode("utf-8", errors="ignore")
            except Exception: text = raw.decode("latin-1", errors="ignore")
            lower = text.lower()
            if "<rss" in lower or "<feed" in lower:
                feed_urls.append({"name": src.name, "feed": src.url, "type": src.type, "extract_links": src.extract_links}); return
            discovered = discover_feed_links(text, src.url)
            if discovered:
                for f in discovered:
                    p = urlparse(f).path.lower()
                    deny_re = getattr(cfg.crawl, "path_deny_regex", None)
                    allow_re = getattr(cfg.crawl, "path_allow_regex", None)
                    if deny_re and re.search(deny_re, p): continue
                    if allow_re and not re.search(allow_re, p): continue
                    feed_urls.append({"name": src.name, "feed": f, "type": src.type, "extract_links": src.extract_links})
            else:
                feed_urls.append({"name": src.name, "feed": src.url, "type": src.type, "extract_links": src.extract_links})

        await asyncio.gather(*[prepare_source(s) for s in cfg.sources])

        # De-dup
        seen, final_feeds = set(), []
        for f in feed_urls:
            if f["feed"] not in seen:
                seen.add(f["feed"]); final_feeds.append(f)

        # 2) Parse
        sem = asyncio.Semaphore(cfg.crawl.concurrency)

        async def process_feed(entry: Dict[str, str]) -> int:
            url, name = entry["feed"], entry["name"]
            source_type = entry.get("type")  # 'youtube', 'podcast', or None
            extract_links = entry.get("extract_links", False)  # Newsletter mode
            inserts = 0
            async with sem:
                # Skip robots.txt check for YouTube/Podcast RSS feeds (public feeds meant to be consumed)
                if source_type not in ("youtube", "podcast"):
                    if not await robots.allowed(session, url): return 0
                raw = await fetcher.get(session, url)
                if not raw: return 0
                text = raw.decode("utf-8", errors="ignore")
                parsed = feedparser.parse(text)

                if parsed.entries:
                    for e in parsed.entries[:40]:
                        published_ts = normalize_ts(e)
                        if not published_ts or not within_window(published_ts, week_start_ts, week_end_ts):
                            continue
                        link = e.get("link") or e.get("id") or url
                        title = (e.get("title") or "").strip() or link
                        summary = BeautifulSoup((e.get("summary") or ""), "lxml").get_text(" ", strip=True)

                        # For YouTube/Podcast feeds, use description as content directly
                        # No need to fetch the full page content
                        content_text = ""
                        if source_type in ("youtube", "podcast"):
                            # Use summary/description as main content for media sources
                            content_text = summary
                            logger.info(f"Processing {source_type} feed item", title=title[:50], url=link, desc_len=len(summary))
                        else:
                            # Regular article: fetch full content
                            if link and await robots.allowed(session, link):
                                art_raw = await fetcher.get(session, link)
                                if art_raw:
                                    art_txt = art_raw.decode("utf-8", errors="ignore")
                                    content_text = extract_main_content(art_txt, link)

                        # NEWSLETTER MODE: Extract individual article URLs and crawl them
                        if extract_links and content_text:
                            extracted_urls = extract_newsletter_urls(content_text)
                            if extracted_urls:
                                logger.info(f"Newsletter detected, extracting {len(extracted_urls)} article URLs",
                                           source=name, newsletter_title=title[:50])

                                for ext_url in extracted_urls[:15]:  # Limit to 15 articles per newsletter
                                    try:
                                        if not await robots.allowed(session, ext_url):
                                            continue
                                        ext_raw = await fetcher.get(session, ext_url)
                                        if not ext_raw:
                                            continue
                                        ext_html = ext_raw.decode("utf-8", errors="ignore")
                                        ext_content = extract_main_content(ext_html, ext_url)

                                        if len(ext_content) < 200:  # Skip too short content
                                            continue

                                        # Extract title from the page
                                        ext_soup = BeautifulSoup(ext_html, "lxml")
                                        ext_title_tag = ext_soup.find("title")
                                        ext_title = ext_title_tag.get_text(strip=True) if ext_title_tag else ext_url
                                        # Clean title (remove site name suffix)
                                        ext_title = ext_title.split(" | ")[0].split(" - ")[0].strip()

                                        ext_summary = ext_content[:300]

                                        # Apply editorial filter
                                        if not is_editorial_article(ext_url, cfg.model_dump(), text=ext_content):
                                            continue

                                        ext_cat = classify(ext_title, ext_summary, cfg.categories)
                                        if not ext_cat:
                                            continue

                                        ext_content_type = detect_content_type(ext_title, ext_summary, ext_content, cfg.model_dump(), source_name=name)

                                        from content_classifier import (
                                            calculate_technical_level,
                                            calculate_marketing_score,
                                            should_exclude_article
                                        )
                                        ext_tech_level = calculate_technical_level(ext_title, ext_summary, ext_content)
                                        ext_marketing_score = calculate_marketing_score(ext_title, ext_summary, ext_content)
                                        ext_excluded, ext_reason = should_exclude_article(ext_title, ext_summary, ext_content, min_quality_score=50)

                                        ext_item = {
                                            "id": hash_id(ext_url, ext_title),
                                            "url": ext_url,
                                            "title": ext_title,
                                            "summary": ext_summary,
                                            "content": ext_content[:10000],
                                            "published_ts": published_ts,  # Use newsletter's publish date
                                            "source_name": name,
                                            "category_key": ext_cat,
                                            "created_ts": now_ts,
                                            "content_type": ext_content_type,
                                            "source_type": "article",
                                            "tech_level": ext_tech_level,
                                            "marketing_score": ext_marketing_score,
                                            "is_excluded": 1 if ext_excluded else 0,
                                            "exclusion_reason": ext_reason if ext_excluded else None
                                        }
                                        upsert_item(cfg.storage.sqlite_path, ext_item)
                                        inserts += 1
                                        logger.info(f"Extracted article from newsletter", title=ext_title[:50], url=ext_url[:60])

                                        # Découvrir et ajouter la source si nouvelle
                                        try:
                                            await discover_and_add_source(
                                                session, ext_url,
                                                config_path="config.yaml",
                                                discovered_by=name  # Nom de la newsletter
                                            )
                                        except Exception as disc_err:
                                            pass  # Silently ignore discovery errors

                                    except Exception as ext_err:
                                        logger.warning(f"Failed to extract article from newsletter", url=ext_url[:60], error=str(ext_err))
                                        continue

                                continue  # Skip inserting the newsletter itself

                        text_for_filter = (content_text or summary or "")
                        # Skip editorial filters for YouTube/Podcast sources
                        if source_type not in ("youtube", "podcast"):
                            if not is_editorial_article(link, cfg.model_dump(), text=text_for_filter):
                                continue

                        cat_key = classify(title, (summary or content_text[:300]), cfg.categories)
                        if not cat_key: continue

                        # Détection du type de contenu (technical vs rex)
                        content_type = detect_content_type(title, summary, content_text, cfg.model_dump(), source_name=name)

                        # NOUVEAUTÉ Phase 1 : Calcul du niveau technique et score marketing
                        from content_classifier import (
                            calculate_technical_level,
                            calculate_marketing_score,
                            should_exclude_article
                        )

                        tech_level = calculate_technical_level(title, summary, content_text)
                        marketing_score = calculate_marketing_score(title, summary, content_text)
                        is_excluded_bool, exclusion_reason = should_exclude_article(title, summary, content_text, min_quality_score=50)

                        item = {
                            "id": hash_id(link, title),
                            "url": link, "title": title,
                            "summary": summary or content_text[:300],
                            "content": content_text[:10000],
                            "published_ts": published_ts,
                            "source_name": name,
                            "category_key": cat_key,
                            "created_ts": now_ts,
                            "content_type": content_type,
                            "source_type": source_type or "article",
                            "tech_level": tech_level,
                            "marketing_score": marketing_score,
                            "is_excluded": 1 if is_excluded_bool else 0,
                            "exclusion_reason": exclusion_reason if is_excluded_bool else None
                        }
                        upsert_item(cfg.storage.sqlite_path, item); inserts += 1
                else:
                    # fallback: scrapper liens de la page
                    soup = BeautifulSoup(text, "lxml")
                    links: List[tuple[str, str]] = []
                    for a in soup.select("a[href]"):
                        href = urljoin(url, a["href"]); t = (a.get_text() or "").strip()
                        if len(t) > 6 and href.startswith("http"): links.append((href, t))
                    links = links[:20]

                    def guess_published_ts(html_txt: str) -> Optional[int]:
                        s = BeautifulSoup(html_txt, "lxml")
                        candidates = [
                            ('meta[property="article:published_time"]', "content"),
                            ('meta[name="article:published_time"]', "content"),
                            ('meta[name="publish-date"]', "content"),
                            ('meta[name="pubdate"]', "content"),
                            ('meta[name="date"]', "content"),
                            ('time[datetime]', "datetime"),
                        ]
                        for sel, attr in candidates:
                            el = s.select_one(sel)
                            if el and el.has_attr(attr):
                                try:
                                    dt = datetime.fromisoformat(el[attr].replace("Z", "+00:00"))
                                    return int(dt.astimezone(timezone.utc).timestamp())
                                except Exception: pass
                        time_el = s.find("time")
                        if time_el and time_el.get("datetime"):
                            try:
                                dt = datetime.fromisoformat(time_el["datetime"].replace("Z", "+00:00"))
                                return int(dt.astimezone(timezone.utc).timestamp())
                            except Exception: pass
                        return None

                    for href, t in links:
                        if not await robots.allowed(session, href): continue
                        art_raw = await fetcher.get(session, href)
                        if not art_raw: continue
                        art_txt = art_raw.decode("utf-8", errors="ignore")
                        published_ts = guess_published_ts(art_txt)
                        if not published_ts or not within_window(published_ts, week_start_ts, week_end_ts):
                            continue
                        text_content = extract_main_content(art_txt, href)
                        if not is_editorial_article(href, cfg.model_dump(), text=text_content):
                            continue
                        cat_key = classify(t, text_content[:300], cfg.categories)
                        if not cat_key: continue

                        # Détection du type de contenu (technical vs rex)
                        content_type = detect_content_type(t, text_content[:300], text_content, cfg.model_dump(), source_name=name)

                        # NOUVEAUTÉ Phase 1 : Calcul du niveau technique et score marketing
                        tech_level = calculate_technical_level(t, text_content[:300], text_content)
                        marketing_score = calculate_marketing_score(t, text_content[:300], text_content)
                        is_excluded_bool, exclusion_reason = should_exclude_article(t, text_content[:300], text_content, min_quality_score=50)

                        item = {
                            "id": hash_id(href, t),
                            "url": href, "title": t,
                            "summary": text_content[:300],
                            "content": text_content[:10000],
                            "published_ts": published_ts,
                            "source_name": name,
                            "category_key": cat_key,
                            "created_ts": now_ts,
                            "content_type": content_type,
                            "source_type": source_type or "article",  # Fallback scraper uses source_type too
                            "tech_level": tech_level,
                            "marketing_score": marketing_score,
                            "is_excluded": 1 if is_excluded_bool else 0,
                            "exclusion_reason": exclusion_reason if is_excluded_bool else None
                        }
                        upsert_item(cfg.storage.sqlite_path, item); inserts += 1
            return inserts

        total_new = 0
        for added in await tqdm.gather(*[process_feed(f) for f in final_feeds]):
            total_new += (added or 0)

        # 3) Export semaine -> export/<YYYYwWW>/
        groups = query_latest_by_cat(cfg.storage.sqlite_path, cfg.export.max_items_per_cat,
                                     min_ts=week_start_ts, max_ts=week_end_ts)

        header = f"Veille Tech — Semaine {week_label} ({week_start_str} → {week_end_str})"

        out_root = Path(cfg.export.out_dir)
        week_dir = out_root / week_label
        week_dir.mkdir(parents=True, exist_ok=True)

        # JSON / MD dans le dossier de la semaine
        json_path = week_dir / "digest.json"
        json_path.write_text(json.dumps(groups, indent=2, ensure_ascii=False), encoding="utf-8")

        if cfg.export.make_markdown_digest:
            md = to_markdown(groups, categories_by_key, header=header)
            md_path = week_dir / "digest.md"
            md_path.write_text(md, encoding="utf-8")

        # lien symbolique "latest" → cette semaine (best effort)
        latest = out_root / "latest"
        try:
            if latest.is_symlink() or latest.exists():
                latest.unlink()
            latest.symlink_to(week_dir, target_is_directory=True)
        except Exception:
            pass

        # 4) Slack (optionnel)
        webhook_env = cfg.notify.slack_webhook_env
        if webhook_env:
            wh = os.environ.get(webhook_env)
            if wh:
                lines = [f"*Veille Tech* — ajouts semaine {week_label} ({week_start_str}→{week_end_str}):"]
                for k, items in groups.items():
                    if items:
                        title = categories_by_key.get(k).title if k in categories_by_key else k
                        lines.append(f"• {title}: {len(items)} items")
                await notify_slack(wh, "\n".join(lines), session)

        # Logging final et métriques
        total_articles = sum(len(items) for items in groups.values())
        logger.info("Pipeline completed successfully",
                   feeds_processed=len(final_feeds),
                   new_items=total_new,
                   total_articles=total_articles,
                   week=week_label)

        # Sauvegarder les métriques
        metrics.increment("articles_crawled", total_new)
        metrics_path = week_dir / "metrics.json"
        metrics.save(str(metrics_path))

        print(f"Done. New items inserted: {total_new}")
        print(f"Exported: {json_path}")
        if cfg.export.make_markdown_digest:
            print(f"Exported: {md_path}")
        print(f"Metrics: {metrics_path}")

# -----------------------
# CLI
# -----------------------

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Veille techno crawler (hebdomadaire Europe/Paris)")
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--week-offset", type=int, default=None,
                        help="Décalage de semaine: 0=cette semaine, -1=semaine dernière")
    args = parser.parse_args()
    if args.week_offset is not None:
        os.environ["WEEK_OFFSET"] = str(args.week_offset)
    asyncio.run(run(args.config))