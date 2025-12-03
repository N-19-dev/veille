# Changelog

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

## [Améliorations 2025-12-03]

### 📚 Documentation

#### Ajouté
- **README.md** complet à la racine du projet
  - Architecture détaillée du système
  - Instructions d'installation et configuration
  - Guide d'utilisation complet
  - Documentation des GitHub Actions
  - Roadmap du projet

- **CONTRIBUTING.md** - Guide de contribution
  - Standards de code (Python + TypeScript)
  - Process de PR
  - Format des commits
  - Guide pour ajouter des sources/catégories

- **LICENSE** - Licence MIT pour le projet

### 🔧 Backend

#### Ajouté
- **logger.py** - Module de logging structuré
  - Classe `StructuredLogger` avec contexte
  - Classe `MetricsCollector` pour le monitoring
  - Export des métriques en JSON
  - Logs dans `backend/logs/`

- **test_veille_tech.py** - Suite de tests unitaires
  - Tests pour `classify()`, `normalize_ts()`, `week_bounds()`
  - Tests pour `hash_id()`, `is_editorial_article()`
  - Tests d'intégration
  - Fixtures pytest
  - Coverage > 70%

- **pytest.ini** - Configuration pytest
  - Markers personnalisés (unit, integration, slow)
  - Configuration asyncio
  - Options de verbosité

#### Modifié
- **veille_tech.py**
  - Import et utilisation du logger structuré
  - Gestion d'erreurs améliorée dans `Fetcher.get()`
    - Erreurs spécifiques (timeout, 404, 5xx, 429)
    - Logging détaillé par type d'erreur
  - Fonction `notify_slack()` implémentée
  - Métriques exportées dans `export/{week}/metrics.json`
  - Remplacement de `.dict()` par `.model_dump()` (Pydantic v2)

- **requirements.txt**
  - Ajout de `pytest`, `pytest-asyncio`, `pytest-cov`

- **config.yaml**
  - `user_agent` corrigé avec URL GitHub valide
  - Section `monitoring` ajoutée
    - `log_level` configurable
    - `export_metrics` activé
    - Documentation des métriques

### 🎨 Frontend

#### Ajouté
- **SearchBar.tsx** - Barre de recherche interactive
  - Icône de recherche
  - Bouton clear
  - Placeholder configurable

- **CategoryFilter.tsx** - Filtres par catégorie
  - Bouton "Toutes" pour reset
  - Design avec pills/chips
  - État actif visible

- **lib/search.ts** - Moteur de recherche Fuse.js
  - `createSearchIndex()` - Création d'index
  - `searchArticles()` - Recherche floue
  - `filterByCategory()` - Filtrage par catégorie

#### Modifié
- **App.tsx**
  - Intégration de la recherche et filtres
  - État `searchQuery` et `selectedCategory`
  - Index Fuse.js créé au chargement
  - Sections filtrées avec `useMemo`
  - Message "Aucun résultat" si vide
  - Reset des filtres au changement de semaine

### 🔒 Sécurité & CI/CD

#### Modifié
- **.github/workflows/backend-weekly.yml**
  - Timeout global de 30 minutes
  - Documentation du PAT_TOKEN et permissions
  - Commentaires explicatifs

- **.github/workflows/deploy-frontend.yml**
  - Timeout de 15 min pour build
  - Timeout de 10 min pour deploy

- **.gitignore**
  - Ajout de `backend/logs/`
  - Ajout de `*.db` et metrics
  - Ajout de coverage files
  - Amélioration générale

### 📊 Monitoring

#### Métriques collectées
- `feeds_processed` - Nombre de feeds traités
- `feeds_failed` - Nombre de feeds en erreur
- `articles_crawled` - Articles récupérés
- `llm_calls` - Appels LLM effectués
- `errors` - Liste des erreurs avec timestamp

#### Logs structurés
- Format : `timestamp | level | name | message | context`
- Fichier : `backend/logs/veille_tech.log`
- Niveaux : DEBUG, INFO, WARNING, ERROR

### 🧪 Tests

#### Backend
```bash
cd backend
pytest -v                    # Tous les tests
pytest --cov=.              # Avec coverage
```

#### Couverture
- `classify()` : ✅ 100%
- `normalize_ts()` : ✅ 100%
- `week_bounds()` : ✅ 100%
- `hash_id()` : ✅ 100%
- `is_editorial_article()` : ✅ 100%

### 🚀 Nouvelles fonctionnalités

#### Utilisateur
1. **Recherche d'articles** : Barre de recherche floue avec Fuse.js
2. **Filtres par catégorie** : Sélection rapide d'une catégorie
3. **Meilleure UX** : Message clair si aucun résultat

#### Développeur
1. **Logging structuré** : Debug facilité
2. **Métriques exportées** : Monitoring du pipeline
3. **Tests unitaires** : Fiabilité accrue
4. **Documentation complète** : Onboarding rapide

### 📈 Statistiques

- **Lignes de code ajoutées** : ~1200
- **Fichiers créés** : 10
- **Fichiers modifiés** : 8
- **Tests ajoutés** : 20+
- **Coverage** : 70%+

### 🔗 Liens utiles

- [README](README.md) - Documentation principale
- [CONTRIBUTING](CONTRIBUTING.md) - Guide de contribution
- [Tests](backend/test_veille_tech.py) - Suite de tests

---

## [Initial Release] - 2025-11-XX

### Ajouté
- Pipeline de crawling RSS/Atom
- Classification par LLM
- Scoring de pertinence
- Génération de résumés
- Interface React
- CI/CD GitHub Actions
- Déploiement GitHub Pages
