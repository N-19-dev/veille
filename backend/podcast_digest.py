#!/usr/bin/env python3
"""
podcast_digest.py - Monthly podcast preparation email

Collects the best articles from the last 4 weeks and sends a digest email
with links + an AI prompt to generate podcast content.

Usage:
    python podcast_digest.py
    python podcast_digest.py --weeks 4          # Number of weeks to look back (default: 4)
    python podcast_digest.py --top 15           # Number of top articles (default: 15)
    python podcast_digest.py --dry-run          # Print email content without sending
"""
import argparse
import json
import os
from pathlib import Path
from typing import List, Dict, Any

from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content

from logger import get_logger

logger = get_logger("podcast_digest", log_file="logs/podcast_digest.log", level="INFO")

RECIPIENT_EMAIL = "natsornet@gmail.com"
RECIPIENT_NAME = "Nathan"
FROM_EMAIL = "veille@datamag.dev"
FROM_NAME = "Veille MAG - Podcast Prep"


def find_recent_weeks(export_dir: Path, num_weeks: int) -> List[Path]:
    """Find the most recent N week directories."""
    week_dirs = sorted(
        [d for d in export_dir.iterdir() if d.is_dir() and d.name[0:4].isdigit() and "w" in d.name],
        key=lambda d: d.name,
        reverse=True,
    )
    return week_dirs[:num_weeks]


def load_articles_from_week(week_dir: Path) -> List[Dict[str, Any]]:
    """Load articles from a week's ai_selection.json, with week metadata."""
    selection_path = week_dir / "ai_selection.json"
    range_path = week_dir / "range.txt"

    if not selection_path.exists():
        logger.warning(f"No ai_selection.json in {week_dir.name}")
        return []

    with open(selection_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    date_range = ""
    if range_path.exists():
        date_range = range_path.read_text().strip()

    articles = []
    for category_key, items in data.items():
        for item in items:
            item["category_key"] = category_key
            item["week_id"] = week_dir.name
            item["date_range"] = date_range
            articles.append(item)

    return articles


def select_top_articles(all_articles: List[Dict[str, Any]], top_n: int) -> List[Dict[str, Any]]:
    """Select top N articles by score, ensuring category diversity."""
    # Sort by score descending
    sorted_articles = sorted(all_articles, key=lambda a: a.get("score", 0), reverse=True)

    selected = []
    seen_urls = set()
    category_counts: Dict[str, int] = {}
    max_per_category = max(3, top_n // 4)

    for article in sorted_articles:
        if len(selected) >= top_n:
            break

        url = article["url"]
        cat = article["category_key"]

        # Skip duplicates
        if url in seen_urls:
            continue

        # Limit per category for diversity
        if category_counts.get(cat, 0) >= max_per_category:
            continue

        selected.append(article)
        seen_urls.add(url)
        category_counts[cat] = category_counts.get(cat, 0) + 1

    return selected


CATEGORY_LABELS = {
    "warehouses_engines": "Warehouses & Query Engines",
    "etl_orchestration": "ETL & Orchestration",
    "data_modeling_governance": "Data Modeling & Governance",
    "lake_storage_formats": "Data Lakes & Storage Formats",
    "cloud_infra_observability": "Cloud, Infra & Observability",
    "python_analytics": "Python & Analytics",
    "ai_data_engineering": "AI & Data Engineering",
    "news": "News & Trends",
}


def build_email_content(articles: List[Dict[str, Any]], weeks_covered: List[str]) -> tuple[str, str]:
    """Build HTML and plain text email content."""
    date_ranges = []
    for w in weeks_covered:
        range_path = Path(__file__).parent / "export" / w / "range.txt"
        if range_path.exists():
            date_ranges.append(f"{w}: {range_path.read_text().strip()}")

    period = "\n".join(date_ranges) if date_ranges else ", ".join(weeks_covered)

    # Group articles by category
    by_category: Dict[str, List[Dict]] = {}
    for a in articles:
        cat = a["category_key"]
        by_category.setdefault(cat, []).append(a)

    # --- Plain text version ---
    text_lines = [
        f"PODCAST PREP - Top {len(articles)} articles du mois",
        f"Periode: {period}",
        "=" * 60,
        "",
    ]

    for cat_key, cat_articles in sorted(by_category.items()):
        cat_label = CATEGORY_LABELS.get(cat_key, cat_key.replace("_", " ").title())
        text_lines.append(f"\n## {cat_label}")
        text_lines.append("-" * 40)
        for a in cat_articles:
            score = a.get("score", 0)
            text_lines.append(f"  [{score:.0f}] {a['title']}")
            text_lines.append(f"       {a['url']}")
            text_lines.append(f"       Source: {a['source_name']} | {a.get('date_range', '')}")
            if a.get("summary"):
                summary = a["summary"][:200].replace("\n", " ")
                text_lines.append(f"       > {summary}")
            text_lines.append("")

    # --- AI Prompt ---
    article_list_for_prompt = ""
    for i, a in enumerate(articles, 1):
        cat_label = CATEGORY_LABELS.get(a["category_key"], a["category_key"])
        article_list_for_prompt += f"{i}. [{cat_label}] {a['title']} — {a['source_name']} (score: {a.get('score', 0):.0f})\n"
        article_list_for_prompt += f"   URL: {a['url']}\n"
        if a.get("summary"):
            article_list_for_prompt += f"   Resume: {a['summary'][:200].replace(chr(10), ' ')}\n"
        article_list_for_prompt += "\n"

    ai_prompt = f"""Tu es un redacteur de podcast tech specialise en data engineering. Je suis un data engineer junior qui fait un podcast mensuel de news pour son equipe (principalement des data engineers).

Voici les {len(articles)} articles les plus importants du mois ({period}) :

{article_list_for_prompt}

A partir de ces articles, genere le contenu de mon podcast en suivant ces regles :

1. **Format** : Podcast de 15-20 minutes, ton conversationnel et accessible
2. **Structure** :
   - Intro accrocheuse (30 sec) : pourquoi ce mois est interessant pour les data engineers
   - 3 a 5 sujets principaux regroupes par theme (pas un article = un sujet, regroupe les articles lies)
   - Pour chaque sujet : contexte simple, pourquoi c'est important pour nous (data engineers), ce qu'il faut retenir
   - Outro avec les 3 takeaways du mois
3. **Ton** : Je suis junior, je ne pretends pas tout savoir. Le podcast doit etre informatif et humble, pas condescendant. Utilise des analogies simples.
4. **Evite** : Le jargon non explique, les details trop techniques, les opinions trop tranchees
5. **Ajoute** : Des transitions naturelles entre les sujets, des questions rhetoriques pour engager l'auditeur
6. **Langue** : Francais

Genere :
- Le script complet du podcast (avec indications de ton entre crochets)
- Une liste de 3-5 bullet points "a retenir" pour le post LinkedIn associe"""

    text_lines.append("\n" + "=" * 60)
    text_lines.append("PROMPT IA POUR GENERER LE CONTENU DU PODCAST")
    text_lines.append("=" * 60)
    text_lines.append("(Copie-colle ce prompt dans Claude/ChatGPT)")
    text_lines.append("")
    text_lines.append(ai_prompt)

    plain_text = "\n".join(text_lines)

    # --- HTML version ---
    html_articles = ""
    for cat_key, cat_articles in sorted(by_category.items()):
        cat_label = CATEGORY_LABELS.get(cat_key, cat_key.replace("_", " ").title())
        html_articles += f'<h2 style="color:#6C63FF;margin-top:28px;">{cat_label}</h2>\n'
        for a in cat_articles:
            score = a.get("score", 0)
            summary = a.get("summary", "")[:200].replace("\n", " ")
            html_articles += f"""
            <div style="background:#1a1a2e;border-radius:8px;padding:16px;margin-bottom:12px;">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <a href="{a['url']}" style="color:#E0E0FF;font-size:16px;font-weight:bold;text-decoration:none;">{a['title']}</a>
                    <span style="background:#6C63FF;color:white;border-radius:12px;padding:2px 10px;font-size:13px;white-space:nowrap;margin-left:8px;">{score:.0f}</span>
                </div>
                <div style="color:#888;font-size:13px;margin-top:4px;">{a['source_name']} — {a.get('date_range', '')}</div>
                <div style="color:#aaa;font-size:14px;margin-top:8px;">{summary}</div>
            </div>
"""

    html = f"""<!DOCTYPE html>
<html>
<body style="background:#0f0f23;color:#E0E0FF;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;padding:24px;max-width:700px;margin:0 auto;">
    <div style="text-align:center;margin-bottom:32px;">
        <h1 style="color:#6C63FF;font-size:28px;">🎙️ Podcast Prep — Top {len(articles)} du mois</h1>
        <p style="color:#888;font-size:14px;">{period.replace(chr(10), ' | ')}</p>
    </div>

    {html_articles}

    <div style="background:#16213e;border-radius:12px;padding:24px;margin-top:32px;border:1px solid #6C63FF;">
        <h2 style="color:#6C63FF;margin-top:0;">🤖 Prompt IA pour le podcast</h2>
        <p style="color:#aaa;font-size:13px;margin-bottom:12px;">Copie-colle ce prompt dans Claude ou ChatGPT :</p>
        <pre style="background:#0f0f23;color:#E0E0FF;padding:16px;border-radius:8px;font-size:13px;line-height:1.5;white-space:pre-wrap;overflow-x:auto;">{ai_prompt}</pre>
    </div>

    <div style="text-align:center;margin-top:32px;color:#555;font-size:12px;">
        Veille MAG — Podcast Prep
    </div>
</body>
</html>"""

    return html, plain_text


def send_email(html: str, text: str, num_articles: int) -> bool:
    """Send email via SendGrid."""
    load_dotenv()
    api_key = os.getenv("SENDGRID_API_KEY")
    if not api_key:
        raise ValueError("Missing SENDGRID_API_KEY in .env")

    sg = SendGridAPIClient(api_key)

    message = Mail(
        from_email=Email(FROM_EMAIL, FROM_NAME),
        to_emails=To(RECIPIENT_EMAIL, RECIPIENT_NAME),
        subject=f"🎙️ Podcast Prep — Top {num_articles} articles data engineering du mois",
        html_content=Content("text/html", html),
        plain_text_content=Content("text/plain", text),
    )

    try:
        response = sg.send(message)
        logger.info(f"Email sent to {RECIPIENT_EMAIL} (status: {response.status_code})")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Send monthly podcast prep email")
    parser.add_argument("--weeks", type=int, default=4, help="Number of weeks to look back (default: 4)")
    parser.add_argument("--top", type=int, default=15, help="Number of top articles to include (default: 15)")
    parser.add_argument("--dry-run", action="store_true", help="Print content without sending email")
    args = parser.parse_args()

    export_dir = Path(__file__).parent / "export"

    # Find recent weeks
    week_dirs = find_recent_weeks(export_dir, args.weeks)
    if not week_dirs:
        logger.error("No week directories found in export/")
        return

    week_ids = [w.name for w in week_dirs]
    logger.info(f"Loading articles from weeks: {', '.join(week_ids)}")

    # Load all articles
    all_articles = []
    for week_dir in week_dirs:
        articles = load_articles_from_week(week_dir)
        all_articles.extend(articles)
        logger.info(f"  {week_dir.name}: {len(articles)} articles")

    logger.info(f"Total articles loaded: {len(all_articles)}")

    # Select top articles
    top_articles = select_top_articles(all_articles, args.top)
    logger.info(f"Selected top {len(top_articles)} articles")

    # Build email
    html, text = build_email_content(top_articles, week_ids)

    if args.dry_run:
        print(text)
        print("\n\n--- HTML preview saved to /tmp/podcast_prep.html ---")
        with open("/tmp/podcast_prep.html", "w", encoding="utf-8") as f:
            f.write(html)
        return

    # Send email
    if send_email(html, text, len(top_articles)):
        logger.info("Podcast prep email sent successfully!")
    else:
        logger.error("Failed to send podcast prep email")


if __name__ == "__main__":
    main()
