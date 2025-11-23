#!/usr/bin/env python3
"""
Script pour forcer la régénération des 3 dernières semaines.
Usage: python regenerate_weeks.py [--skip-llm]
"""
import os
import sys
import subprocess
import argparse

def run(cmd: list[str], allow_failure: bool = False):
    """Exécute une commande et affiche le résultat."""
    print("\n" + "="*80)
    print("+ " + " ".join(cmd))
    print("="*80)
    result = subprocess.run(cmd, check=False)
    if result.returncode != 0 and not allow_failure:
        raise subprocess.CalledProcessError(result.returncode, cmd)
    return result.returncode == 0

def regenerate_week(week_offset: int, skip_llm: bool = False):
    """Régénère toutes les données pour une semaine donnée."""
    config = "config.yaml"
    offset_str = str(week_offset)
    
    print(f"\n{'#'*80}")
    print(f"# RÉGÉNÉRATION DE LA SEMAINE {week_offset}")
    print(f"{'#'*80}\n")
    
    # 1️⃣ CRAWL : récupération de tous les articles
    print(f"\n📥 Étape 1/4 : Crawl des articles (semaine {week_offset})...")
    run([sys.executable, "veille_tech.py",
         "--config", config,
         "--week-offset", offset_str])
    
    # 2️⃣ CLASSIFICATION LLM : correction des catégories
    print(f"\n🏷️  Étape 2/4 : Classification LLM (semaine {week_offset})...")
    # Permet l'échec si GROQ_API_KEY n'est pas définie
    run([sys.executable, "classify_llm.py",
         "--config", config,
         "--week-offset", offset_str], allow_failure=True)
    
    # 3️⃣ SCORING PERTINENCE : embeddings + règles
    print(f"\n📊 Étape 3/4 : Analyse de pertinence (semaine {week_offset})...")
    run([sys.executable, "analyze_relevance.py",
         "--config", config,
         "--week-offset", offset_str])
    
    # 4️⃣ RÉSUMÉ DE LA SEMAINE (LLM) - optionnel
    if skip_llm:
        print(f"\n⏭️  Étape 4/4 : Résumé de la semaine (IGNORÉ - skip-llm activé)")
    else:
        print(f"\n📝 Étape 4/4 : Résumé de la semaine (semaine {week_offset})...")
        # Permet l'échec si GROQ_API_KEY n'est pas définie
        success = run([sys.executable, "summarize_week_llm.py",
                      "--config", config,
                      "--week-offset", offset_str], allow_failure=True)
        if not success:
            print("\n⚠️  Le résumé LLM a échoué (probablement GROQ_API_KEY manquant)")
            print("   Les autres données ont été régénérées avec succès.")
    
    print(f"\n✅ Semaine {week_offset} régénérée avec succès !")

def main():
    """Régénère les 3 dernières semaines."""
    parser = argparse.ArgumentParser(
        description="Régénère les 3 dernières semaines de veille technologique"
    )
    parser.add_argument(
        "--skip-llm",
        action="store_true",
        help="Ignore les étapes nécessitant l'API LLM (classification et résumé)"
    )
    args = parser.parse_args()
    
    # Vérifier si GROQ_API_KEY est définie
    has_api_key = os.getenv("GROQ_API_KEY") is not None
    
    print("\n" + "🔄 "*20)
    print("RÉGÉNÉRATION DES 3 DERNIÈRES SEMAINES")
    print("🔄 "*20 + "\n")
    
    if not has_api_key and not args.skip_llm:
        print("⚠️  GROQ_API_KEY n'est pas définie dans l'environnement.")
        print("   Les étapes LLM (classification et résumé) seront ignorées en cas d'erreur.\n")
    
    if args.skip_llm:
        print("ℹ️  Mode --skip-llm activé : les résumés LLM seront ignorés.\n")
    
    # Semaines à régénérer : -1, -2, -3
    weeks_to_regenerate = [-1, -2, -3]
    
    for week_offset in weeks_to_regenerate:
        try:
            regenerate_week(week_offset, skip_llm=args.skip_llm)
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Erreur lors de la régénération de la semaine {week_offset}")
            print(f"   Erreur: {e}")
            response = input(f"\nContinuer avec les semaines suivantes ? (o/n) : ")
            if response.lower() != 'o':
                print("\n⚠️  Régénération interrompue par l'utilisateur.")
                sys.exit(1)
    
    print("\n" + "✨ "*20)
    print("RÉGÉNÉRATION TERMINÉE AVEC SUCCÈS !")
    print("✨ "*20)
    print("\n→ Résultats disponibles dans export/")

if __name__ == "__main__":
    main()
