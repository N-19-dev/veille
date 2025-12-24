# 🧪 CI/CD & Tests Automatiques

**Statut** : ✅ Implémenté (Sprint 3 - 5 SP)
**Date** : Décembre 2024

---

## 🎯 Objectif

Garantir la qualité du code avec des tests automatiques exécutés en CI/CD :
- Backend : Tests unitaires et intégration avec **pytest**
- Frontend : Linting avec **ESLint**
- Coverage reporting avec **Codecov**
- Fail automatique si tests échouent

---

## 📊 Vue d'ensemble des Workflows

### 1. **Backend Tests** (`test-backend.yml`)

**Trigger** :
- Sur Pull Request modifiant `backend/**`
- Sur Push vers `main` modifiant `backend/**`
- Manuel via `workflow_dispatch`

**Steps** :
1. ✅ Setup Python 3.11
2. ✅ Install dependencies (requirements.txt)
3. ✅ Run pytest with coverage (`pytest --cov`)
4. ✅ Upload coverage to Codecov
5. ✅ Upload coverage artifact (30 days retention)

**Durée** : ~2-3 minutes
**Fail si** : Un test pytest échoue

---

### 2. **Backend Weekly** (`backend-weekly.yml`)

**Trigger** :
- Tous les lundis à 06:00 UTC (cron)
- Manuel via `workflow_dispatch`

**Steps** :
1. ✅ Setup Python 3.11
2. ✅ Install dependencies
3. **✅ Run pytest** ← NOUVEAU (Sprint 3)
4. ✅ Upload coverage to Codecov
5. ✅ Run backend pipeline (crawl + analyze + export)
6. ✅ Commit export files
7. ✅ Trigger frontend deployment

**Durée** : ~10-15 minutes
**Fail si** : Tests pytest échouent → Pipeline n'est PAS exécuté

---

### 3. **Frontend Deploy** (`deploy-frontend.yml`)

**Trigger** :
- Sur Push vers `main`
- Déclenché par `backend-weekly.yml`
- Manuel via `workflow_dispatch`

**Steps** :
1. ✅ Setup Node.js 20
2. ✅ Install dependencies (npm ci)
3. **✅ Run ESLint** ← NOUVEAU (Sprint 3)
4. ✅ Copy export into public
5. ✅ Build with Vite
6. ✅ Deploy to GitHub Pages

**Durée** : ~3-5 minutes
**Fail si** : ESLint trouve des erreurs → Build n'est PAS déployé

---

## 🧪 Tests Backend (pytest)

### Structure des Tests

```
backend/
├── test_llm_provider.py           # Tests LLM abstraction (14 tests)
├── test_veille_tech.py            # Tests crawling
├── test_content_classifier.py     # Tests classification contenu
├── test_sentry.py                 # Tests intégration Sentry
├── test_marketing_penalty.py      # Tests pénalité marketing
└── requirements.txt               # pytest, pytest-asyncio, pytest-cov
```

### Exécuter les Tests Localement

```bash
cd backend
source .venv/bin/activate

# Tous les tests
pytest

# Avec coverage
pytest --cov=. --cov-report=term --cov-report=html

# Tests spécifiques
pytest test_llm_provider.py -v

# Avec markers
pytest -m unit          # Tests unitaires
pytest -m integration   # Tests d'intégration
```

### Coverage Report

Après exécution avec `--cov-report=html`, ouvrir :
```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

---

## 🎨 Linting Frontend (ESLint)

### Configuration

```json
// frontend/.eslintrc.json
{
  "extends": [
    "eslint:recommended",
    "plugin:react/recommended",
    "plugin:@typescript-eslint/recommended"
  ]
}
```

### Exécuter Localement

```bash
cd frontend

# Lint check
npm run lint

# Fix auto
npm run lint -- --fix
```

---

## 📈 Code Coverage (Codecov)

### Setup

1. **Créer compte** sur https://codecov.io
2. **Connecter le repo** GitHub
3. **Récupérer le token** : Settings → Copy Token
4. **Ajouter secret GitHub** :
   - Repo → Settings → Secrets → Actions
   - Name: `CODECOV_TOKEN`
   - Value: (coller le token)

### Badge

Badge dans `README.md` :
```markdown
[![codecov](https://codecov.io/gh/USERNAME/veille_tech_crawling/branch/main/graph/badge.svg)](https://codecov.io/gh/USERNAME/veille_tech_crawling)
```

**Note** : Remplacer `USERNAME` par votre username GitHub.

### Visualisation

- **Dashboard** : https://codecov.io/gh/USERNAME/veille_tech_crawling
- **Coverage par fichier** : Voir quels fichiers sont bien testés
- **Diff coverage** : Coverage des nouvelles lignes dans PR
- **Trends** : Évolution du coverage au fil du temps

---

## ✅ Bonnes Pratiques

### 1. **Tests Before Merge**

Créer une Pull Request déclenche automatiquement `test-backend.yml`.
**Ne jamais merger** si les tests échouent.

### 2. **Coverage Minimum**

Objectif : **> 70% coverage**
- Backend critique (LLM, scoring) : **> 80%**
- Utils et helpers : **> 60%**

### 3. **Fast Feedback**

Les tests doivent être **rapides** :
- Tests unitaires : < 1s chacun
- Suite complète : < 3 minutes

Utiliser `pytest -m unit` pour tests rapides.

### 4. **Markers**

Organiser les tests avec markers :
```python
@pytest.mark.unit
def test_llm_provider_creation():
    ...

@pytest.mark.integration
def test_full_pipeline():
    ...

@pytest.mark.slow
def test_heavy_computation():
    ...
```

Exécuter :
```bash
pytest -m "unit and not slow"  # Tests unitaires rapides seulement
```

---

## 🚨 Troubleshooting

### Tests échouent en CI mais passent localement

**Cause possible** :
- Différence d'environnement (Python 3.11 vs 3.13)
- Variables d'environnement manquantes
- Fichiers non commités (fixtures, mocks)

**Solution** :
1. Vérifier Python version : `python --version`
2. Vérifier env vars dans workflow YAML
3. Commit tous les fichiers de test

### Coverage ne s'upload pas

**Vérifier** :
1. Secret `CODECOV_TOKEN` existe dans GitHub
2. Workflow a permission `contents: read`
3. Fichier `coverage.xml` est généré : `ls backend/coverage.xml`

**Debug** :
```yaml
- name: Debug coverage file
  run: |
    ls -la backend/
    cat backend/coverage.xml
```

### ESLint bloque le deploy

**Cause** : Erreurs de linting dans le frontend

**Solutions** :
```bash
# Voir les erreurs
cd frontend && npm run lint

# Fix auto
npm run lint -- --fix

# Désactiver temporairement (déconseillé)
# Modifier deploy-frontend.yml :
npm run lint || echo "Linting failed but continuing"
```

---

## 📊 Métriques & KPIs

**Objectifs Sprint 3** :

| Métrique | Objectif | Actuel |
|----------|----------|--------|
| **Coverage backend** | > 70% | À mesurer après setup Codecov |
| **Tests backend** | 100% passants | ✅ 14/14 (test_llm_provider.py) |
| **Linting frontend** | 0 erreurs | ✅ Passe |
| **CI run time** | < 5 min | ✅ ~3 min |
| **Fail rate** | < 5% | À surveiller |

---

## 🔜 Améliorations Futures

### Tests Frontend (Vitest)

**Actuellement** : Seulement ESLint
**À implémenter** :

1. **Install vitest** :
```bash
cd frontend
npm install -D vitest @vitest/ui @testing-library/react @testing-library/user-event
```

2. **Config vitest.config.ts** :
```typescript
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html']
    }
  }
})
```

3. **Ajouter script** dans `package.json` :
```json
"scripts": {
  "test": "vitest",
  "test:coverage": "vitest --coverage"
}
```

4. **Créer tests** :
```typescript
// src/components/__tests__/Hero.test.tsx
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import Hero from '../Hero'

describe('Hero', () => {
  it('renders title', () => {
    render(<Hero weekLabel="2025w51" dateRange="Dec 16 - Dec 22" weeks={[]} onWeekChange={() => {}} />)
    expect(screen.getByText(/Veille Tech/i)).toBeInTheDocument()
  })
})
```

5. **Update workflow** :
```yaml
- name: Run tests with vitest
  run: npm run test:coverage

- name: Upload coverage
  uses: codecov/codecov-action@v4
  with:
    file: ./frontend/coverage/coverage-final.json
    flags: frontend
```

**Effort estimé** : 2-3 SP

---

## 📚 Ressources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov plugin](https://pytest-cov.readthedocs.io/)
- [Codecov documentation](https://docs.codecov.com/)
- [GitHub Actions workflow syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [ESLint rules](https://eslint.org/docs/latest/rules/)

---

**✅ Sprint 3 CI/CD Tests : COMPLETÉ**

**Deliverable** : Tests automatiques en CI qui bloquent le merge/deploy si échec ✅
