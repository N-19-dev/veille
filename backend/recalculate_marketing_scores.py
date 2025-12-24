#!/usr/bin/env python3
"""
Recalcule les marketing_scores pour tous les articles existants en DB.
"""

import sqlite3
from content_classifier import calculate_marketing_score

def recalculate_all_marketing_scores():
    print("🔄 RECALCUL DES MARKETING SCORES")
    print("=" * 70)

    conn = sqlite3.connect("veille.db")
    cursor = conn.cursor()

    # Récupérer tous les articles
    cursor.execute("""
        SELECT id, title, summary, content
        FROM items
        WHERE title IS NOT NULL
    """)

    articles = cursor.fetchall()
    print(f"📊 {len(articles)} articles à recalculer\n")

    updated = 0
    high_marketing = []

    for id_, title, summary, content in articles:
        summary = summary or ""
        content = content or ""

        # Calculer le score marketing
        mkt_score = calculate_marketing_score(title, summary, content)

        # Mettre à jour en DB
        cursor.execute("""
            UPDATE items
            SET marketing_score = ?
            WHERE id = ?
        """, (mkt_score, id_))

        updated += 1

        # Tracker les articles avec score marketing élevé
        if mkt_score >= 20:
            high_marketing.append((title, mkt_score))

        if updated % 100 == 0:
            print(f"  Traités: {updated}/{len(articles)}")

    conn.commit()
    conn.close()

    print(f"\n✅ {updated} articles mis à jour")

    if high_marketing:
        print(f"\n🚨 {len(high_marketing)} articles avec marketing_score >= 20:")
        for title, score in sorted(high_marketing, key=lambda x: x[1], reverse=True)[:20]:
            print(f"  [{score:3d}] {title[:65]}...")

    print("\n💡 Relancer maintenant: python test_marketing_penalty.py")

if __name__ == "__main__":
    recalculate_all_marketing_scores()
