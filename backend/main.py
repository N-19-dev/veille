# Orchestration : crawl (semaine) -> analyse LLM (semaine)
import os
import sys
import subprocess

def run(cmd: list[str]):
    print("+", " ".join(cmd))
    subprocess.run(cmd, check=True)

def main():
    config = "config.yaml"
    week_offset = os.getenv("WEEK_OFFSET", "0")

    run([sys.executable, "veille_tech.py", "--config", config, "--week-offset", week_offset])
    run([sys.executable, "analyze_llm.py", "--config", config, "--week-offset", week_offset])

if __name__ == "__main__":
    main()