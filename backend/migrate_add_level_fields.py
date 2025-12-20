#!/usr/bin/env python3
"""
Migration: Ajouter les champs tech_level et marketing_score à la table items.

Phase 1 - Quick Wins : Filtrage anti-bruit et niveau technique
"""

import sqlite3
from pathlib import Path

DB_PATH = Path("veille.db")


def migrate():
    """Ajoute les nouvelles colonnes si elles n'existent pas."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("🔄 Migration: Ajout des champs tech_level et marketing_score")
    print("=" * 60)

    # Vérifier les colonnes existantes
    cursor.execute("PRAGMA table_info(items)")
    existing_columns = {row[1] for row in cursor.fetchall()}

    # Ajouter tech_level si manquant
    if "tech_level" not in existing_columns:
        print("\n✅ Ajout de la colonne 'tech_level' (TEXT)")
        cursor.execute("""
            ALTER TABLE items
            ADD COLUMN tech_level TEXT DEFAULT 'intermediate'
        """)
        print("   → Colonne ajoutée avec succès")
    else:
        print("\n⏭️  La colonne 'tech_level' existe déjà")

    # Ajouter marketing_score si manquant
    if "marketing_score" not in existing_columns:
        print("\n✅ Ajout de la colonne 'marketing_score' (INTEGER)")
        cursor.execute("""
            ALTER TABLE items
            ADD COLUMN marketing_score INTEGER DEFAULT 0
        """)
        print("   → Colonne ajoutée avec succès")
    else:
        print("\n⏭️  La colonne 'marketing_score' existe déjà")

    # Ajouter is_excluded si manquant (pour tracking des articles exclus)
    if "is_excluded" not in existing_columns:
        print("\n✅ Ajout de la colonne 'is_excluded' (INTEGER)")
        cursor.execute("""
            ALTER TABLE items
            ADD COLUMN is_excluded INTEGER DEFAULT 0
        """)
        print("   → Colonne ajoutée avec succès")
    else:
        print("\n⏭️  La colonne 'is_excluded' existe déjà")

    # Ajouter exclusion_reason si manquant
    if "exclusion_reason" not in existing_columns:
        print("\n✅ Ajout de la colonne 'exclusion_reason' (TEXT)")
        cursor.execute("""
            ALTER TABLE items
            ADD COLUMN exclusion_reason TEXT
        """)
        print("   → Colonne ajoutée avec succès")
    else:
        print("\n⏭️  La colonne 'exclusion_reason' existe déjà")

    conn.commit()

    # Afficher le résumé
    cursor.execute("PRAGMA table_info(items)")
    all_columns = cursor.fetchall()

    print("\n" + "=" * 60)
    print("📊 Structure de la table 'items' après migration:")
    print("=" * 60)

    for col in all_columns:
        col_name = col[1]
        col_type = col[2]
        col_default = col[4] if col[4] else "NULL"
        print(f"  {col_name:<30} {col_type:<15} DEFAULT {col_default}")

    # Statistiques
    cursor.execute("SELECT COUNT(*) FROM items")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM items WHERE tech_level IS NOT NULL AND tech_level != 'intermediate'")
    already_classified = cursor.fetchone()[0]

    print("\n" + "=" * 60)
    print("📈 Statistiques:")
    print("=" * 60)
    print(f"  Total d'articles: {total}")
    print(f"  Articles déjà classifiés: {already_classified}")
    print(f"  Articles à classifier: {total - already_classified}")

    conn.close()

    print("\n✅ Migration terminée avec succès!")
    print("\n💡 Prochaine étape:")
    print("   Relancer le crawl pour calculer le niveau technique des nouveaux articles:")
    print("   $ python veille_tech.py --config config.yaml")


if __name__ == "__main__":
    migrate()
