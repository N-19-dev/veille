# 🔍 Veille Tech Crawling

Système automatisé de veille technologique pour Data Engineers, utilisant l'IA pour la classification, le scoring et la génération de résumés hebdomadaires.

[![Deploy Frontend](https://github.com/USERNAME/veille_tech_crawling/actions/workflows/deploy-frontend.yml/badge.svg)](https://github.com/USERNAME/veille_tech_crawling/actions/workflows/deploy-frontend.yml)
[![Backend Weekly](https://github.com/USERNAME/veille_tech_crawling/actions/workflows/backend-weekly.yml/badge.svg)](https://github.com/USERNAME/veille_tech_crawling/actions/workflows/backend-weekly.yml)

## 📋 Table des matières

- [Vue d'ensemble](#-vue-densemble)
- [Architecture](#-architecture)
- [Fonctionnalités](#-fonctionnalités)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Utilisation](#-utilisation)
- [Déploiement](#-déploiement)
- [Technologies](#-technologies)
- [Roadmap](#-roadmap)
- [Contribution](#-contribution)

## 🎯 Vue d'ensemble

Ce projet automatise la veille technologique en :
1. **Crawlant** 60+ sources RSS/Atom (blogs tech, newsletters, Medium, dev.to)
2. **Classifiant** les articles avec un LLM (8 catégories : warehouses, orchestration, ML, etc.)
3. **Scorant** la pertinence via embeddings sémantiques + règles qualité
4. **Générant** un résumé hebdomadaire intelligent
5. **Publiant** sur une interface web moderne

**Exemple de sortie** : [Voir le digest de la semaine](https://USERNAME.github.io/veille_tech_crawling/)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   GitHub Actions (Lundi 06:00 UTC)          │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────▼────────────────┐
        │     Backend Python Pipeline     │
        │                                 │
        │  1. veille_tech.py             │ ← Crawl RSS + autodécouverte
        │  2. classify_llm.py            │ ← Classification LLM
        │  3. analyze_relevance.py       │ ← Scoring (embeddings + règles)
        │  4. summarize_week_llm.py      │ ← Résumé LLM
        │                                 │
        │  📦 Output: export/2025wXX/    │
        │     ├── digest.json            │
        │     ├── digest.md              │
        │     ├── selection.json         │
        │     └── summary.json           │
        └────────────┬────────────────────┘
                     │
        ┌────────────▼─────────────┐
        │   Git commit + push      │
        │   Trigger Frontend build │
        └────────────┬─────────────┘
                     │
        ┌────────────▼─────────────────────┐
        │  Frontend React + Vite           │
        │                                  │
        │  • Interface moderne (Tailwind)  │
        │  • Top 3 articles                │
        │  • Sections par catégorie        │
        │  • Sélecteur de semaines         │
        │                                  │
        │  🌐 Deploy: GitHub Pages        │
        └──────────────────────────────────┘
```

## ✨ Fonctionnalités

### Backend
- ✅ Crawling intelligent avec respect robots.txt + rate limiting
- ✅ Autodécouverte de feeds RSS/Atom
- ✅ Classification LLM multi-catégories
- ✅ Scoring de pertinence par embeddings sémantiques (sentence-transformers)
- ✅ Déduplication par hash (URL + titre)
- ✅ Extraction de contenu (readability + BeautifulSoup)
- ✅ Stockage SQLite + export JSON/Markdown
- ✅ Génération de résumés LLM hebdomadaires

### Frontend
- ✅ Interface React moderne (Vite + TypeScript)
- ✅ Design responsive (Tailwind CSS)
- ✅ Top 3 des articles les plus pertinents
- ✅ Navigation par semaine
- ✅ Rendu Markdown avec code highlighting
- ✅ Scores de pertinence visibles

## 🚀 Installation

### Prérequis
- **Python** 3.11+
- **Node.js** 20+
- **API Key Groq** (gratuite : https://console.groq.com)

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend

```bash
cd frontend
npm install
```

## ⚙️ Configuration

### 1. Variables d'environnement

Créez un fichier `.env` dans `backend/` :

```bash
# API LLM (Groq gratuit)
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Optionnel : Notifications Slack
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx/yyy/zzz
```

### 2. Personnaliser config.yaml

Éditez `backend/config.yaml` :

```yaml
# Ajustez les catégories selon votre domaine
categories:
  - key: "your_category"
    title: "🎯 Your Category"
    keywords: ["keyword1", "keyword2"]

# Ajoutez vos sources
sources:
  - name: "Your Blog"
    url: "https://yourblog.com/feed"

# Ajustez les seuils de pertinence
relevance:
  score_threshold: 60  # Min score pour être inclus
```

### 3. URL du User-Agent

**Important** : Dans `config.yaml`, remplacez :

```yaml
user_agent: "VeilleTechBot/1.0 (+https://github.com/YOUR_USERNAME/veille_tech_crawling)"
```

## 💻 Utilisation

### Exécution locale

#### Mode manuel (semaine en cours)
```bash
cd backend
python main.py
```

#### Semaine dernière (N-1)
```bash
WEEK_OFFSET=-1 python main.py
```

#### Semaine spécifique
```bash
WEEK_OFFSET=-2 python main.py  # Il y a 2 semaines
```

### Frontend local

```bash
cd frontend
npm run dev
# Ouvre http://localhost:5173
```

### Build production

```bash
cd frontend
npm run build
# Output dans frontend/dist/
```

## 🌐 Déploiement

### GitHub Actions (Automatique)

Le projet est configuré pour un déploiement automatique :

**1. Backend hebdomadaire** (`.github/workflows/backend-weekly.yml`)
- Trigger : Tous les lundis à 06:00 UTC
- Action : Crawl + classification + scoring + résumé
- Commit les exports dans `export/`

**2. Frontend GitHub Pages** (`.github/workflows/deploy-frontend.yml`)
- Trigger : Push sur `main` OU fin du backend
- Action : Build React + deploy sur GitHub Pages

### Configuration des secrets GitHub

Dans Settings → Secrets and variables → Actions, ajoutez :

| Secret | Description |
|--------|-------------|
| `GROQ_API_KEY` | Votre clé API Groq (gratuite) |
| `PAT_TOKEN` | Personal Access Token avec scope `repo` + `workflow` |

**Créer le PAT** : https://github.com/settings/tokens → Generate new token (classic) → Cocher `repo` + `workflow`

### Activer GitHub Pages

Settings → Pages → Source: **GitHub Actions**

## 🛠️ Technologies

### Backend
- **Python 3.11+** : Langage principal
- **asyncio + aiohttp** : Crawling asynchrone
- **feedparser** : Parsing RSS/Atom
- **sentence-transformers** : Embeddings sémantiques
- **openai (Groq)** : Classification + résumés LLM
- **BeautifulSoup + readability** : Extraction de contenu
- **SQLite** : Stockage et déduplication
- **Pydantic** : Validation de configuration

### Frontend
- **React 19** : Framework UI
- **TypeScript** : Typage statique
- **Vite** : Build tool moderne
- **Tailwind CSS** : Design system
- **marked** : Rendu Markdown
- **Fuse.js** : Recherche floue (à implémenter)

### CI/CD
- **GitHub Actions** : Automatisation
- **GitHub Pages** : Hébergement statique

## 📊 Structure du projet

```
veille_tech_crawling/
├── backend/
│   ├── veille_tech.py              # 1. Crawling RSS + extraction
│   ├── classify_llm.py             # 2. Classification LLM
│   ├── analyze_relevance.py        # 3. Scoring pertinence
│   ├── summarize_week_llm.py       # 4. Résumé hebdomadaire
│   ├── main.py                     # Pipeline complet
│   ├── config.yaml                 # Configuration centrale
│   ├── requirements.txt            # Dépendances Python
│   └── veille.db                   # Base SQLite (gitignored)
│
├── frontend/
│   ├── src/
│   │   ├── components/             # Composants React
│   │   ├── lib/parse.ts            # Parsing des exports
│   │   └── App.tsx                 # Composant principal
│   ├── public/export/              # Exports copiés (build)
│   ├── package.json
│   └── vite.config.ts
│
├── .github/workflows/
│   ├── backend-weekly.yml          # Crawl hebdomadaire
│   └── deploy-frontend.yml         # Deploy GitHub Pages
│
├── export/                         # Exports hebdomadaires
│   ├── 2025w48/
│   │   ├── digest.json
│   │   ├── selection.json
│   │   └── summary.json
│   └── latest → 2025w48            # Symlink vers dernière semaine
│
└── README.md                       # Ce fichier
```

## 🗺️ Roadmap

### Court terme
- [x] Documentation complète
- [ ] Tests unitaires (pytest)
- [ ] Logging structuré (loguru)
- [ ] Barre de recherche frontend
- [ ] Filtres par catégorie

### Moyen terme
- [ ] API REST (FastAPI)
- [ ] Monitoring (Sentry)
- [ ] Cache embeddings (Redis)
- [ ] Export PDF
- [ ] Mode sombre

### Long terme
- [ ] Dashboard analytics (tendances)
- [ ] Personnalisation par utilisateur
- [ ] Recommandations ML
- [ ] Application mobile

## 🤝 Contribution

Les contributions sont bienvenues !

1. Fork le projet
2. Créez une branche (`git checkout -b feature/amélioration`)
3. Committez (`git commit -m 'Add: nouvelle fonctionnalité'`)
4. Push (`git push origin feature/amélioration`)
5. Ouvrez une Pull Request

## 📝 Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 👨‍💻 Auteur

**Nathan Sornet**
- GitHub: [@nathansornet](https://github.com/nathansornet)
- LinkedIn: [Nathan Sornet](https://linkedin.com/in/nathansornet)

## 🙏 Remerciements

- **Groq** pour l'API LLM gratuite
- **GitHub** pour Pages et Actions
- Toutes les sources de blogs tech agrégées

---

⭐ Si ce projet vous est utile, n'hésitez pas à lui donner une étoile !
