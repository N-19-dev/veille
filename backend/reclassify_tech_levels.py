#!/usr/bin/env python3
"""
Reclassification: Calculer tech_level et marketing_score pour tous les articles existants.

Phase 1 - Quick Wins : Application des nouveaux filtres anti-bruit
"""

import sqlite3
from pathlib import Path
from tqdm import tqdm

from content_classifier import (
    calculate_technical_level,
    calculate_marketing_score,
    should_exclude_article,
    detect_beginner_content
)

DB_PATH = Path("veille.db")


def reclassify_all_articles(dry_run: bool = False):
    """
    Recalcule le niveau technique et le score marketing pour tous les articles.

    Args:
        dry_run: Si True, affiche les stats sans modifier la DB
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("🔄 Reclassification des articles avec les nouveaux filtres")
    print("=" * 60)

    # Récupérer tous les articles
    cursor.execute("""
        SELECT id, title, summary, content
        FROM items
        WHERE title IS NOT NULL
    """)

    articles = cursor.fetchall()
    total = len(articles)

    print(f"\n📊 {total} articles à classifier\n")

    # Statistiques
    stats = {
        "beginner": 0,
        "intermediate": 0,
        "advanced": 0,
        "excluded_beginner": 0,
        "excluded_promotional": 0,
        "excluded_low_quality": 0,
        "high_marketing": 0
    }

    updates = []

    for article_id, title, summary, content in tqdm(articles, desc="Classification"):
        # Valeurs par défaut
        title = title or ""
        summary = summary or ""
        content = content or ""

        # Calculer le niveau technique
        tech_level = calculate_technical_level(title, summary, content)
        stats[tech_level] += 1

        # Calculer le score marketing
        marketing_score = calculate_marketing_score(title, summary, content)
        if marketing_score >= 30:
            stats["high_marketing"] += 1

        # Vérifier si l'article doit être exclu
        should_exclude, reason = should_exclude_article(title, summary, content, min_quality_score=50)

        is_excluded = 1 if should_exclude else 0
        exclusion_reason = reason if should_exclude else None

        if reason == "beginner_content":
            stats["excluded_beginner"] += 1
        elif reason == "promotional_content":
            stats["excluded_promotional"] += 1
        elif reason == "low_quality_with_marketing":
            stats["excluded_low_quality"] += 1

        updates.append((
            tech_level,
            marketing_score,
            is_excluded,
            exclusion_reason,
            article_id
        ))

    # Appliquer les mises à jour
    if not dry_run:
        print("\n💾 Mise à jour de la base de données...")
        cursor.executemany("""
            UPDATE items
            SET tech_level = ?,
                marketing_score = ?,
                is_excluded = ?,
                exclusion_reason = ?
            WHERE id = ?
        """, updates)

        conn.commit()
        print("✅ Base de données mise à jour")
    else:
        print("\n⏭️  Mode dry-run : aucune modification appliquée")

    # Afficher les statistiques
    print("\n" + "=" * 60)
    print("📊 Résultats de la classification:")
    print("=" * 60)

    print("\n🎯 Niveau technique:")
    print(f"  🟢 Débutant:      {stats['beginner']:>4} ({100*stats['beginner']/total:>5.1f}%)")
    print(f"  🟡 Intermédiaire: {stats['intermediate']:>4} ({100*stats['intermediate']/total:>5.1f}%)")
    print(f"  🔴 Avancé:        {stats['advanced']:>4} ({100*stats['advanced']/total:>5.1f}%)")

    print("\n🚫 Articles exclus (filtrage anti-bruit):")
    total_excluded = stats["excluded_beginner"] + stats["excluded_promotional"] + stats["excluded_low_quality"]
    print(f"  Total exclus:          {total_excluded:>4} ({100*total_excluded/total:>5.1f}%)")
    print(f"  - Contenu débutant:    {stats['excluded_beginner']:>4}")
    print(f"  - Contenu promotionnel: {stats['excluded_promotional']:>4}")
    print(f"  - Basse qualité + marketing: {stats['excluded_low_quality']:>4}")

    print("\n📈 Score marketing:")
    print(f"  Articles avec score marketing ≥ 30: {stats['high_marketing']} ({100*stats['high_marketing']/total:.1f}%)")

    print("\n" + "=" * 60)
    print("💡 Impact sur la qualité du feed:")
    print("=" * 60)

    kept = total - total_excluded
    print(f"  Articles conservés:  {kept:>4} ({100*kept/total:>5.1f}%)")
    print(f"  Articles exclus:     {total_excluded:>4} ({100*total_excluded/total:>5.1f}%)")

    if not dry_run:
        # Statistiques post-migration
        cursor.execute("""
            SELECT
                COUNT(*) FILTER (WHERE is_excluded = 0) as kept,
                COUNT(*) FILTER (WHERE is_excluded = 1) as excluded,
                COUNT(*) FILTER (WHERE tech_level = 'beginner' AND is_excluded = 0) as beginner_kept,
                COUNT(*) FILTER (WHERE tech_level = 'intermediate' AND is_excluded = 0) as intermediate_kept,
                COUNT(*) FILTER (WHERE tech_level = 'advanced' AND is_excluded = 0) as advanced_kept
            FROM items
        """)

        result = cursor.fetchone()
        kept_db, excluded_db, beg_kept, int_kept, adv_kept = result

        print("\n✅ Vérification base de données:")
        print(f"  Articles conservés:   {kept_db}")
        print(f"  Articles exclus:      {excluded_db}")
        print(f"\n  Distribution des articles conservés:")
        print(f"    🟢 Débutant:      {beg_kept} ({100*beg_kept/kept_db:.1f}%)" if kept_db > 0 else "    🟢 Débutant:      0")
        print(f"    🟡 Intermédiaire: {int_kept} ({100*int_kept/kept_db:.1f}%)" if kept_db > 0 else "    🟡 Intermédiaire: 0")
        print(f"    🔴 Avancé:        {adv_kept} ({100*adv_kept/kept_db:.1f}%)" if kept_db > 0 else "    🔴 Avancé:        0")

    conn.close()

    print("\n" + "=" * 60)
    print("✅ Reclassification terminée!")
    print("=" * 60)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Reclassifier les articles avec les nouveaux filtres")
    parser.add_argument("--dry-run", action="store_true", help="Mode test sans modification de la DB")

    args = parser.parse_args()

    reclassify_all_articles(dry_run=args.dry_run)
