import os
import sys
import subprocess

def run(cmd: list[str]):
    print("\n+ " + " ".join(cmd))
    subprocess.run(cmd, check=True)

def main():
    config = "config.yaml"
    week_offset = os.getenv("WEEK_OFFSET", "0")

    # 1️⃣ CRAWL : récupération de tous les articles
    run([sys.executable, "veille_tech.py",
         "--config", config,
         "--week-offset", week_offset])

    # 1️⃣-bis CLASSIFICATION LLM : correction des catégories
    run([sys.executable, "classify_llm.py",
         "--config", config,
         "--week-offset", week_offset])

    # 2️⃣ SCORING PERTINENCE : embeddings + règles
    run([sys.executable, "analyze_relevance.py",
         "--config", config,
         "--week-offset", week_offset])

    # 3️⃣ RÉSUMÉ DE LA SEMAINE (LLM)
    run([sys.executable, "summarize_week_llm.py",
         "--config", config,
         "--week-offset", week_offset])

    print("\n✨ Workflow complet terminé !")
    print("→ Résultat dans export/<YYYYwWW>/")

if __name__ == "__main__":
    main()