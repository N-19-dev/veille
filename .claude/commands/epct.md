---
allowed-tools: Bash(*), WebSearch, Glob, Grep, Read, Task, AskUserQuestion, TodoWrite, Edit, Write
argument-hint: [feature-description] | [--auto-mode]
description: EPCT Workflow - Explore, Plan, Code, Test avec validation utilisateur
model: claude-opus-4-5-20251101
---

# EPCT Workflow: $ARGUMENTS

Ce workflow suit une méthodologie structurée en 4 phases pour garantir une implémentation robuste et réfléchie.

---

## 🔍 Phase 1/4: EXPLORE - Recherche et Analyse du Contexte

### Objectif
Rassembler toutes les informations nécessaires avant de planifier l'implémentation.

### Actions à réaliser

**1. Recherche d'informations externes**
- Utiliser WebSearch pour rechercher des best practices, documentation, et exemples liés à la fonctionnalité demandée
- Identifier les patterns, architectures, et solutions existantes
- Rechercher les pièges courants et les considérations importantes

**2. Exploration du code existant**
- Utiliser Task(subagent_type=Explore) pour explorer la structure du codebase
- Identifier les fichiers, modules, et composants pertinents avec Glob et Grep
- Lire et analyser le code existant avec Read pour comprendre:
  - L'architecture actuelle
  - Les patterns utilisés
  - Les dépendances existantes
  - Les conventions de code
  - Les tests existants

**3. Analyse de la configuration**
- Lire les fichiers de configuration (package.json, config.yaml, .env.example, etc.)
- Identifier les commandes disponibles (scripts npm, pytest, eslint, typescript, etc.)
- Comprendre les dépendances et l'environnement

**4. Synthèse de l'exploration**
Créer un résumé structuré contenant:
- Ce qui existe déjà (fonctionnalités similaires, patterns)
- Ce qui doit être créé/modifié
- Les contraintes techniques identifiées
- Les dépendances nécessaires
- Les tests disponibles dans le projet

### Validation Phase 1

**IMPORTANT**: À la fin de cette phase, vous DEVEZ:
1. Présenter un résumé clair de vos découvertes
2. Demander à l'utilisateur s'il souhaite continuer vers la phase PLAN
3. Proposer d'approfondir certains aspects si nécessaire

**NE PAS passer automatiquement à la phase suivante.**

---

## 📋 Phase 2/4: PLAN - Architecture et Stratégie

### Objectif
Concevoir une solution détaillée et obtenir la validation de l'utilisateur AVANT de coder.

### Actions à réaliser

**1. Proposition d'architecture**
Créer un plan détaillé incluant:
- Les fichiers à créer/modifier (avec chemins exacts)
- L'ordre des modifications
- Les patterns à suivre (basés sur l'exploration)
- Les dépendances à ajouter (si nécessaire)
- Les tests à créer/modifier

**2. Identification des incertitudes**
Utiliser AskUserQuestion pour clarifier:
- Les choix architecturaux (s'il existe plusieurs approches valides)
- Les préférences sur l'implémentation
- Les aspects ambigus de la demande
- Les priorités (MVP vs solution complète)

**PENSEZ PROFONDÉMENT**: Ne pas hésiter à challenger votre propre plan:
- Y a-t-il des edge cases non couverts?
- Cette approche suit-elle les conventions du projet?
- Y a-t-il des risques de régression?
- Cette solution est-elle maintenable?

**3. Utilisation de TodoWrite**
Créer une todo list structurée avec toutes les étapes d'implémentation.

**4. Présentation du plan**
Structurer le plan de façon claire:
```
## Plan d'Implémentation

### Fichiers à modifier
- `path/to/file1.py` : [description des changements]
- `path/to/file2.tsx` : [description des changements]

### Fichiers à créer
- `path/to/new-file.ts` : [description et raison]

### Dépendances
- [nom-package] : [raison]

### Étapes d'implémentation
1. [Étape 1 avec détails]
2. [Étape 2 avec détails]
...

### Tests prévus
- [Description des tests basés sur la config existante]

### Points d'attention
- [Risques identifiés]
- [Décisions architecturales]
```

### Validation Phase 2

**OBLIGATOIRE**: Vous DEVEZ:
1. Demander explicitement validation du plan avec AskUserQuestion
2. Proposer des alternatives si pertinent
3. Poser des questions sur les points incertains
4. **ATTENDRE la confirmation avant de passer au CODE**

Options à proposer:
- ✅ Valider et passer au CODE
- 🔄 Modifier le plan (quels aspects?)
- ❓ Clarifier certains points
- 🛑 Annuler

---

## 💻 Phase 3/4: CODE - Implémentation

### Objectif
Implémenter la solution exactement comme planifié et validé.

### Actions à réaliser

**1. Suivre le plan validé**
- Implémenter dans l'ordre défini
- Respecter les conventions identifiées en phase EXPLORE
- Utiliser Edit pour modifier les fichiers existants
- Utiliser Write uniquement pour les nouveaux fichiers
- Mettre à jour la todo list avec TodoWrite après chaque étape

**2. Qualité du code**
- Suivre les patterns existants du projet
- Respecter le style de code (indentation, nommage, etc.)
- Ne pas sur-engineer : faire exactement ce qui est demandé
- Éviter les emojis sauf demande explicite
- Ajouter des commentaires uniquement si la logique n'est pas évidente

**3. Gestion des erreurs**
- Gérer les erreurs de façon appropriée au contexte
- Ne pas ajouter de validation excessive aux frontières internes
- Valider uniquement aux points d'entrée (user input, API externes)

**4. Communication pendant le CODE**
- Informer l'utilisateur de la progression
- Marquer les todos comme in_progress puis completed
- Signaler tout écart par rapport au plan validé

### Validation Phase 3

Après l'implémentation:
- Résumer les changements effectués
- Confirmer que tout correspond au plan
- Demander si l'utilisateur souhaite passer aux TESTS

---

## ✅ Phase 4/4: TEST - Validation

### Objectif
Tester l'implémentation avec les outils EXISTANTS du projet.

### Actions à réaliser

**1. Identification des commandes de test disponibles**
Lire les fichiers de configuration pour identifier les commandes:
- `package.json` → scripts npm (lint, test, build, typecheck, etc.)
- `pytest.ini` ou `pyproject.toml` → configuration pytest
- `tsconfig.json` → configuration TypeScript
- `.eslintrc.*` → configuration ESLint
- Autres fichiers de config pertinents

**2. Exécution des tests existants**
Lancer UNIQUEMENT les commandes qui existent:
- Tests unitaires (pytest, vitest, jest, etc.)
- Linting (eslint, flake8, etc.)
- Type checking (tsc, mypy, etc.)
- Build (npm run build, etc.)

**IMPORTANT**:
- NE PAS créer de nouveaux tests s'ils n'existent pas dans le projet
- NE PAS lancer de commandes qui n'existent pas
- NE PAS inventer des configurations de test

**3. Analyse des résultats**
- Rapporter les résultats de chaque commande
- Si des tests échouent: analyser et corriger
- Si des erreurs de lint/type: corriger
- Si le build échoue: debugger et résoudre

**4. Vérification manuelle**
Si pertinent selon la fonctionnalité:
- Suggérer des tests manuels à l'utilisateur
- Expliquer comment vérifier le bon fonctionnement
- Proposer des commandes pour tester localement

### Validation Phase 4

**Rapport final**:
```
## ✅ Résultats des Tests

### Tests exécutés
- [Commande 1] : ✅ PASS / ❌ FAIL (détails)
- [Commande 2] : ✅ PASS / ❌ FAIL (détails)

### Fichiers modifiés
- path/to/file1 : [description]
- path/to/file2 : [description]

### Fichiers créés
- path/to/new-file : [description]

### Statut final
✅ Implémentation terminée et testée
OU
⚠️ Tests en échec - corrections nécessaires
```

---

## Notes Importantes

### Comportement attendu
- **Jamais de passage automatique** entre les phases sans validation utilisateur
- **Toujours demander confirmation** avant de coder
- **Poser des questions** sur les incertitudes plutôt que deviner
- **Suivre strictement** le plan validé en phase CODE

### Utilisation des outils
- WebSearch : recherche d'informations externes
- Task(Explore) : exploration approfondie du codebase
- Glob/Grep : recherche de patterns dans le code
- Read : lecture de fichiers spécifiques
- AskUserQuestion : validation et clarification
- TodoWrite : suivi de la progression
- Edit/Write : modifications du code

### Flags optionnels
Si `--auto-mode` est passé en argument:
- Réduire les validations intermédiaires
- MAIS toujours demander validation avant CODE
- MAIS toujours poser les questions critiques

---

## Démarrage

Pour démarrer ce workflow, répondez à ces questions:

1. **Quelle est la fonctionnalité à implémenter?**
2. **Y a-t-il des contraintes particulières?**
3. **Préférez-vous un mode guidé (validation à chaque phase) ou semi-automatique?**

Une fois ces informations fournies, je commencerai la **Phase 1: EXPLORE**.
