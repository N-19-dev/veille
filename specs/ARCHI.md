# Architecture Technique - Veille Tech Crawling

*Document généré automatiquement par analyse du code - Date : 2025-12-20*

## 1. Vue d'Ensemble

**Type de projet :** Full-Stack Web Application
**Stack principale :** Python (Backend) + React + TypeScript (Frontend)

Système automatisé de veille technologique pour Data Engineers qui crawle 60+ sources RSS, classifie les articles via LLM, score la pertinence par embeddings sémantiques, et génère des résumés hebdomadaires publiés sur une interface web moderne.

**Architecture Globale :**
```
GitHub Actions (Lundi 06:00 UTC)
  ↓
Backend Python Pipeline (4 étapes séquentielles)
  ├── 1. Crawling RSS + extraction contenu
  ├── 2. Classification LLM (Groq)
  ├── 3. Scoring pertinence (embeddings)
  └── 4. Génération résumé LLM
  ↓
Export JSON/Markdown → Git commit + push
  ↓
Frontend React Build (Vite)
  ↓
GitHub Pages Deploy
```

---

## 2. Stack Technique Détaillée

### Backend Python

#### **Runtime & Core**
- **Python** : 3.11+ (asyncio natif)
- **Package Manager** : pip + venv
- **Virtual Env** : `.venv/` (gitignored)

#### **Crawling & HTTP**
- **aiohttp** : Client HTTP asynchrone
- **aiolimiter** : Rate limiting per-host (1.0 req/sec)
- **feedparser** : Parsing RSS/Atom
- **BeautifulSoup4** : HTML parsing
- **html5lib** : HTML5 parser
- **lxml** : XML/HTML parser (backend BeautifulSoup)
- **readability-lxml** : Extraction contenu article

#### **Intelligence Artificielle**
- **openai** : Client OpenAI-compatible (utilisé avec Groq)
  - Base URL: `https://api.groq.com/openai/v1`
  - Model: `llama-3.1-8b-instant`
- **sentence-transformers** : Embeddings sémantiques
  - Model local: `all-MiniLM-L6-v2` (384 dimensions)
- **scikit-learn** : Calcul similarité cosine

#### **Data & Storage**
- **SQLite 3** : Base de données locale (veille.db)
- **Pydantic** : Validation configuration YAML

#### **Utils & CLI**
- **python-dotenv** : Chargement variables .env
- **pyyaml** : Parsing config.yaml
- **tqdm** : Barres de progression CLI

#### **API (Optionnelle)**
- **FastAPI** : REST API development (api_server.py)
- **uvicorn** : ASGI server

#### **Testing**
- **pytest** : Framework de tests
- **pytest-asyncio** : Support tests async
- **pytest-cov** : Coverage reporting

---

### Frontend React

#### **Framework & Build**
- **React** : 19.2.0 (avec Strict Mode)
- **react-dom** : 19.2.0
- **Vite** : 7.2.2 (build tool ultra-rapide)
- **@vitejs/plugin-react** : 5.1.0 (HMR + Fast Refresh)
- **TypeScript** : 5.9.3 (strict mode activé)

#### **Styling**
- **Tailwind CSS** : 3.4.13 (utility-first CSS)
- **@tailwindcss/typography** : 0.5.19 (prose styling pour markdown)
- **autoprefixer** : 10.4.20
- **postcss** : 8.4.33

#### **Features**
- **Fuse.js** : 7.1.0 (fuzzy search)
- **marked** : 17.0.0 (markdown parser + renderer)

#### **Development Tools**
- **ESLint** : 9.39.1
  - **@eslint/js** : 9.39.1
  - **eslint-plugin-react-hooks** : 5.2.0 (rules React hooks)
  - **eslint-plugin-react-refresh** : 0.4.24
  - **typescript-eslint** : 8.46.3
- **globals** : 16.5.0

#### **Types**
- **@types/react** : 19.2.2
- **@types/react-dom** : 19.2.2
- **@types/node** : 24.10.0

---

### Infrastructure & DevOps

#### **Déploiement**
- **GitHub Actions** : CI/CD automatique
  - Workflow backend: `.github/workflows/backend-weekly.yml` (Lundi 06:00 UTC)
  - Workflow frontend: `.github/workflows/deploy-frontend.yml` (on push main)
- **GitHub Pages** : Hosting statique frontend
  - Base path: `/veille/`
  - Source: GitHub Actions

#### **Monitoring & Observability**
- **Logging** : Python logging + logger.py custom (fichier `logs/veille_tech.log`)
- **Métriques** : MetricsCollector custom (feeds_processed, articles_crawled, errors)
- ⚠️ **Monitoring externe** : Aucun (Sentry, Datadog, etc. - manquant)

#### **CI/CD**
- ✅ GitHub Actions backend (weekly cron)
- ✅ GitHub Actions frontend (deploy on push)
- ❌ Tests automatiques en CI (non configuré)
- ❌ Staging environment (non existant)

---

## 3. Structure du Projet

```
veille_tech_crawling/
├── backend/                      # Backend Python
│   ├── .venv/                    # Virtual environment (gitignored)
│   ├── config.yaml               # Configuration centrale (60+ sources)
│   ├── requirements.txt          # Dépendances Python
│   ├── pytest.ini               # Configuration pytest
│   ├── .env                     # Variables d'environnement (gitignored)
│   │
│   ├── main.py                  # 🎯 Orchestrateur pipeline (37 lignes)
│   ├── veille_tech.py           # 📡 Crawling + extraction (668 lignes)
│   ├── classify_llm.py          # 🤖 Classification LLM (248 lignes)
│   ├── analyze_relevance.py     # 📊 Scoring pertinence (581 lignes)
│   ├── summarize_week_llm.py    # 📝 Résumé hebdomadaire (374 lignes)
│   ├── content_classifier.py    # 🎯 Type contenu + filtrage (378 lignes)
│   ├── logger.py                # 📋 Logging structuré (112 lignes)
│   ├── api_server.py            # 🌐 API REST optionnelle (179 lignes)
│   │
│   ├── test_veille_tech.py      # ✅ Tests veille_tech (312 lignes)
│   ├── test_content_classifier.py # ✅ Tests content_classifier (228 lignes)
│   │
│   ├── regenerate_weeks.py      # 🔄 Utilitaire regénération
│   ├── write_week_selection.py  # 📄 Utilitaire écriture sélection
│   ├── generate_summary_from_selection.py
│   ├── convert_to_summary_json.py
│   ├── broken_sources_cleanup.py
│   ├── check_alternate_urls.py
│   ├── fix_sources.py
│   ├── migrate_add_level_fields.py
│   ├── reclassify_tech_levels.py
│   │
│   ├── veille.db                # 🗄️ Base SQLite (gitignored)
│   ├── logs/                    # 📋 Logs d'exécution
│   └── scripts/                 # 🛠️ Scripts shell
│
├── frontend/                    # Frontend React
│   ├── src/
│   │   ├── components/          # Composants React
│   │   │   ├── App.tsx          # Composant principal (221 lignes)
│   │   │   ├── Hero.tsx         # Header + sélecteur semaine
│   │   │   ├── Overview.tsx     # Aperçu markdown
│   │   │   ├── ContentTypeTabs.tsx # Onglets Technical/REX
│   │   │   ├── SearchBar.tsx    # Barre de recherche
│   │   │   ├── CategoryFilter.tsx # Filtres catégories
│   │   │   ├── SectionCard.tsx  # Conteneur catégorie
│   │   │   ├── ArticleCard.tsx  # Carte article
│   │   │   ├── Top3.tsx        # Top 3 articles
│   │   │   └── Chip.tsx        # Badge réutilisable
│   │   ├── lib/
│   │   │   ├── parse.ts         # Parsing exports JSON/MD
│   │   │   └── search.ts        # Logique recherche Fuse.js
│   │   ├── main.tsx            # Entry point React
│   │   └── index.css           # Styles Tailwind globaux
│   │
│   ├── public/
│   │   └── export/             # Données copiées (build)
│   │
│   ├── scripts/
│   │   └── copy-export.js      # Copie backend/export → public/export
│   │
│   ├── package.json
│   ├── package-lock.json
│   ├── vite.config.ts          # Config Vite (base: /veille/)
│   ├── tsconfig.json           # TypeScript config
│   ├── tsconfig.app.json
│   ├── tsconfig.node.json
│   ├── tailwind.config.js      # Tailwind config
│   ├── postcss.config.js
│   └── eslint.config.js        # ESLint config
│
├── export/                     # 📤 Exports hebdomadaires
│   ├── categories.json         # Mapping category_key → title
│   ├── weeks.json             # Index semaines + métadonnées
│   ├── search.json            # Index recherche plat
│   ├── latest → 2025w51       # Symlink semaine courante
│   └── 2025w51/               # Semaine ISO
│       ├── digest.json        # Format frontend complet
│       ├── ai_selection.json  # Articles filtrés
│       ├── ai_selection.md
│       ├── ai_summary.md
│       ├── top3.json
│       ├── top3.md
│       └── range.txt          # Plage dates
│
├── .github/
│   └── workflows/
│       ├── backend-weekly.yml  # Crawl Monday 06:00 UTC
│       └── deploy-frontend.yml # Deploy GitHub Pages
│
├── .claude/
│   └── commands/              # Commandes slash Claude Code
│       ├── epct.md
│       └── reverse-engineer.md
│
├── README.md                  # Documentation utilisateur
├── CLAUDE.md                  # Guide Claude Code
└── .gitignore
```

---

## 4. Architecture Applicative

### Pattern Architectural : **Pipeline Séquentiel**

Le backend suit un pattern de pipeline ETL avec 4 étapes indépendantes orchestrées par `main.py` :

```
main.py (subprocess.run orchestration)
  ↓
┌─────────────────────────────────────────────┐
│ PHASE 1: CRAWLING & EXTRACTION              │
│ veille_tech.py                              │
│ ─────────────────────────────────────────── │
│ • Fetch 60+ RSS/Atom feeds (async)          │
│ • Auto-découverte feeds (HTML parsing)      │
│ • Respect robots.txt + rate limiting        │
│ • Extract article content (readability)     │
│ • Filter par path regex + min length        │
│ • Classify par keywords (initial)           │
│ • Detect content_type (technical/rex)       │
│ • Calculate tech_level + marketing_score    │
│ • Deduplication (hash URL+title)            │
│ • Store in SQLite (upsert)                  │
└─────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────┐
│ PHASE 2: LLM CLASSIFICATION                 │
│ classify_llm.py                             │
│ ─────────────────────────────────────────── │
│ • Read uncategorized articles                │
│ • Call Groq API (llama-3.1-8b-instant)      │
│ • Prompt with 8 categories description      │
│ • Parse JSON response {category, confidence}│
│ • Update DB (category_key, llm_classified)  │
│ • Rate limit: 30 req/min                    │
└─────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────┐
│ PHASE 3: RELEVANCE SCORING & SELECTION      │
│ analyze_relevance.py                        │
│ ─────────────────────────────────────────── │
│ • Load all articles of week                  │
│ • Calculate components:                      │
│   - semantic_score (55%): embeddings cosine  │
│   - source_weight (20%): reputation          │
│   - quality_score (15%): length + code       │
│   - tech_score (10%): keywords               │
│ • Combine → final_score [0-100]             │
│ • Filter by threshold (per category)         │
│ • Diversity filter (max 2 per source/cat)   │
│ • Export: ai_selection.json + top3.json     │
│ • Create indexes: categories, weeks, search │
│ • Symlink export/latest                     │
└─────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────┐
│ PHASE 4: WEEKLY SUMMARY GENERATION          │
│ summarize_week_llm.py                       │
│ ─────────────────────────────────────────── │
│ • Read ai_selection.json                    │
│ • Build markdown context (grouped by cat)   │
│ • Call Groq LLM with structured prompt      │
│ • Parse response (overview + sections)       │
│ • Post-process markdown (normalize)         │
│ • Export: digest.json + digest.md           │
└─────────────────────────────────────────────┘
  ↓
Git commit + push → Trigger frontend deploy
```

### Flux de Données Complet

```
RSS Feeds (60+ sources config.yaml)
  ↓
veille_tech.py → SQLite items table
  ↓
classify_llm.py → Update category_key
  ↓
analyze_relevance.py → Calculate scores + Filter
  ↓
summarize_week_llm.py → Generate digest
  ↓
export/<YYYYwWW>/digest.json
  ↓
Frontend React → Load + Display
  ↓
User (GitHub Pages)
```

---

## 5. Base de Données

### SQLite Schema (`veille.db`)

#### **Table `items`**

**Colonnes principales (création initiale) :**
```sql
CREATE TABLE items (
  id TEXT PRIMARY KEY,              -- sha256(url + "||" + title)
  url TEXT NOT NULL,                -- URL article
  title TEXT NOT NULL,              -- Titre article
  summary TEXT,                     -- Résumé court (feed RSS)
  content TEXT,                     -- Contenu complet extrait
  published_ts INTEGER,             -- Timestamp publication (UTC)
  source_name TEXT,                 -- Nom flux RSS
  category_key TEXT,                -- Clé catégorie (ex: "warehouses_engines")
  created_ts INTEGER NOT NULL       -- Timestamp crawl (UTC)
);

CREATE INDEX idx_items_cat_pub
  ON items(category_key, published_ts DESC);
```

**Colonnes ajoutées par migrations :**

```sql
-- classify_llm.py:
llm_classified INTEGER DEFAULT 0,   -- 0=non traité, 1=classé LLM
original_category_key TEXT,         -- Catégorie avant LLM

-- analyze_relevance.py:
semantic_score REAL,                -- Score embeddings (0-100)
source_weight REAL,                 -- Poids source (0-100)
quality_score REAL,                 -- Score qualité (0-100)
tech_score REAL,                    -- Score tech keywords (0-100)
final_score INTEGER,                -- Score final (0-100)

-- veille_tech.py + content_classifier.py (Phase 1):
content_type TEXT DEFAULT 'technical', -- "technical" | "rex"
tech_level TEXT DEFAULT 'intermediate', -- "beginner" | "intermediate" | "advanced"
marketing_score INTEGER DEFAULT 0,  -- Score marketing (0-100)
is_excluded INTEGER DEFAULT 0,      -- Flag exclusion anti-bruit
exclusion_reason TEXT,              -- "beginner_content" | "promotional_content" | ...

-- Legacy/debug:
llm_score INTEGER,                  -- Score LLM (deprecated)
llm_notes TEXT                      -- Notes LLM debug
```

**Index supplémentaires :**
```sql
CREATE INDEX idx_items_content_type ON items(content_type);
CREATE INDEX idx_items_final_score ON items(final_score DESC);
```

#### **Statistiques Typiques**

- **Taille DB** : ~50-100 MB (après plusieurs mois)
- **Articles par semaine** : ~500-1000 crawlés, ~50-100 sélectionnés
- **Retention** : Indéfinie (pas de purge automatique)

---

## 6. API & Endpoints

### API FastAPI (Optionnelle - Development)

**Fichier** : `api_server.py` (179 lignes)

**Endpoints** :

| Méthode | Path | Description |
|---------|------|-------------|
| GET | `/api/weeks` | Liste toutes les semaines disponibles |
| GET | `/api/week/{week}/sections` | Articles par catégorie pour une semaine |
| GET | `/api/week/{week}/top3` | Top 3 articles de la semaine |
| GET | `/api/week/latest` | Semaine courante (via symlink) |

**CORS** :
- Autorise : `http://localhost:5173` (dev)
- Autorise : `https://*.github.io` (GitHub Pages)

**Note Importante** :
L'API n'est **pas utilisée en production**. Le frontend consomme directement les fichiers statiques JSON depuis `export/`.

---

## 7. Standards de Code

### Backend Python

**Conventions :**
- **Modules** : `snake_case.py`
- **Fonctions** : `snake_case()`
- **Classes** : `PascalCase`
- **Constantes** : `UPPER_CASE`
- **Type hints** : Utilisés partout (Python 3.11+)
- **Docstrings** : Français, format simple
- **Imports** : Groupés (stdlib → tiers → local)

**Exemple :**
```python
from typing import List, Optional
import asyncio

def week_bounds(
    tz_name: str = "Europe/Paris",
    week_offset: int = 0
) -> tuple[int, int, str, str, str]:
    """Calcule les bornes de la semaine ISO.

    Returns:
        (start_ts_utc, end_ts_utc, week_label, start_str, end_str)
    """
    ...
```

**Logging :**
```python
logger.info("Processing feed", feed=feed_name, articles=count)
logger.error("Failed to fetch", url=url, error=str(e))
```

**Error Handling :**
- Try/except dans Fetcher et async calls
- Graceful degradation (errors logged, pas de crash)

---

### Frontend React/TypeScript

**Conventions :**
- **Composants** : `PascalCase.tsx`
- **Utils** : `camelCase.ts`
- **Types** : `PascalCase` (interfaces/types)
- **Props** : Interface avec suffix `Props` ou inline
- **Hooks** : Prefix `use` (React convention)

**Style :**
- Tailwind utility-first
- Responsive : mobile-first (`sm:`, `md:` breakpoints)
- Semantic HTML (`<header>`, `<main>`, `<section>`, `<article>`)
- Accessibility : `aria-*`, `alt`, `htmlFor`, focus rings

**TypeScript** :
```typescript
interface ArticleCardProps {
  title: string;
  url?: string;
  source?: string;
  date?: string;
  score?: number | string;
  tech_level?: 'beginner' | 'intermediate' | 'advanced';
  marketing_score?: number;
  className?: string;
}

export function ArticleCard({ title, url, source, ... }: ArticleCardProps) {
  ...
}
```

**React Patterns :**
- Functional components (pas de class)
- Hooks : `useState`, `useEffect`, `useMemo`
- Props drilling (pas de Context/Redux pour ce projet)
- Conditional rendering : `{condition && <Component />}`

---

## 8. Sécurité

### Implémenté ✅

- [x] **Variables d'environnement** : API keys via `.env` (gitignored)
- [x] **robots.txt respect** : RobotsCache avec urllib.robotparser
- [x] **Rate limiting** : AsyncLimiter per-host (1.0 req/sec)
- [x] **User-Agent** : Custom UA avec URL projet
- [x] **Deduplication** : Hash (URL + titre) pour éviter duplicates
- [x] **HTTPS upgrade** : Auto-upgrade HTTP → HTTPS
- [x] **Sanitization HTML** : readability + BeautifulSoup
- [x] **TypeScript strict** : Typage strict frontend
- [x] **CORS** : Configuré pour localhost + GitHub Pages

### Manquant ⚠️

- [ ] **Secrets hardcodés** : ❌ Aucun secret détecté en dur (bonne pratique)
- [ ] **Input validation** : ⚠️ Validation Pydantic config.yaml uniquement
- [ ] **Rate limiting API** : ❌ Pas de rate limit sur api_server.py (mais non prod)
- [ ] **HTTPS enforcement** : ❌ Pas de redirection forcée
- [ ] **Content Security Policy** : ❌ Aucun header CSP
- [ ] **Dependency scanning** : ❌ Pas de Dependabot/Snyk
- [ ] **Secrets scanning** : ❌ Pas de GitHub Secret Scanning

**Recommandations P1 :**
1. Activer Dependabot (GitHub) pour scans CVE
2. Ajouter CSP headers si API déployée en prod
3. Audit sécurité OWASP Top 10

---

## 9. Performance

### Optimisations Implémentées ✅

**Backend :**
- [x] **Asyncio** : Crawling async (8 feeds parallèles)
- [x] **Connection pooling** : aiohttp TCPConnector
- [x] **Rate limiting intelligent** : Per-host (évite ban)
- [x] **Embeddings caching** : Global `_model_semantic`, `_profile_embedding`
- [x] **SQLite indexing** : Index sur (category_key, published_ts)
- [x] **Batch processing** : Classif LLM par batch async

**Frontend :**
- [x] **Vite build** : Rollup optimisé + code splitting
- [x] **useMemo** : Filtrage + parsing memoized
- [x] **Lazy loading** : Images favicons `loading="lazy"`
- [x] **Static files** : Pas d'API calls (JSON statiques)
- [x] **Tailwind purge** : CSS unused purgé au build

### Problèmes Identifiés ⚠️

**Backend :**
- ⚠️ **Embeddings recalcul** : Pas de cache Redis (recalculé chaque run)
- ⚠️ **LLM calls séquentiels** : 30 req/min max (Groq limite)
- ⚠️ **SQLite contention** : Pas de WAL mode (single-writer)

**Frontend :**
- ⚠️ **Large JSON files** : digest.json peut être > 500 KB
- ⚠️ **No virtualization** : Toutes les cartes rendues (pas de react-window)
- ⚠️ **No pagination** : Toutes les semaines chargées d'un coup

**Recommandations P2 :**
1. Redis cache pour embeddings (évite recalcul)
2. SQLite WAL mode pour meilleure concurrence
3. Pagination frontend (react-window pour long lists)
4. Compress JSON exports (gzip)

---

## 10. Tests

### Configuration Pytest

**Fichier** : `pytest.ini`

```ini
[pytest]
testpaths = .
python_files = test_*.py
python_classes = Test*
python_functions = test_*

addopts = -v --tb=short --strict-markers --disable-warnings

markers =
    slow: tests lents
    integration: tests d'intégration
    unit: tests unitaires

asyncio_mode = auto
```

### Tests Existants

**Fichiers de tests :**
- `test_veille_tech.py` (312 lignes) - 20+ tests
- `test_content_classifier.py` (228 lignes) - 17 tests

**Total : 37 tests**

**Coverage :**
```bash
pytest --cov=. --cov-report=html
```
- ⚠️ Coverage actuel : **Non mesuré régulièrement**
- 🎯 Coverage cible : **> 80%**

**Marqueurs utilisés :**
- `@pytest.mark.unit` : Tests rapides (< 1s)
- `@pytest.mark.integration` : Tests avec I/O externe
- `@pytest.mark.slow` : Tests long-running (> 10s)

**Ce qui est testé :**
- ✅ `classify()` : Classification par keywords
- ✅ `week_bounds()` : Calcul semaines ISO
- ✅ `normalize_ts()` : Normalisation timestamps
- ✅ `detect_content_type()` : Détection technical/rex
- ✅ `calculate_marketing_score()` : Score marketing
- ✅ `calculate_technical_level()` : Niveau technique

**Ce qui manque :**
- ❌ Tests LLM calls (mocking Groq API)
- ❌ Tests embeddings (mocking sentence-transformers)
- ❌ Tests end-to-end pipeline complet
- ❌ Tests frontend (Vitest/Jest)
- ❌ Tests E2E (Playwright)

---

## 11. Dette Technique Identifiée

### P0 - Critique (À corriger immédiatement)

**Aucune dette critique détectée** ✅

Le code est globalement de bonne qualité, bien structuré et documenté.

### P1 - Haute (À corriger sous 1-2 sprints)

#### [DEBT-001] Absence de tests frontend
**Impact :** Risque de régressions UI non détectées
**Estimation :** 13 SP
**Action :**
- Setup Vitest
- Tests composants critiques (App, SearchBar, CategoryFilter)
- Tests E2E Playwright (search + filter flows)

#### [DEBT-002] Pas de CI/CD pour tests
**Impact :** Tests manuels uniquement
**Estimation :** 5 SP
**Action :**
- Ajouter step pytest dans `.github/workflows/backend-weekly.yml`
- Fail si tests échouent
- Coverage report upload (Codecov)

#### [DEBT-003] Embeddings non cachés (Redis)
**Impact :** Performance (recalcul chaque run)
**Estimation :** 8 SP
**Action :**
- Setup Redis (Docker ou cloud)
- Cache embeddings par hash(content)
- TTL 30 jours

#### [DEBT-004] Monitoring/Observability manquant
**Impact :** Bugs production non détectés
**Estimation :** 8 SP
**Action :**
- Intégrer Sentry (backend + frontend)
- Alertes Slack si erreurs
- Dashboard métriques (articles/semaine, sources down, etc.)

### P2 - Moyenne (Backlog)

#### [DEBT-005] Pas de staging environment
**Impact :** Test en prod uniquement
**Estimation :** 5 SP

#### [DEBT-006] SQLite single-writer (pas de WAL)
**Impact :** Performance DB limitée
**Estimation :** 2 SP

#### [DEBT-007] Pas de Dependabot (CVE scanning)
**Impact :** Dépendances vulnérables non détectées
**Estimation :** 1 SP

#### [DEBT-008] Frontend JSON non paginé
**Impact :** Performance si > 100 semaines
**Estimation :** 5 SP

---

## 12. Ce qui Manque (Gaps)

### Infrastructure

- [ ] **Monitoring** : Sentry, Datadog, New Relic
- [ ] **Staging** : Environnement de test pré-prod
- [ ] **Backup strategy** : Backup SQLite automatique
- [ ] **Rollback strategy** : Version antérieure si deploy fail
- [ ] **Health checks** : Endpoint `/health` pour monitoring

### Code

- [ ] **Tests frontend** : Coverage 0% actuellement
- [ ] **Tests E2E** : Playwright flows complets
- [ ] **CI tests** : pytest + vitest automatiques
- [ ] **API documentation** : Swagger/OpenAPI (si API prod)
- [ ] **Error tracking** : Sentry integration

### Sécurité

- [ ] **Dependabot** : Scans CVE automatiques
- [ ] **Secret scanning** : GitHub Secret Scanning
- [ ] **CSP headers** : Content Security Policy
- [ ] **Rate limiting** : Sur API si prod
- [ ] **HTTPS enforcement** : Redirection forcée

### Performance

- [ ] **Redis cache** : Embeddings + LLM responses
- [ ] **CDN** : CloudFront/Cloudflare pour assets
- [ ] **Image optimization** : WebP + lazy loading avancé
- [ ] **Bundle analysis** : Webpack Bundle Analyzer

### Features

- [ ] **Mode sombre** : Dark mode toggle
- [ ] **Export PDF** : Digest en PDF
- [ ] **Notifications** : Slack/email hebdomadaire
- [ ] **Personnalisation** : Filtres sauvegardés par user
- [ ] **Analytics** : Tendances, stats, graphiques

---

## 13. Score Santé Globale : 73/100

| Critère | Score | Commentaire |
|---------|-------|-------------|
| **Architecture** | 18/20 | Pipeline clair, modulaire, bien séparé |
| **Tests** | 10/20 | Backend partiellement testé, frontend 0% |
| **Documentation** | 18/20 | README excellent, CLAUDE.md complet |
| **Sécurité** | 14/20 | Bonnes pratiques, mais monitoring manquant |
| **Performance** | 13/20 | Asyncio bien utilisé, manque caching |
| **TOTAL** | **73/100** | **Bon - Quelques améliorations nécessaires** |

---

## 14. Points d'Extension Future

### Modularité

Le code est conçu pour être facilement extensible :

1. **Nouveaux LLM providers** : Abstraction OpenAI-compatible (Groq, OpenAI, Ollama)
2. **Nouveaux modèles embeddings** : Configurable (actuellement hardcodé)
3. **Nouveaux scoring components** : Ajouter freshness_score, engagement_score, etc.
4. **Nouveaux storage backends** : PostgreSQL au lieu de SQLite
5. **Nouveaux export formats** : PDF, HTML email, Notion, etc.
6. **Nouveaux workflows** : Dbt, Airflow pour orchestration avancée

### Intégrations Possibles

- **Slack bot** : Commande `/veille` pour digest
- **Email newsletter** : Envoi automatique hebdomadaire
- **API publique** : Exposer l'API pour tiers
- **Webhook** : Notifier services externes (Zapier, etc.)
- **RSS feed** : Générer RSS du digest

---

## 15. Conclusion

L'architecture de **Veille Tech Crawling** est **solide, moderne et bien conçue**. Le pipeline backend est **modulaire et asynchrone**, le frontend est **type-safe et performant**, et le déploiement est **automatisé via GitHub Actions**.

**Forces principales :**
- Pipeline ETL clair en 4 phases
- Scoring multi-critères sophistiqué
- Interface utilisateur moderne et responsive
- Déploiement automatique et fiable
- Code bien documenté et structuré

**Axes d'amélioration prioritaires :**
1. Tests frontend (Vitest + Playwright)
2. CI/CD pour tests automatiques
3. Monitoring avec Sentry
4. Cache Redis pour embeddings

Le projet est **prêt pour la production** et déjà déployé avec succès. Les améliorations identifiées sont des **optimisations incrémentales** plutôt que des problèmes bloquants.
