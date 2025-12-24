#!/usr/bin/env python3
"""
Script d'audit de pertinence pour analyser les articles sélectionnés.
Identifie les faux positifs (bruit, marketing, beginner) et faux négatifs.
"""

import sqlite3
import yaml
import re
from collections import defaultdict, Counter
from typing import List, Dict, Any
import statistics

# Patterns de détection de bruit
MARKETING_KEYWORDS = [
    "sponsored", "partner", "partnership", "webinar", "free trial",
    "download now", "sign up", "get started", "pricing", "plans",
    "discount", "offer", "promotion", "sale", "buy", "purchase",
    "advertise", "ad-", "announcement", "press release"
]

BEGINNER_KEYWORDS = [
    "introduction to", "intro to", "getting started", "beginner",
    "101", "basics", "fundamentals", "what is", "tutorial",
    "for beginners", "crash course", "easy guide", "simple guide",
    "step by step", "hello world", "first steps"
]

def load_config():
    """Charge la configuration."""
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def analyze_articles(limit: int = 100):
    """Analyse les derniers articles sélectionnés."""
    conn = sqlite3.connect("veille.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Récupérer config pour les seuils
    config = load_config()
    thresholds = config.get("category_thresholds", {})
    default_threshold = 45

    print(f"📊 AUDIT DE PERTINENCE - {limit} derniers articles")
    print("=" * 70)

    # Récupérer les articles récents sélectionnés (final_score au-dessus des seuils)
    cursor.execute("""
        SELECT
            id, url, title, source_name, category_key,
            final_score, semantic_score, source_weight, quality_score, tech_score,
            published_ts, created_ts,
            LENGTH(content) as content_length
        FROM items
        WHERE final_score IS NOT NULL
        ORDER BY created_ts DESC
        LIMIT ?
    """, (limit,))

    articles = [dict(row) for row in cursor.fetchall()]

    if not articles:
        print("❌ Aucun article trouvé dans la base de données")
        return

    print(f"✅ {len(articles)} articles analysés\n")

    # Statistiques globales
    scores = [a["final_score"] for a in articles]
    print("📈 STATISTIQUES GLOBALES")
    print("-" * 70)
    print(f"Score final moyen: {statistics.mean(scores):.1f}")
    print(f"Score final médian: {statistics.median(scores):.1f}")
    print(f"Score final min/max: {min(scores):.1f} / {max(scores):.1f}")
    print(f"Écart-type: {statistics.stdev(scores):.1f}\n")

    # Distribution par catégorie
    print("📊 DISTRIBUTION PAR CATÉGORIE")
    print("-" * 70)
    by_category = defaultdict(list)
    for a in articles:
        by_category[a["category_key"]].append(a)

    for cat, items in sorted(by_category.items(), key=lambda x: len(x[1]), reverse=True):
        cat_scores = [i["final_score"] for i in items]
        threshold = thresholds.get(cat, default_threshold)
        print(f"{cat:25s} | {len(items):3d} articles | "
              f"Avg: {statistics.mean(cat_scores):5.1f} | "
              f"Seuil: {threshold:3d}")
    print()

    # Détection de faux positifs - Marketing
    print("🚨 DÉTECTION FAUX POSITIFS - MARKETING")
    print("-" * 70)
    marketing_articles = []
    for a in articles:
        title_lower = a["title"].lower()
        marketing_matches = [kw for kw in MARKETING_KEYWORDS if kw in title_lower]
        if marketing_matches:
            marketing_articles.append((a, marketing_matches))

    if marketing_articles:
        print(f"⚠️  {len(marketing_articles)} articles suspects (mots-clés marketing)")
        for a, keywords in marketing_articles[:10]:  # Top 10
            print(f"  - [{a['final_score']:.0f}] {a['title'][:60]}...")
            print(f"    Keywords: {', '.join(keywords)}")
            print(f"    Source: {a['source_name']}")
    else:
        print("✅ Aucun article marketing détecté")
    print()

    # Détection de faux positifs - Beginner
    print("🚨 DÉTECTION FAUX POSITIFS - BEGINNER")
    print("-" * 70)
    beginner_articles = []
    for a in articles:
        title_lower = a["title"].lower()
        beginner_matches = [kw for kw in BEGINNER_KEYWORDS if kw in title_lower]
        if beginner_matches:
            beginner_articles.append((a, beginner_matches))

    if beginner_articles:
        print(f"⚠️  {len(beginner_articles)} articles beginner détectés")
        for a, keywords in beginner_articles[:10]:  # Top 10
            print(f"  - [{a['final_score']:.0f}] {a['title'][:60]}...")
            print(f"    Keywords: {', '.join(keywords)}")
            print(f"    Source: {a['source_name']}")
    else:
        print("✅ Aucun article beginner détecté")
    print()

    # Articles à la frontière (score proche du seuil)
    print("🎯 ARTICLES À LA FRONTIÈRE (score ± 5 du seuil)")
    print("-" * 70)
    border_articles = []
    for a in articles:
        threshold = thresholds.get(a["category_key"], default_threshold)
        if threshold - 5 <= a["final_score"] <= threshold + 5:
            border_articles.append(a)

    if border_articles:
        print(f"📍 {len(border_articles)} articles à la frontière")
        for a in border_articles[:10]:
            threshold = thresholds.get(a["category_key"], default_threshold)
            print(f"  - [{a['final_score']:.0f}] (seuil: {threshold}) {a['title'][:50]}...")
            print(f"    Source: {a['source_name']} | Catégorie: {a['category_key']}")
    else:
        print("✅ Peu d'articles à la frontière")
    print()

    # Top sources
    print("📰 TOP SOURCES (articles sélectionnés)")
    print("-" * 70)
    source_counts = Counter([a["source_name"] for a in articles])
    for source, count in source_counts.most_common(10):
        source_articles = [a for a in articles if a["source_name"] == source]
        avg_score = statistics.mean([a["final_score"] for a in source_articles])
        print(f"{source:35s} | {count:3d} articles | Avg score: {avg_score:.1f}")
    print()

    # Analyse des articles REJETÉS (score en dessous du seuil)
    print("❌ ANALYSE FAUX NÉGATIFS (articles rejetés)")
    print("-" * 70)

    # Récupérer des articles rejetés (score entre 35 et seuil)
    cursor.execute("""
        SELECT
            id, url, title, source_name, category_key,
            final_score, semantic_score, source_weight, quality_score, tech_score
        FROM items
        WHERE final_score IS NOT NULL
          AND final_score BETWEEN 35 AND 50
        ORDER BY final_score DESC
        LIMIT 50
    """)

    rejected = [dict(row) for row in cursor.fetchall()]
    if rejected:
        print(f"🔍 {len(rejected)} articles rejetés analysés (score 35-50)")

        # Regrouper par catégorie
        rejected_by_cat = defaultdict(list)
        for r in rejected:
            rejected_by_cat[r["category_key"]].append(r)

        for cat, items in sorted(rejected_by_cat.items(), key=lambda x: len(x[1]), reverse=True):
            threshold = thresholds.get(cat, default_threshold)
            print(f"\n  {cat} (seuil: {threshold}):")
            for r in items[:3]:  # Top 3 par catégorie
                print(f"    - [{r['final_score']:.0f}] {r['title'][:55]}...")
                print(f"      Source: {r['source_name']}")
    else:
        print("✅ Peu d'articles rejetés dans la zone 35-50")
    print()

    # Recommandations
    print("💡 RECOMMANDATIONS")
    print("=" * 70)

    if marketing_articles:
        print(f"1. 🚨 Ajouter blacklist marketing ({len(marketing_articles)} articles)")
        print(f"   Keywords: {', '.join(set([kw for _, kws in marketing_articles for kw in kws]))}")

    if beginner_articles:
        print(f"2. 📚 Améliorer détection beginner ({len(beginner_articles)} articles)")
        print(f"   Keywords: {', '.join(set([kw for _, kws in beginner_articles for kw in kws]))}")

    if border_articles:
        print(f"3. 🎯 Revoir seuils pour {len(border_articles)} articles frontière")

    # Suggestions de seuils
    print("\n4. 📊 Suggestions d'ajustement de seuils:")
    for cat, items in sorted(by_category.items(), key=lambda x: len(x[1]), reverse=True):
        if len(items) < 5:
            continue
        cat_scores = [i["final_score"] for i in items]
        current_threshold = thresholds.get(cat, default_threshold)
        avg = statistics.mean(cat_scores)
        median = statistics.median(cat_scores)

        # Si la moyenne est bien au-dessus du seuil, on peut l'augmenter
        if avg > current_threshold + 10:
            suggested = int(median - 5)
            print(f"   {cat:25s} | Actuel: {current_threshold:3d} → Suggéré: {suggested:3d} "
                  f"(avg: {avg:.0f}, médian: {median:.0f})")

    conn.close()

if __name__ == "__main__":
    analyze_articles(limit=100)
