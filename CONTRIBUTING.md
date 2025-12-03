# 🤝 Guide de contribution

Merci de votre intérêt pour contribuer à ce projet de veille technologique ! Voici comment participer.

## 📋 Table des matières

- [Code de conduite](#code-de-conduite)
- [Comment contribuer](#comment-contribuer)
- [Structure du projet](#structure-du-projet)
- [Développement local](#développement-local)
- [Standards de code](#standards-de-code)
- [Tests](#tests)
- [Pull Requests](#pull-requests)

## Code de conduite

Ce projet adhère à un code de conduite standard. En participant, vous vous engagez à maintenir un environnement respectueux et inclusif.

## Comment contribuer

### Types de contributions

Nous acceptons plusieurs types de contributions :

1. **Rapports de bugs** : Signalez les problèmes via les issues GitHub
2. **Suggestions de fonctionnalités** : Proposez des améliorations
3. **Ajout de sources** : Suggérez de nouvelles sources RSS/Atom
4. **Code** : Corrigez des bugs ou implémentez de nouvelles fonctionnalités
5. **Documentation** : Améliorez la documentation ou les exemples

### Créer une issue

Avant de soumettre une issue, vérifiez qu'elle n'existe pas déjà.

**Pour un bug :**
- Titre clair et descriptif
- Étapes pour reproduire
- Comportement attendu vs comportement observé
- Environnement (OS, Python/Node version)
- Logs ou captures d'écran si pertinent

**Pour une fonctionnalité :**
- Titre clair
- Description du problème que ça résout
- Solution proposée
- Alternatives envisagées

## Structure du projet

```
veille_tech_crawling/
├── backend/              # Pipeline Python
│   ├── veille_tech.py    # Crawling principal
│   ├── classify_llm.py   # Classification
│   ├── analyze_relevance.py  # Scoring
│   ├── summarize_week_llm.py # Résumés
│   ├── logger.py         # Logging structuré
│   ├── test_*.py         # Tests unitaires
│   └── config.yaml       # Configuration
│
├── frontend/             # Interface React
│   ├── src/
│   │   ├── components/   # Composants UI
│   │   └── lib/          # Utilitaires
│   └── public/
│
└── .github/workflows/    # CI/CD
```

## Développement local

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Tests
pytest -v

# Linting (optionnel)
pip install black pylint
black .
pylint *.py
```

### Frontend

```bash
cd frontend
npm install

# Dev server
npm run dev

# Tests (à implémenter)
npm test

# Linting
npm run lint
```

## Standards de code

### Python (Backend)

- **Style** : PEP 8
- **Formatage** : Black (line length: 100)
- **Type hints** : Utiliser Pydantic pour les modèles
- **Docstrings** : Google style

```python
def classify(title: str, summary: str, categories: List[Category]) -> Optional[str]:
    """
    Classifie un article dans une catégorie.

    Args:
        title: Titre de l'article
        summary: Résumé de l'article
        categories: Liste des catégories possibles

    Returns:
        Clé de la catégorie ou None si pas de match
    """
    # Implementation...
```

### TypeScript/React (Frontend)

- **Style** : ESLint + Prettier
- **Composants** : Function components avec hooks
- **Props** : Interfaces TypeScript explicites
- **CSS** : Tailwind CSS uniquement

```tsx
interface MyComponentProps {
  title: string;
  onAction: (id: string) => void;
}

export default function MyComponent({ title, onAction }: MyComponentProps) {
  // Implementation...
}
```

### Commits

Format des messages de commit :

```
type(scope): description courte

[Description détaillée optionnelle]

[Footer optionnel: references, breaking changes]
```

**Types** :
- `feat`: Nouvelle fonctionnalité
- `fix`: Correction de bug
- `docs`: Documentation
- `style`: Formatage, point-virgules manquants, etc.
- `refactor`: Refactoring du code
- `test`: Ajout ou modification de tests
- `chore`: Tâches de maintenance

**Exemples** :
```
feat(backend): add rate limiting per host
fix(frontend): search bar not clearing on week change
docs(readme): update installation instructions
```

## Tests

### Backend

Nous utilisons pytest. Tous les tests doivent passer avant un merge.

```bash
# Lancer tous les tests
pytest -v

# Tests spécifiques
pytest test_veille_tech.py -v

# Coverage
pytest --cov=. --cov-report=html
```

**Écrire des tests** :
- Un fichier `test_*.py` par module
- Noms de fonctions : `test_<feature>_<scenario>`
- Utiliser des fixtures pour les données répétitives
- Viser au moins 70% de couverture

### Frontend

(À implémenter : Jest + React Testing Library)

## Pull Requests

### Processus

1. **Fork** le repo
2. **Créez une branche** : `git checkout -b feature/ma-fonctionnalité`
3. **Committez** vos changements (suivre le format de commit)
4. **Testez** : assurez-vous que tous les tests passent
5. **Push** : `git push origin feature/ma-fonctionnalité`
6. **Ouvrez une PR** vers `main`

### Checklist PR

Avant de soumettre, vérifiez :

- [ ] Les tests passent (`pytest` + `npm test`)
- [ ] Le code suit les standards (linting)
- [ ] La documentation est à jour
- [ ] Les commits suivent le format
- [ ] Pas de secrets/credentials dans le code
- [ ] Les changements sont testés localement

### Review

Soyez patient, les reviews peuvent prendre quelques jours. Attendez-vous à :
- Des questions de clarification
- Des suggestions d'amélioration
- Des demandes de tests supplémentaires

C'est normal et constructif !

## Ajout de sources RSS

Pour ajouter une nouvelle source de veille :

1. Modifiez `backend/config.yaml`
2. Ajoutez dans la section `sources` :

```yaml
sources:
  - name: "Nom de la source"
    url: "https://example.com/feed.xml"
```

3. Testez localement :

```bash
cd backend
python veille_tech.py --config config.yaml
```

4. Vérifiez que la source est bien crawlée
5. Soumettez une PR avec une description de la source

## Ajout de catégories

Pour ajouter une nouvelle catégorie :

1. Modifiez `backend/config.yaml`
2. Ajoutez dans la section `categories` :

```yaml
categories:
  - key: "ma_categorie"
    title: "🎯 Ma Catégorie"
    keywords: ["keyword1", "keyword2", "keyword3"]
```

3. Ajoutez un seuil dans `category_thresholds` :

```yaml
category_thresholds:
  ma_categorie: 55
```

4. Testez la classification localement
5. Soumettez une PR

## Questions ?

- Ouvrez une issue avec le tag `question`
- Rejoignez les discussions GitHub
- Consultez la [documentation complète](README.md)

Merci de contribuer ! 🙏
