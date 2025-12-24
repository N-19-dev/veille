#!/usr/bin/env python3
"""
Test de la pénalité marketing sur le final_score.
Affiche l'impact avant/après pour les articles marketing détectés.
"""

import sqlite3
import yaml
from pathlib import Path

def test_marketing_penalty():
    print("🧪 TEST PÉNALITÉ MARKETING")
    print("=" * 70)

    # Charger config
    config = yaml.safe_load(Path("config.yaml").read_text(encoding="utf-8"))
    thresholds = config.get("category_thresholds", {})

    # Connecter à la DB
    conn = sqlite3.connect("veille.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Récupérer les 4 articles marketing identifiés par l'audit
    marketing_keywords = ["pricing", "partner"]

    print("\n📊 ARTICLES MARKETING (keywords: pricing, partner, announcing)")
    print("-" * 70)

    cursor.execute("""
        SELECT
            title, source_name, category_key,
            final_score, semantic_score, source_weight, quality_score, tech_score,
            marketing_score
        FROM items
        WHERE (LOWER(title) LIKE '%pricing%'
           OR LOWER(title) LIKE '%partner%'
           OR LOWER(title) LIKE '%announcing%'
           OR LOWER(title) LIKE '%award%')
          AND final_score IS NOT NULL
        ORDER BY created_ts DESC
        LIMIT 10
    """)

    articles = [dict(row) for row in cursor.fetchall()]

    if not articles:
        print("❌ Aucun article marketing trouvé")
        return

    print(f"✅ {len(articles)} articles avec keywords marketing\n")

    for i, a in enumerate(articles, 1):
        threshold = thresholds.get(a["category_key"], 45)
        mkt_score = a["marketing_score"] or 0
        penalty = mkt_score * 0.2

        # Calculer score sans et avec pénalité
        # Le final_score actuel en DB n'a PAS encore la pénalité
        current_final = a["final_score"]
        new_final = current_final - penalty

        print(f"{i}. {a['title'][:60]}...")
        print(f"   Source: {a['source_name']} | Catégorie: {a['category_key']}")
        print(f"   Marketing score: {mkt_score:.0f}")
        print(f"   Final score AVANT pénalité: {current_final:.1f}")
        print(f"   Pénalité marketing: -{penalty:.1f}")
        print(f"   Final score APRÈS pénalité: {new_final:.1f}")
        print(f"   Seuil catégorie: {threshold}")

        if current_final >= threshold and new_final < threshold:
            print(f"   ✅ IMPACT: Article sera REJETÉ (passé de {current_final:.1f} à {new_final:.1f})")
        elif current_final >= threshold and new_final >= threshold:
            print(f"   ⚠️  Reste SÉLECTIONNÉ mais score réduit")
        else:
            print(f"   ℹ️  Déjà rejeté")
        print()

    print("=" * 70)
    print("💡 CONCLUSION")
    print("-" * 70)
    print("Pour appliquer cette pénalité aux articles existants:")
    print("1. Lancer: python analyze_relevance.py")
    print("2. Les scores seront recalculés avec la pénalité marketing")
    print("3. Vérifier que les articles marketing passent en dessous du seuil")

    conn.close()

if __name__ == "__main__":
    test_marketing_penalty()
