import os
import sys
import subprocess
from sentry_init import init_sentry, set_tag, capture_exception, capture_message

def run(cmd: list[str]):
    print("\n+ " + " ".join(cmd))
    subprocess.run(cmd, check=True)

def main():
    # Initialiser Sentry pour monitoring d'erreurs
    init_sentry(environment="production", enable_tracing=True)

    config = "config.yaml"
    week_offset = os.getenv("WEEK_OFFSET", "0")

    # Ajouter tags pour contextualiser les erreurs
    set_tag("week_offset", week_offset)
    set_tag("pipeline", "weekly-digest")

    try:
        # 1️⃣ CRAWL : récupération de tous les articles
        set_tag("pipeline_step", "crawl")
        run([sys.executable, "veille_tech.py",
             "--config", config,
             "--week-offset", week_offset])

        # 1️⃣-bis CLASSIFICATION LLM : correction des catégories
        set_tag("pipeline_step", "classify")
        run([sys.executable, "classify_llm.py",
             "--config", config,
             "--week-offset", week_offset])

        # 2️⃣ SCORING PERTINENCE : embeddings + règles
        set_tag("pipeline_step", "scoring")
        run([sys.executable, "analyze_relevance.py",
             "--config", config,
             "--week-offset", week_offset])

        # 3️⃣ RÉSUMÉ DE LA SEMAINE (LLM)
        set_tag("pipeline_step", "summarize")
        run([sys.executable, "summarize_week_llm.py",
             "--config", config,
             "--week-offset", week_offset])

        print("\n✨ Workflow complet terminé !")
        print("→ Résultat dans export/<YYYYwWW>/")

        # Message de succès à Sentry (pour tracking)
        capture_message(f"Pipeline weekly-digest complété (week_offset={week_offset})", level="info")

    except subprocess.CalledProcessError as e:
        # Erreur dans un des sous-processus
        capture_exception(e)
        print(f"\n❌ Erreur dans le pipeline (étape {e.cmd[1]})")
        raise

    except Exception as e:
        # Toute autre erreur
        capture_exception(e)
        print(f"\n❌ Erreur inattendue: {e}")
        raise

if __name__ == "__main__":
    main()