#!/usr/bin/env python3
"""
daily_feed.py - Génère les feeds continus (articles + vidéos/podcasts)

Exporte dans export/feed.json:
- articles: les 10 meilleurs articles récents
- videos: les 5 meilleures vidéos/podcasts récents

Le ranking combine:
- final_score (algo) : score de pertinence calculé par analyze_relevance.py
- community_votes : upvotes - downvotes depuis Firebase

Usage:
    python daily_feed.py
    python daily_feed.py --days 7  # Articles des 7 derniers jours
"""

import argparse
import json
import os
import re
import sqlite3
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Optional

import yaml
from dotenv import load_dotenv

# Charger les variables d'environnement (.env)
load_dotenv()

# LLM pour renommer les newsletters (optional)
try:
    from llm_provider import get_provider
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False


# Patterns pour détecter les newsletters
NEWSLETTER_PATTERNS = [
    r"weekly\s*#?\d*",
    r"newsletter\s*#?\d*",
    r"digest\s*#?\d*",
    r"roundup\s*#?\d*",
    r"edition\s*#?\d*",
]

def is_newsletter(title: str) -> bool:
    """Détecte si un article est une newsletter basé sur le titre."""
    title_lower = title.lower()
    return any(re.search(pattern, title_lower) for pattern in NEWSLETTER_PATTERNS)


def generate_newsletter_title(original_title: str, summary: str, config: dict, content: str = "") -> str:
    """
    Génère un titre plus descriptif pour une newsletter.

    Utilise le LLM si disponible, sinon extrait du résumé ou contenu.
    """
    # Utiliser le contenu si le résumé est trop court
    text_for_title = summary if len(summary or "") >= 100 else (content or summary or "")

    if not text_for_title or len(text_for_title) < 50:
        return original_title

    # Extraire le numéro de la newsletter pour le garder
    number_match = re.search(r"#(\d+)", original_title)
    number_suffix = f" (#{number_match.group(1)})" if number_match else ""

    # Essayer avec le LLM si disponible
    if LLM_AVAILABLE and os.getenv("GROQ_API_KEY"):
        try:
            provider = get_provider(config.get("llm", {}))

            # Skip les premiers 500 caractères qui sont souvent des pubs/promos
            content_for_llm = text_for_title[500:2000] if len(text_for_title) > 500 else text_for_title[:1500]

            # Nettoyer les URLs du contenu pour éviter que le LLM les extraie
            content_for_llm = re.sub(r'https?://\S+', '', content_for_llm)
            content_for_llm = re.sub(r'\s+', ' ', content_for_llm).strip()

            prompt = f"""Cette newsletter agrège plusieurs articles tech. Génère un titre accrocheur basé sur le sujet technique le plus intéressant.

RÈGLES STRICTES:
1. Le titre DOIT mentionner une TECHNOLOGIE concrète (Iceberg, Kafka, DuckDB, Spark, etc.) ou un CONCEPT technique (data lakehouse, streaming, ML pipelines, etc.)
2. INTERDIT: "Reserve", "Join", "Register", "Webinar", "Download", "Free", dates, URLs
3. Format: "[Sujet technique principal]" (30-50 caractères)
4. Exemples de BONS titres: "Iceberg REST Catalog Deep Dive", "OpenAI's Data Agent Architecture", "DuckDB vs Polars Performance"

Contenu de la newsletter:
{content_for_llm[:1200]}

Réponds avec UNIQUEMENT le titre (sans guillemets). Si aucun sujet technique clair, réponds: SKIP"""

            response = provider.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=50,
            )

            new_title = response.strip().strip('"\'')

            # Si le LLM dit SKIP ou retourne un titre trop court, utiliser le fallback
            if new_title and new_title.upper() != "SKIP" and len(new_title) > 15:
                return new_title + number_suffix

        except Exception as e:
            print(f"[warning] LLM title generation failed: {e}")

    # Fallback: extraire du texte (nettoyer les URLs d'abord)
    clean_text = re.sub(r'https?://\S+', '', text_for_title)
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()

    # Prendre la première phrase significative
    sentences = re.split(r'[.!?]', clean_text)
    for sentence in sentences:
        sentence = sentence.strip()
        # Éviter les CTAs et phrases trop courtes/longues
        if len(sentence) > 25 and len(sentence) < 70:
            lower = sentence.lower()
            if not any(word in lower for word in ['reserve', 'join', 'register', 'webinar', 'download']):
                return sentence + number_suffix

    # Dernier recours: garder le titre original
    return original_title


def rename_newsletters_in_feed(
    items: list[dict[str, Any]],
    config: dict,
    db_path: str = None
) -> list[dict[str, Any]]:
    """
    Renomme les newsletters dans une liste d'items.

    Applique le renommage à tous les items qui sont des newsletters,
    y compris ceux venant du rolling buffer.

    Si db_path est fourni, charge le content depuis la DB pour les newsletters
    avec un résumé trop court.
    """
    # Pré-charger les contenus des newsletters depuis la DB si nécessaire
    content_cache: dict[str, str] = {}
    if db_path:
        newsletter_urls = [
            item.get("url", "") for item in items
            if is_newsletter(item.get("title", "")) and len(item.get("summary", "")) < 100
        ]
        if newsletter_urls:
            try:
                conn = get_db_connection(db_path)
                placeholders = ",".join("?" * len(newsletter_urls))
                rows = conn.execute(
                    f"SELECT url, content FROM items WHERE url IN ({placeholders})",
                    newsletter_urls
                ).fetchall()
                conn.close()
                content_cache = {row["url"]: row["content"] or "" for row in rows}
            except Exception as e:
                print(f"[warning] Could not load newsletter content: {e}")

    renamed_count = 0
    for item in items:
        title = item.get("title", "")
        if is_newsletter(title):
            # Garder le titre original si pas déjà stocké
            if "original_title" not in item:
                item["original_title"] = title

            summary = item.get("summary", "")
            content = content_cache.get(item.get("url", ""), "")
            new_title = generate_newsletter_title(title, summary, config, content)

            if new_title != title:
                item["title"] = new_title
                renamed_count += 1

    if renamed_count > 0:
        print(f"[info] {renamed_count} newsletter(s) renommée(s)")

    return items

# Firebase (optional - graceful fallback if not available)
try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False


def load_config(config_path: str = "config.yaml") -> dict:
    """Charge la configuration."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_db_connection(db_path: str) -> sqlite3.Connection:
    """Crée une connexion à la base de données."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_firebase() -> Optional[Any]:
    """Initialize Firebase Admin SDK."""
    if not FIREBASE_AVAILABLE:
        print("[warning] Firebase not available, votes won't be included")
        return None

    # Already initialized?
    try:
        return firestore.client()
    except ValueError:
        pass

    # Try to initialize
    try:
        cred_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY")
        if cred_json:
            # Check if it's a path or JSON content
            if cred_json.startswith("{"):
                import json as json_module
                cred_dict = json_module.loads(cred_json)
                cred = credentials.Certificate(cred_dict)
            elif Path(cred_json).exists():
                cred = credentials.Certificate(cred_json)
            else:
                print("[warning] Firebase credentials not found")
                return None
        else:
            print("[info] No Firebase credentials, votes won't be included")
            return None

        firebase_admin.initialize_app(cred)
        return firestore.client()
    except Exception as e:
        print(f"[warning] Firebase init failed: {e}")
        return None


def fetch_votes_from_firebase(db: Any) -> dict[str, dict[str, int]]:
    """
    Récupère tous les votes depuis Firebase.

    Returns:
        Dict[article_id] = {"upvotes": X, "downvotes": Y}
    """
    if db is None:
        return {}

    try:
        votes_ref = db.collection('votes')
        votes = votes_ref.stream()

        article_votes: dict[str, dict[str, int]] = defaultdict(lambda: {"upvotes": 0, "downvotes": 0})

        for vote in votes:
            data = vote.to_dict()
            article_id = data.get('article_id', '')
            vote_value = data.get('vote_value', 0)

            if vote_value > 0:
                article_votes[article_id]["upvotes"] += 1
            elif vote_value < 0:
                article_votes[article_id]["downvotes"] += 1

        print(f"[info] Loaded votes for {len(article_votes)} articles from Firebase")
        return dict(article_votes)

    except Exception as e:
        print(f"[warning] Failed to fetch votes: {e}")
        return {}


def compute_combined_score(
    algo_score: float,
    upvotes: int,
    downvotes: int,
    published_ts: int,
    max_boost: float = 20.0,
    confidence_prior: int = 5,
    gravity: float = 1.5
) -> float:
    """
    Calcule un score combiné algo + votes + time decay (style HN).

    Formule:
    1. Calcule un vote boost Bayésien
    2. Combine avec algo_score
    3. Applique time decay: score / (age_hours + 2)^gravity

    Le time decay fait descendre les vieux articles même s'ils ont beaucoup de votes,
    permettant aux nouveaux articles d'avoir une chance.

    Exemples avec gravity=1.5:
    - Article 60pts, 0h → 60 / 2^1.5 = 21.2
    - Article 60pts, 24h → 60 / 26^1.5 = 0.5
    - Article 80pts, 6h → 80 / 8^1.5 = 3.5
    - Article 50pts, 1h → 50 / 3^1.5 = 9.6

    Args:
        algo_score: Score de pertinence (0-100)
        upvotes: Nombre d'upvotes
        downvotes: Nombre de downvotes
        published_ts: Timestamp de publication (Unix)
        max_boost: Boost maximum des votes (default ±20 points)
        confidence_prior: Prior Bayésien (default 5)
        gravity: Facteur de décroissance temporelle (default 1.5, HN utilise 1.8)

    Returns:
        Score combiné avec time decay
    """
    import math

    # 1. Calcul du vote boost (Bayésien)
    total_votes = upvotes + downvotes
    vote_boost = 0.0

    if total_votes > 0:
        bayesian_ratio = (confidence_prior * 0.5 + upvotes) / (confidence_prior + total_votes)
        normalized_boost = (bayesian_ratio - 0.5) * 2
        confidence_factor = math.sqrt(total_votes)
        vote_boost = normalized_boost * confidence_factor * (max_boost / 3)
        vote_boost = max(-max_boost, min(max_boost, vote_boost))

    # 2. Score de base (algo + votes)
    base_score = algo_score + vote_boost

    # 3. Time decay (style HN)
    now_ts = datetime.now(timezone.utc).timestamp()
    age_hours = max(0, (now_ts - published_ts) / 3600)

    # Formule HN: score / (age + 2)^gravity
    time_decay_factor = math.pow(age_hours + 2, gravity)
    final_score = base_score / time_decay_factor

    # Normalise pour avoir des scores plus lisibles (multiplie par 10)
    return final_score * 10


def fetch_top_articles(
    conn: sqlite3.Connection,
    votes: dict[str, dict[str, int]],
    limit: int = 10,
    days: int | None = 14,
    min_score: int = 40
) -> list[dict[str, Any]]:
    """
    Récupère les meilleurs articles (hors vidéos/podcasts).
    Trie par score combiné (algo + votes).

    Args:
        days: Nombre de jours à considérer. None = pas de limite de date.
    """
    # Fetch more articles than needed to allow re-ranking
    fetch_limit = limit * 3

    if days is not None:
        cutoff_ts = int((datetime.now(timezone.utc) - timedelta(days=days)).timestamp())
        query = """
            SELECT
                id, url, title, summary, source_name, published_ts,
                category_key, final_score, content_type, tech_level,
                marketing_score, source_type
            FROM items
            WHERE published_ts >= ?
              AND final_score >= ?
              AND (source_type IS NULL OR source_type = 'article')
              AND is_excluded = 0
            ORDER BY final_score DESC, published_ts DESC
            LIMIT ?
        """
        cursor = conn.execute(query, (cutoff_ts, min_score, fetch_limit))
    else:
        # No date restriction - fetch all time
        query = """
            SELECT
                id, url, title, summary, source_name, published_ts,
                category_key, final_score, content_type, tech_level,
                marketing_score, source_type
            FROM items
            WHERE final_score >= ?
              AND (source_type IS NULL OR source_type = 'article')
              AND is_excluded = 0
            ORDER BY final_score DESC, published_ts DESC
            LIMIT ?
        """
        cursor = conn.execute(query, (min_score, fetch_limit))
    rows = cursor.fetchall()

    # Add votes and compute combined score
    articles = []
    for row in rows:
        item = dict(row)
        article_id = item["id"]
        article_votes = votes.get(article_id, {"upvotes": 0, "downvotes": 0})

        item["upvotes"] = article_votes["upvotes"]
        item["downvotes"] = article_votes["downvotes"]
        item["combined_score"] = compute_combined_score(
            item["final_score"],
            article_votes["upvotes"],
            article_votes["downvotes"],
            item["published_ts"]
        )
        articles.append(item)

    # Sort by combined score
    articles.sort(key=lambda x: x["combined_score"], reverse=True)

    return articles[:limit]


def fetch_top_videos(
    conn: sqlite3.Connection,
    votes: dict[str, dict[str, int]],
    limit: int = 5,
    days: int | None = 14,
    min_score: int = 30
) -> list[dict[str, Any]]:
    """
    Récupère les meilleures vidéos et podcasts.
    Trie par score combiné (algo + votes).

    Args:
        days: Nombre de jours à considérer. None = pas de limite de date.
    """
    fetch_limit = limit * 3

    if days is not None:
        cutoff_ts = int((datetime.now(timezone.utc) - timedelta(days=days)).timestamp())
        query = """
            SELECT
                id, url, title, summary, source_name, published_ts,
                category_key, final_score, content_type, tech_level,
                marketing_score, source_type
            FROM items
            WHERE published_ts >= ?
              AND final_score >= ?
              AND source_type IN ('youtube', 'podcast')
              AND is_excluded = 0
            ORDER BY final_score DESC, published_ts DESC
            LIMIT ?
        """
        cursor = conn.execute(query, (cutoff_ts, min_score, fetch_limit))
    else:
        # No date restriction - fetch all time
        query = """
            SELECT
                id, url, title, summary, source_name, published_ts,
                category_key, final_score, content_type, tech_level,
                marketing_score, source_type
            FROM items
            WHERE final_score >= ?
              AND source_type IN ('youtube', 'podcast')
              AND is_excluded = 0
            ORDER BY final_score DESC, published_ts DESC
            LIMIT ?
        """
        cursor = conn.execute(query, (min_score, fetch_limit))
    rows = cursor.fetchall()

    # Add votes and compute combined score
    videos = []
    for row in rows:
        item = dict(row)
        article_id = item["id"]
        article_votes = votes.get(article_id, {"upvotes": 0, "downvotes": 0})

        item["upvotes"] = article_votes["upvotes"]
        item["downvotes"] = article_votes["downvotes"]
        item["combined_score"] = compute_combined_score(
            item["final_score"],
            article_votes["upvotes"],
            article_votes["downvotes"],
            item["published_ts"]
        )
        videos.append(item)

    # Sort by combined score
    videos.sort(key=lambda x: x["combined_score"], reverse=True)

    return videos[:limit]


def format_item(item: dict[str, Any], config: dict = None) -> dict[str, Any]:
    """Formate un item pour l'export JSON."""
    title = item["title"]
    summary = item["summary"] or ""

    # Truncate long summaries (e.g. podcast transcripts) to 300 chars
    if len(summary) > 300:
        summary = summary[:300].rsplit(' ', 1)[0] + '...'

    # Renommer les newsletters avec un titre plus descriptif
    if config and is_newsletter(title):
        title = generate_newsletter_title(title, summary, config)

    return {
        "id": item["id"],
        "url": item["url"],
        "title": title,
        "original_title": item["title"],  # Garder le titre original
        "summary": summary,
        "source_name": item["source_name"],
        "published_ts": item["published_ts"],
        "category_key": item["category_key"],
        "score": round(item["combined_score"], 1),
        "algo_score": round(item["final_score"], 1),
        "upvotes": item["upvotes"],
        "downvotes": item["downvotes"],
        "content_type": item["content_type"] or "technical",
        "tech_level": item["tech_level"] or "intermediate",
        "source_type": item["source_type"] or "article",
    }


def generate_feed(
    config_path: str = "config.yaml",
    days: int = 14,
    articles_limit: int = 10,
    videos_limit: int = 5,
    output_dir: str = "export",
    use_rolling_buffer: bool = True
) -> dict[str, Any]:
    """
    Génère le feed complet avec rolling buffer.

    Le rolling buffer garantit qu'on a toujours `articles_limit` articles
    et `videos_limit` vidéos. Les anciens items ne sont remplacés que
    si de meilleurs arrivent.

    Args:
        config_path: Chemin vers config.yaml
        days: Jours à considérer pour les nouveaux articles
        articles_limit: Nombre d'articles cible (constant)
        videos_limit: Nombre de vidéos cible (constant)
        output_dir: Dossier contenant le feed existant
        use_rolling_buffer: Si True, fusionne avec le feed existant

    Returns:
        Dict avec 'articles' et 'videos'
    """
    config = load_config(config_path)
    db_path = config["storage"]["sqlite_path"]

    # Initialize Firebase and fetch votes
    firebase_db = init_firebase()
    votes = fetch_votes_from_firebase(firebase_db)

    conn = get_db_connection(db_path)

    try:
        # Fetch articles from DB (last N days first)
        new_articles = fetch_top_articles(
            conn, votes,
            limit=articles_limit * 2,
            days=days
        )
        new_videos = fetch_top_videos(
            conn, votes,
            limit=videos_limit * 2,
            days=days
        )

        # If not enough items in recent window, fetch from all time
        # Time decay will still rank newer items higher
        if len(new_articles) < articles_limit:
            all_articles = fetch_top_articles(
                conn, votes,
                limit=articles_limit * 2,
                days=None  # No date restriction
            )
            # Merge: keep recent ones + add older ones to fill
            seen_urls = {a["url"] for a in new_articles}
            for a in all_articles:
                if a["url"] not in seen_urls:
                    new_articles.append(a)
                    seen_urls.add(a["url"])

        if len(new_videos) < videos_limit:
            all_videos = fetch_top_videos(
                conn, votes,
                limit=videos_limit * 2,
                days=None  # No date restriction
            )
            seen_urls = {v["url"] for v in new_videos}
            for v in all_videos:
                if v["url"] not in seen_urls:
                    new_videos.append(v)
                    seen_urls.add(v["url"])

        # Format for export (with newsletter title rewriting)
        formatted_articles = [format_item(a, config) for a in new_articles]
        formatted_videos = [format_item(v, config) for v in new_videos]

        # Rolling buffer: merge with existing feed
        if use_rolling_buffer:
            existing_feed = load_existing_feed(output_dir)
            if existing_feed:
                existing_articles = existing_feed.get("articles", [])
                existing_videos = existing_feed.get("videos", [])

                formatted_articles = merge_feeds(
                    formatted_articles,
                    existing_articles,
                    articles_limit,
                    "articles"
                )
                formatted_videos = merge_feeds(
                    formatted_videos,
                    existing_videos,
                    videos_limit,
                    "videos"
                )
            else:
                # No existing feed - apply time decay and take top N
                formatted_articles = merge_feeds(
                    formatted_articles,
                    [],  # No existing items
                    articles_limit,
                    "articles"
                )
                formatted_videos = merge_feeds(
                    formatted_videos,
                    [],
                    videos_limit,
                    "videos"
                )
        else:
            # No rolling buffer - still apply time decay for ranking
            formatted_articles = merge_feeds(formatted_articles, [], articles_limit, "articles")
            formatted_videos = merge_feeds(formatted_videos, [], videos_limit, "videos")

        # Renommer les newsletters (Data Engineering Weekly → titre descriptif)
        formatted_articles = rename_newsletters_in_feed(formatted_articles, config, db_path)

        feed = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "config": {
                "articles_limit": articles_limit,
                "videos_limit": videos_limit,
                "days_lookback": days,
                "rolling_buffer": use_rolling_buffer,
            },
            "articles": formatted_articles,
            "videos": formatted_videos,
        }

        return feed

    finally:
        conn.close()


def load_existing_feed(output_dir: str = "export") -> dict[str, Any] | None:
    """Charge le feed existant s'il existe."""
    feed_path = Path(output_dir) / "feed.json"
    if feed_path.exists():
        try:
            with open(feed_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"[warning] Could not load existing feed: {e}")
    return None


def recalculate_time_decay_score(item: dict[str, Any], gravity: float = 1.5) -> float:
    """
    Recalcule le score avec time decay style Hacker News (en HEURES).

    Utilise algo_score (score de pertinence brut) + votes + âge en HEURES.
    Formule HN: score / (age_hours + 2)^gravity

    Avec gravity=1.5:
    - Article frais (0h): score / 2.83 = 35%
    - Article 6h: score / 22.6 = 4.4%
    - Article 12h: score / 52.4 = 1.9%
    - Article 24h: score / 133 = 0.75%
    - Article 48h: score / 354 = 0.28%

    Turnover très rapide, nouveaux articles montent en quelques heures.
    """
    import math

    # Score de base (algo_score = score sans time decay)
    algo_score = item.get("algo_score", item.get("score", 50))
    upvotes = item.get("upvotes", 0)
    downvotes = item.get("downvotes", 0)
    published_ts = item.get("published_ts", 0)

    # Vote boost - les votes ont un impact significatif sur le ranking
    # max_boost=40 permet aux votes de doubler ou diviser par 2 un score moyen (50)
    # confidence_prior=3 = les premiers votes comptent rapidement
    total_votes = upvotes + downvotes
    vote_boost = 0.0
    max_boost = 40.0  # ±40 points (était 20)
    confidence_prior = 3  # Moins de votes nécessaires pour impact (était 5)

    if total_votes > 0:
        # Bayesian average: évite qu'un seul vote ait trop d'impact
        bayesian_ratio = (confidence_prior * 0.5 + upvotes) / (confidence_prior + total_votes)
        # Normalise entre -1 et +1
        normalized_boost = (bayesian_ratio - 0.5) * 2
        # Plus de votes = plus de confiance (sqrt pour ne pas exploser)
        confidence_factor = math.sqrt(total_votes)
        vote_boost = normalized_boost * confidence_factor * (max_boost / 2.5)
        vote_boost = max(-max_boost, min(max_boost, vote_boost))

    # Exemples d'impact:
    # - 3 upvotes, 0 downvotes → +17 points
    # - 5 upvotes, 0 downvotes → +24 points
    # - 10 upvotes, 2 downvotes → +26 points
    # - 0 upvotes, 3 downvotes → -17 points

    base_score = algo_score + vote_boost

    # Time decay en HEURES (comme HN)
    now_ts = datetime.now(timezone.utc).timestamp()
    age_hours = max(0, (now_ts - published_ts) / 3600)  # 3600 = secondes par heure

    # Formule HN: score / (age_hours + 2)^gravity
    time_decay_factor = math.pow(age_hours + 2, gravity)
    final_score = base_score / time_decay_factor

    return final_score


def merge_feeds(
    new_items: list[dict[str, Any]],
    existing_items: list[dict[str, Any]],
    target_count: int,
    item_type: str = "articles",
    gravity: float = 1.5
) -> list[dict[str, Any]]:
    """
    Fusionne les nouveaux items avec les existants (rolling buffer).

    Stratégie:
    1. Combine nouveaux + existants
    2. Déduplique par URL (garde le plus récent)
    3. Recalcule le time decay pour TOUS les items (HN-style)
    4. Trie par score recalculé et garde les top N

    Le time decay fait descendre naturellement les vieux articles,
    permettant aux nouveaux d'avoir leur chance même avec un score plus bas.
    """
    # URLs des nouveaux items pour tracking
    new_urls = {item.get("url", "") for item in new_items}
    existing_urls = {item.get("url", "") for item in existing_items}

    # Index par URL pour déduplication (nouveaux ont priorité)
    items_by_url: dict[str, dict[str, Any]] = {}

    # D'abord les existants
    for item in existing_items:
        url = item.get("url", "")
        if url:
            items_by_url[url] = item

    # Puis les nouveaux (écrasent les existants)
    for item in new_items:
        url = item.get("url", "")
        if url:
            items_by_url[url] = item

    # Recalculer le time decay score pour TOUS les items
    all_items = list(items_by_url.values())
    for item in all_items:
        # Truncate long summaries (legacy items may have full transcripts)
        summary = item.get("summary", "")
        if len(summary) > 300:
            item["summary"] = summary[:300].rsplit(' ', 1)[0] + '...'
        item["_ranking_score"] = recalculate_time_decay_score(item, gravity)

    # Trier par score recalculé, puis par date (plus récent = mieux) pour départager
    all_items.sort(
        key=lambda x: (x["_ranking_score"], x.get("published_ts", 0)),
        reverse=True
    )

    result = all_items[:target_count]

    # Mettre à jour le score affiché (4 décimales pour différencier les petits scores)
    for item in result:
        item["score"] = round(item["_ranking_score"], 4)
        del item["_ranking_score"]

    # Compte combien d'anciens sont conservés (URL existait et pas dans les nouveaux)
    result_urls = {item.get("url", "") for item in result}
    kept_from_existing = len(result_urls & existing_urls - new_urls)
    from_new = len(result_urls & new_urls)

    print(f"[info] {item_type}: {from_new} nouveaux, {kept_from_existing} conservés, {len(result)} total")

    return result


def export_feed(feed: dict[str, Any], output_dir: str = "export") -> Path:
    """Exporte le feed dans export/feed.json."""
    output_path = Path(output_dir) / "feed.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(feed, f, ensure_ascii=False, indent=2)

    return output_path


def main():
    parser = argparse.ArgumentParser(description="Génère les feeds continus")
    parser.add_argument("--config", default="config.yaml", help="Fichier de config")
    parser.add_argument("--days", type=int, default=14, help="Jours à considérer")
    parser.add_argument("--articles", type=int, default=10, help="Nombre d'articles")
    parser.add_argument("--videos", type=int, default=5, help="Nombre de vidéos")
    parser.add_argument("--output", default="export", help="Dossier de sortie")
    parser.add_argument("--no-rolling-buffer", action="store_true",
                        help="Désactive le rolling buffer (remplace tout)")

    args = parser.parse_args()

    print(f"Génération du feed (derniers {args.days} jours)...")
    if not args.no_rolling_buffer:
        print("[info] Rolling buffer activé - les anciens articles sont conservés si meilleurs")

    feed = generate_feed(
        config_path=args.config,
        days=args.days,
        articles_limit=args.articles,
        videos_limit=args.videos,
        output_dir=args.output,
        use_rolling_buffer=not args.no_rolling_buffer
    )

    print(f"  - {len(feed['articles'])} articles")
    print(f"  - {len(feed['videos'])} vidéos/podcasts")

    # Show top articles with votes
    print("\nTop articles:")
    for i, a in enumerate(feed['articles'][:5], 1):
        votes_str = f"▲{a['upvotes']} ▼{a['downvotes']}" if a['upvotes'] or a['downvotes'] else "no votes"
        print(f"  {i}. [{a['score']:.0f}] {a['title'][:50]}... ({votes_str})")

    output_path = export_feed(feed, args.output)
    print(f"\nExporté dans {output_path}")

    return feed


if __name__ == "__main__":
    main()
