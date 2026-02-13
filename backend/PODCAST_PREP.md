# Podcast Prep - Monthly Data Engineering News

Script pour preparer le contenu d'un podcast mensuel de news data engineering.

## Utilisation

```bash
cd backend
source .venv/bin/activate

# Afficher le contenu dans le terminal (dry-run)
python podcast_digest.py --dry-run

# Options
python podcast_digest.py --dry-run --weeks 6    # 6 semaines au lieu de 4
python podcast_digest.py --dry-run --top 20     # 20 articles au lieu de 15

# Envoyer par mail (necessite SENDGRID_API_KEY dans .env)
python podcast_digest.py
```

## Ce que le script fait

1. Charge les articles des N dernieres semaines depuis `export/`
2. Selectionne les meilleurs par score avec diversite de categories
3. Genere un resume groupe par theme + un prompt IA pour generer le script du podcast
4. Affiche dans le terminal (`--dry-run`) ou envoie par mail

## Prompt IA

Le mail/output contient un prompt pret a copier-coller dans Claude ou ChatGPT qui genere :
- Le script complet du podcast (15-20 min)
- Les bullet points pour un post LinkedIn
