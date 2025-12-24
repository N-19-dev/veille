---
allowed-tools: Bash(*), WebSearch, Glob, Grep, Read, Task, AskUserQuestion, TodoWrite, Write
argument-hint: [--skip-questions] | [--quick-mode]
description: Analyse un projet existant et génère toute la documentation (IDEA.md, PRD.md, ARCHI.md, BACKLOG.md)
model: claude-opus-4-5-20251101
---

# Reverse Engineering - Documentation de Projet Existant

Ce workflow analyse votre projet existant et génère automatiquement toute la documentation manquante.

**Workflow en 5 phases :**
1. **REMONTER** : Analyser le code existant
2. **GÉNÉRER** : Créer ARCHI.md, PRD.md, IDEA.md, BACKLOG.md
3. **REDESCENDRE** : Poser questions stratégiques (10 questions)
4. **VALIDER** : Identifier problèmes critiques et gaps
5. **AMÉLIORER** : Plan d'amélioration personnalisé

---

## 📝 Informations de Contexte

Avant de commencer l'analyse, j'ai besoin de quelques informations de base sur votre projet.

**Si vous ne connaissez pas les réponses, laissez vide - j'analyserai le code pour déduire automatiquement.**

---

## 🔍 Phase 1/5 : REMONTER - Analyse du Code Existant

### Objectif
Analyser exhaustivement le projet pour comprendre ce qui existe réellement.

### Actions à réaliser

**1. Exploration de la structure**
- Lister tous les fichiers et dossiers (Glob)
- Identifier la structure du projet
- Détecter le type de projet (web app, API, mobile, CLI, etc.)
- Repérer les fichiers de configuration importants

**2. Analyse des dépendances**
Lire et analyser :
- `package.json` / `requirements.txt` / `Cargo.toml` / `go.mod`
- Identifier la stack technique complète
- Versions des dépendances principales
- Scripts disponibles (npm scripts, make targets, etc.)

**3. Analyse de la configuration**
Lire tous les fichiers de config :
- Configuration build (vite.config, webpack, tsconfig, etc.)
- Configuration tests (jest, pytest, vitest, etc.)
- Configuration linting/formatting (eslint, prettier, flake8, etc.)
- Configuration base de données (prisma, migrations, etc.)
- Variables d'environnement (.env.example)

**4. Analyse du code source**
Utiliser Task(subagent_type=Explore) pour :
- Comprendre l'architecture globale
- Identifier les features implémentées (routes, pages, composants, etc.)
- Analyser les modèles de données (DB schema, types, etc.)
- Repérer les patterns utilisés (MVC, Clean Architecture, etc.)
- Détecter les conventions de code

**5. Recherche de TODOs et FIXMEs**
Grep pour trouver :
- `TODO` : Features prévues mais non faites
- `FIXME` : Bugs connus à corriger
- `HACK` : Code temporaire à refactorer
- `XXX` : Points d'attention

**6. Analyse des tests**
- Identifier les tests existants (unitaires, intégration, E2E)
- Calculer le coverage approximatif (fichiers testés vs total)
- Repérer les zones non testées

**7. Analyse de la dette technique**
Identifier :
- Fichiers > 300 lignes (complexité élevée)
- Code dupliqué (patterns répétés)
- Dépendances obsolètes ou avec CVE
- Secrets potentiellement hardcodés
- Problèmes de performance évidents
- Code smell (anti-patterns)

**8. Recherche web pour contexte**
WebSearch pour :
- Best practices de la stack utilisée
- Patterns architecturaux standards
- Outils manquants recommandés

### Synthèse de l'Exploration

Créer un résumé structuré :

```markdown
## Synthèse de l'Analyse du Code

### Type de Projet Détecté
[Web App / API / Full-Stack / Mobile / CLI / Library]

### Stack Technique Complète
**Frontend :**
- [Framework] [version]
- [Librairies principales]

**Backend :**
- [Framework] [version]
- [Base de données]

**Infra/DevOps :**
- [Déploiement]
- [CI/CD]

### Structure du Projet
```
[Arborescence principale]
```

### Features Implémentées Identifiées
1. [Feature 1 - détectée via routes/pages]
2. [Feature 2 - détectée via composants]
...

### Configuration Détectée
- Tests : [Jest/Pytest/etc.] (Coverage : X%)
- Linting : [ESLint/Flake8/etc.]
- Build : [Vite/Webpack/etc.]

### Dette Technique Identifiée
**Critique (P0) :**
- [Problème 1]

**Haute (P1) :**
- [Problème 2]

**Moyenne (P2) :**
- [Problème 3]

### TODOs/FIXMEs Détectés
- [X] TODOs trouvés
- [Y] FIXMEs trouvés
- [Z] HACKs trouvés
```

---

## 📄 Phase 2/5 : GÉNÉRER - Création de la Documentation

### Objectif
Générer automatiquement tous les fichiers de documentation basés sur l'analyse du code.

### Fichiers à Générer (dans l'ordre)

#### 1. specs/ARCHI.md - Architecture Technique

**Contenu à générer :**

```markdown
# Architecture Technique

*Document généré automatiquement par analyse du code - Date : [DATE]*

## 1. Vue d'Ensemble

**Type de projet :** [Web App/API/etc.]
**Stack principale :** [Technologies détectées]

[Résumé de l'architecture en 2-3 paragraphes]

## 2. Stack Technique Détaillée

### Frontend
- **Framework :** [Nom] [Version]
- **UI Library :** [shadcn/MUI/etc.] [Version]
- **State Management :** [Zustand/Redux/etc.] [Version]
- **Routing :** [Next.js Router/React Router/etc.] [Version]
- **Forms :** [React Hook Form/Formik/etc.] [Version]
- **HTTP Client :** [Axios/React Query/etc.] [Version]

### Backend
- **Framework :** [Express/FastAPI/etc.] [Version]
- **ORM :** [Prisma/TypeORM/SQLAlchemy/etc.] [Version]
- **Database :** [PostgreSQL/MongoDB/etc.] [Version]
- **Authentication :** [JWT/NextAuth/etc.] [Version]
- **API Type :** [REST/GraphQL/tRPC] [Version]

### Infrastructure
- **Déploiement :** [Vercel/AWS/Heroku/etc.]
- **Database Hosting :** [Supabase/RDS/etc.]
- **CDN :** [Cloudflare/CloudFront/etc.]
- **Monitoring :** [Sentry/Datadog/None] ⚠️
- **CI/CD :** [GitHub Actions/GitLab CI/None] ⚠️

### Outils de Développement
- **Package Manager :** [npm/pnpm/yarn] [Version]
- **Build Tool :** [Vite/Webpack/esbuild] [Version]
- **TypeScript :** [Version] - Strict mode: [Yes/No]
- **Linting :** [ESLint/Flake8/etc.] [Config]
- **Formatting :** [Prettier/Black/etc.] [Config]
- **Testing :** [Vitest/Jest/Pytest/etc.] [Config]

## 3. Structure du Projet

```
[Arborescence complète avec explications]
```

**Explications :**
- `src/app/` : [Description]
- `src/components/` : [Description]
- `src/lib/` : [Description]
...

## 4. Architecture Applicative

**Pattern détecté :** [MVC/Clean Architecture/Feature-based/etc.]

[Schéma ou description de l'architecture]

### Flux de Données
1. [Étape 1]
2. [Étape 2]
...

## 5. Base de Données

**Schéma détecté :**

[Si Prisma/ORM : extraire le schéma]

**Modèles principaux :**
- `User` : [Champs]
- `Project` : [Champs]
...

**Relations :**
- [Relations détectées]

## 6. API & Endpoints

**Endpoints détectés :**

| Méthode | Path | Description |
|---------|------|-------------|
| GET | /api/users | [Détecté depuis code] |
| POST | /api/projects | [Détecté depuis code] |
...

## 7. Standards de Code

**Conventions détectées :**
- Naming : [camelCase/snake_case/etc.]
- Indentation : [2 spaces/4 spaces/tabs]
- Imports : [Ordre détecté]
- Comments : [JSDoc/Docstrings/etc.]

## 8. Sécurité

**Implémenté :**
- [x] Authentication : [Type]
- [x] Authorization : [Type]
- [ ] Rate Limiting ⚠️ (Manquant)
- [ ] Input Validation ⚠️ (Partiel)
- [ ] CORS ⚠️ (À vérifier)
- [ ] HTTPS ⚠️ (À vérifier)

**Secrets détectés :**
⚠️ [X] fichiers contiennent potentiellement des secrets hardcodés

## 9. Performance

**Optimisations détectées :**
- [x] Code splitting : [Oui/Non]
- [x] Lazy loading : [Oui/Non]
- [x] Caching : [Type/None]
- [x] Image optimization : [Oui/Non]

**Problèmes identifiés :**
- [Liste des FIXMEs liés à la performance]

## 10. Tests

**Configuration :**
- Framework : [Jest/Vitest/Pytest/etc.]
- Coverage actuel : [X%]

**Tests existants :**
- Unitaires : [X] fichiers
- Intégration : [X] fichiers
- E2E : [X] fichiers

**Zones non testées :**
- [Liste des fichiers critiques sans tests]

## 11. Dette Technique Identifiée

### P0 - Critique (À corriger immédiatement)
- [ ] [Dette 1 - Impact sécurité/production]
- [ ] [Dette 2]

### P1 - Haute (À corriger sous 1-2 sprints)
- [ ] [Dette 3]
- [ ] [Dette 4]

### P2 - Moyenne (Backlog)
- [ ] [Dette 5]

**Score Santé Globale : X/100**
- Architecture : X/20
- Tests : X/20
- Documentation : X/20
- Sécurité : X/20
- Performance : X/20

## 12. Ce qui Manque (Gaps)

**Infrastructure :**
- [ ] Monitoring/Observability (Sentry, Datadog)
- [ ] CI/CD (GitHub Actions)
- [ ] Staging environment
- [ ] Backup strategy

**Code :**
- [ ] Tests (Coverage < 80%)
- [ ] API documentation (Swagger/OpenAPI)
- [ ] Error handling standardisé
- [ ] Logging structuré

**Sécurité :**
- [ ] Audit de sécurité (OWASP)
- [ ] Rate limiting
- [ ] Input validation Zod/Yup
```

---

#### 2. specs/PRD.md - Product Requirements Document

**Contenu à générer (reconstitué depuis le code) :**

```markdown
# Product Requirements Document

*Document reconstitué automatiquement depuis l'analyse du code*

## 1. Vue d'Ensemble

**Résumé du produit :**
[Déduire depuis les features implémentées]

**Objectif principal :**
[Reconstituer depuis les fonctionnalités]

**Utilisateurs cibles :**
[Inférer depuis les features et personas détectés dans le code]

## 2. Le Problème

**Problème résolu (reconstitué) :**
[Déduire depuis les features ce que le projet cherche à résoudre]

**Conséquences du problème :**
[À compléter manuellement - suggestions fournies]

## 3. La Solution

**Description de la solution actuelle :**
[Ce que fait le projet actuellement]

**Différenciateurs (si détectés) :**
- [Caractéristique unique 1]
- [Caractéristique unique 2]

## 4. Personas Utilisateurs (Reconstitués)

### Persona 1 : [Nom déduit]
**Profil :**
- [Déduire depuis les features]

**Besoins :**
- [Features utilisées par ce persona]

**Pain Points :**
- [Déduire depuis les fonctionnalités]

[Répéter pour chaque persona détecté]

## 5. Features Implémentées

### Epic : [Nom Epic 1 - déduit depuis groupes de features]

#### Feature 1.1 : [Nom - détecté depuis code]
**Statut :** ✅ Implémenté

**Description :**
[Reconstituer depuis le code ce que fait cette feature]

**User Story :**
En tant que [persona]
Je veux [action détectée]
Afin de [bénéfice déduit]

**Critères d'acceptation :**
- [x] [Critère 1 - déduit du code]
- [x] [Critère 2]

**Fichiers concernés :**
- `[path/to/file1.tsx]`
- `[path/to/file2.ts]`

---

#### Feature 1.2 : [Nom]
⚠️ **Statut :** Partiellement implémenté (TODOs détectés)

[Même structure]

---

#### Feature 1.3 : [Nom]
❌ **Statut :** Non implémenté (détecté via TODOs uniquement)

[Même structure]

---

[Répéter pour toutes les features détectées]

## 6. Scope MVP

### Ce qui EST dans le MVP actuel
- [x] [Feature complète 1]
- [x] [Feature complète 2]

### Ce qui DEVRAIT être dans le MVP mais manque
- [ ] [Feature critique manquante 1 - ex: tests]
- [ ] [Feature critique manquante 2 - ex: monitoring]

### Hors Scope MVP (v2.0+)
- [ ] [Feature avancée 1 - détectée via TODOs]
- [ ] [Feature avancée 2]

## 7. Roadmap (Reconstituée depuis TODOs/FIXMEs)

### v1.1 (Prochaine version - TODOs détectés)
- [ ] [Feature TODO 1] - [X] TODOs dans le code
- [ ] [Feature TODO 2] - [Y] TODOs dans le code

### v1.5 (FIXMEs détectés)
- [ ] [Amélioration FIXME 1]
- [ ] [Amélioration FIXME 2]

### v2.0 (Hypothétique - à valider)
- [ ] [Feature majeure déduite]

## 8. User Flows Détectés

### Flow 1 : [Nom du flow principal]
1. [Étape 1 - détectée depuis le code]
2. [Étape 2]
...

[Schéma si possible]

## 9. Exigences Non Fonctionnelles (Détectées)

**Performance :**
- [Exigences détectées ou déduites]

**Sécurité :**
- [Exigences implémentées vs manquantes]

**Scalabilité :**
- [Limites actuelles détectées]

## 10. Hypothèses et Dépendances

**Hypothèses (à valider manuellement) :**
- [Hypothèse 1 déduite du code]
- [Hypothèse 2]

**Dépendances externes :**
- [Service externe 1 - détecté via API calls]
- [Service externe 2]

## 11. Métriques de Succès (Suggestions)

⚠️ **À définir manuellement** - Suggestions basées sur features :
- [Métrique 1 suggérée]
- [Métrique 2 suggérée]
```

---

#### 3. IDEA.md - Vision du Projet

**Contenu à générer (partiellement - nécessite complétion manuelle) :**

```markdown
# [Nom du Projet]

*Document partiellement reconstitué - Sections marquées ⚠️ à compléter manuellement*

## 1. QUI/QUOI/COMMENT/POURQUOI

### Qui êtes-vous ?
⚠️ **[À COMPLÉTER MANUELLEMENT]**

### Quel est le projet ?
**Nom :** [Nom détecté ou nom du dossier]

**Description (reconstituée) :**
[Résumé déduit des features implémentées]

### Comment ?
**Stack technique :**
[Extraire de ARCHI.md]

**Approche :**
[Déduire du pattern architectural détecté]

### Pourquoi ?
⚠️ **[À COMPLÉTER MANUELLEMENT]** - Claude ne peut pas deviner votre motivation personnelle.

**Suggestions basées sur le projet :**
- Résoudre le problème [X] que vous avez vécu ?
- Apprendre la stack [Y] ?
- Créer une source de revenu ?
- Portfolio / projet open source ?

## 2. LE PROBLÈME - WHAT

**Problème principal (reconstitué) :**
[Extrait de PRD.md]

**Pour qui ? (reconstitué)**
[Personas extraits de PRD.md]

## 3. LA SOLUTION - HOW

**Fonctionnalités principales (implémentées) :**
[Liste des features complètes de PRD.md]

**Différenciateurs (si détectés) :**
[Caractéristiques uniques du projet]

## 4. OBJECTIFS

⚠️ **[PARTIELLEMENT À COMPLÉTER]**

**Objectifs techniques (détectés) :**
- [Objectif 1 déduit - ex: "Architecture scalable"]
- [Objectif 2 déduit]

**Objectifs business (à compléter) :**
- [ ] [Votre objectif 1]
- [ ] [Votre objectif 2]

**Critères de succès (suggestions) :**
[Métriques suggérées depuis PRD.md]

## 5. ÉTAT ACTUEL

**Phase actuelle :** [MVP/Production/Développement - détecté]

**Ce qui fonctionne :**
- [Feature 1 complète]
- [Feature 2 complète]

**Ce qui reste à faire :**
[Extrait de BACKLOG.md]

**Score santé : X/100**
[Depuis ARCHI.md]

## 6. ROADMAP

[Extraire de PRD.md]

## 7. RESSOURCES

**Temps disponible :**
⚠️ [À compléter]

**Budget :**
⚠️ [À compléter]

**Équipe :**
⚠️ [À compléter]
```

---

#### 4. specs/tasks/BACKLOG.md - Tâches Restantes

```markdown
# Backlog - Ce qui Reste à Faire

*Généré automatiquement depuis analyse du code*

## 🔴 CRITICAL - Dette Technique (P0)

[Pour chaque dette technique P0 détectée :]

### [DEBT-XXX] [Titre du problème]
**Type :** Dette Technique
**Priority :** P0
**Estimation :** [X] SP

**Problème actuel :**
[Description détaillée du problème détecté]

**Impact si non corrigé :**
[Impact business/technique]

**Actions :**
1. [Action 1]
2. [Action 2]

**Fichiers concernés :**
- `[path/to/file]`

**Critère de succès :**
- [ ] [Critère 1]

---

## 🟠 HIGH PRIORITY (P1)

[Features incomplètes et dette P1]

### [FEAT-XXX] [Nom feature]
**Type :** Feature
**Priority :** P1
**Estimation :** [X] SP

**User Story :**
En tant que [persona]
Je veux [action]
Afin de [bénéfice]

**État actuel :**
[X] TODOs détectés dans le code

**Actions :**
[Extraire depuis les TODOs]

**Fichiers concernés :**
- `[path/to/file]` - [X] TODOs

---

## 🟡 MEDIUM PRIORITY (P2)

[Améliorations et optimisations]

---

## 📊 Résumé du Backlog

| Catégorie | Nombre | Story Points |
|-----------|--------|--------------|
| Dette P0 | [X] | [Y] SP |
| Dette P1 | [X] | [Y] SP |
| Features P1 | [X] | [Y] SP |
| Améliorations P2 | [X] | [Y] SP |
| **TOTAL** | **[X]** | **[Y] SP** |

**Estimation temps restant :** [X] sprints ([Y] mois)

## 📈 Priorisation Suggérée

**Sprint 1 (2 sem) :** [Tâches P0 critiques]
**Sprint 2 (2 sem) :** [Tâches P1 importantes]
**Sprint 3+ :** [Tâches P2]
```

---

#### 5. specs/ANALYSIS_REPORT.md - Rapport d'Analyse Complet

```markdown
# Rapport d'Analyse du Projet

**Date d'analyse :** [DATE]
**Analysé par :** Claude Code (Reverse Engineering)
**Projet :** [Nom]

---

## 📊 Score Global : X/100

| Critère | Score | Détails |
|---------|-------|---------|
| Architecture | X/20 | [Commentaire] |
| Tests | X/20 | [Commentaire] |
| Documentation | X/20 | [Commentaire] |
| Sécurité | X/20 | [Commentaire] |
| Performance | X/20 | [Commentaire] |
| **TOTAL** | **X/100** | [Verdict global] |

**Verdict :** [Excellent/Bon/Moyen/Faible/Critique]

---

## ✅ Points Forts

1. **[Point fort 1]**
   - [Détails]

2. **[Point fort 2]**
   - [Détails]

---

## ❌ Problèmes Critiques

### 1. [Problème Critique 1] (P0)
**Détecté dans :** [Fichiers/Configuration]
**Impact :** [Description impact]
**Risque :** [Ce qui peut arriver si non corrigé]
**Recommandation :** [Action corrective]

### 2. [Problème Critique 2] (P0)
[Même structure]

---

## ⚠️ Problèmes Importants

[Liste des problèmes P1]

---

## 💡 Recommandations Prioritaires

### Court Terme (Sprint 1-2)

**1. [Recommandation 1]** - [X] SP
- [Action concrète]
- Priorité : P0
- Impact : [Haut/Moyen/Faible]

**2. [Recommandation 2]** - [X] SP
- [Action concrète]

### Moyen Terme (Mois 2-3)

**3. [Recommandation 3]** - [X] SP
[...]

### Long Terme (Mois 4+)

**4. [Recommandation 4]** - [X] SP
[...]

---

## 📈 Roadmap Suggérée

**Sprint 1 (2 sem) :** [Tâches + SP]
**Sprint 2 (2 sem) :** [Tâches + SP]
**Sprint 3 (2 sem) :** [Tâches + SP]
[...]

**Date MVP "vraiment fini" :** [Estimation]

---

## 📁 Fichiers Critiques Identifiés

**À surveiller (haute complexité) :**
- `[path/to/complex-file]` - [Raison]

**À tester en priorité (non testé + critique) :**
- `[path/to/untested-critical]` - [Raison]

**Secrets potentiels (à vérifier) :**
- `[path/to/potential-secret]` - [Raison]

---

## 📚 Ressources Recommandées

**Pour améliorer architecture :**
- [Lien vers best practice 1]

**Pour améliorer stack [X] :**
- [Lien vers doc 2]

---

## 🎯 Prochaines Étapes Immédiates

1. **Lire toute la documentation générée**
   - [ ] IDEA.md (compléter sections manuelles)
   - [ ] PRD.md (valider features reconnues)
   - [ ] ARCHI.md (vérifier stack détectée)
   - [ ] BACKLOG.md (prioriser tâches)

2. **Passer à la Phase 3 : REDESCENDRE**
   - [ ] Répondre aux 10 questions stratégiques
   - [ ] Valider la direction du projet
   - [ ] Identifier les problèmes bloquants

3. **Créer Sprint 1 de correction**
   - [ ] Importer BACKLOG.md dans votre outil (GitHub/Jira)
   - [ ] Assigner tâches P0
   - [ ] Fixer deadline

---

*Fin de la génération automatique - Passer à Phase 3*
```

---

### Validation Phase 2

Une fois tous les fichiers générés, je vais :
1. Résumer les fichiers créés
2. Vous demander de vérifier l'exactitude
3. **NE PAS s'arrêter** - Passer automatiquement à la Phase 3 (REDESCENDRE)

**IMPORTANT :** La documentation générée est basée sur le code. Certaines sections nécessiteront votre validation et complétion manuelle (notamment IDEA.md - sections motivation et objectifs business).

---

## ❓ Phase 3/5 : REDESCENDRE - Questions Stratégiques

### Objectif
Valider que le projet va dans la bonne direction et identifier les problèmes critiques.

**CRITIQUE :** Cette phase évite de documenter un projet qui va dans le mur. Les réponses permettront de générer un plan d'amélioration personnalisé.

### Les 10 Questions Stratégiques

Je vais vous poser ces 10 questions via AskUserQuestion. **Prenez le temps d'y réfléchir.**

#### Q1. Vision reconstituée vs Vision réelle

"D'après mon analyse du code, voici la vision que j'ai reconstituée :

**Vision reconstituée :** [Résumer IDEA.md en 2 phrases]

**Question :** Est-ce que c'est bien ça ? Ou la vision a évolué depuis ?"

**Options :**
- C'est exactement ça
- C'est partiellement ça (préciser les différences)
- La vision a complètement changé
- On n'a jamais eu de vision claire

---

#### Q2. Problème résolu - Toujours pertinent ?

"Le problème que le projet résout d'après le code :

**Problème identifié :** [Extrait de PRD.md]

**Question :** Ce problème est-il toujours celui que tu veux résoudre ? Ou les priorités ont changé ?"

---

#### Q3. Utilisateurs cibles - Toujours les bons ?

"Les utilisateurs identifiés d'après les features :

**Personas reconstitués :** [Liste depuis PRD.md]

**Question :** Sont-ils toujours ta cible ? Ou tu vises maintenant un autre segment ?"

---

#### Q4. Stack technique - Satisfait ou regrets ?

"Stack actuelle détectée :

**Stack :** [Lister depuis ARCHI.md]

**Question :** Es-tu satisfait de cette stack ? Ou tu regrettes certains choix ?"

**Options :**
- Totalement satisfait
- Quelques regrets mais on garde
- Gros regrets, on devrait migrer
- Aucune idée, besoin de conseils

---

#### Q5. Architecture - Scalable pour la suite ?

"Architecture actuelle : [Pattern détecté]

**Question :** Cette architecture va-t-elle tenir pour atteindre tes objectifs (X utilisateurs, Y features) ? Ou elle va craquer avant ?"

---

#### Q6. Dette technique - Bloquante ou gérable ?

"Dette technique identifiée : **Score X/100**

**Problèmes P0 :** [Liste]

**Question :** Cette dette te bloque-t-elle au quotidien ?"

**Options :**
- Oui, ça ralentit tout (critique)
- Parfois gênant (moyen)
- Pas vraiment un problème (faible)

---

#### Q7. État du projet - Où en es-tu ?

**Question :** Dans quelle phase est le projet actuellement ?"

**Options :**
- MVP à finir (focus features)
- Production avec users (focus stabilité)
- Croissance (focus performance)
- Pivot en cours (focus changement direction)

---

#### Q8. Prochaine étape critique - C'est quoi ?

"D'après le code, il reste [X features à finir, Y dette technique].

**Question :** Quelle est TA prochaine priorité absolue ?"

**Options :**
- Finir feature X (business)
- Fixer la dette technique (qualité)
- Acquérir plus d'users (growth)
- Améliorer performance (scalabilité)
- Pivoter (changement direction)

---

#### Q9. Ressources disponibles - Combien de temps ?

**Question :** Combien de temps peux-tu allouer à l'amélioration du projet ?"

**Options :**
- 100% (freeze features, focus refactoring)
- 50% (sprints dédiés)
- 20% (1 jour par semaine)
- 0% (juste maintenir, pas de refactoring)

---

#### Q10. Risques identifiés - Qu'est-ce qui te fait peur ?

**Question :** Quelle partie du projet te fait le plus peur ?"

**Catégories :**
- Techniquement : [Quel module/fichier ?]
- Business : [Quelle deadline/risque ?]
- Équipe : [Quel départ/manque de compétence ?]

---

### Après les Questions

**STOP ET ATTENDRE VOS RÉPONSES.**

Ne pas générer le plan d'amélioration avant d'avoir reçu toutes vos réponses.

---

## 🎯 Phase 4/5 : VALIDER - Diagnostic Complet

### Objectif
Analyser le gap entre vision code et vision réelle, identifier les problèmes critiques.

**UNIQUEMENT APRÈS AVOIR REÇU VOS RÉPONSES aux 10 questions.**

### Fichier à Générer : specs/STRATEGIC_REVIEW.md

```markdown
# Revue Stratégique du Projet

**Date :** [DATE]
**Analysé par :** Claude Code

---

## 📋 Réponses aux Questions Stratégiques

**Q1. Vision :** [Votre réponse]
**Q2. Problème :** [Votre réponse]
**Q3. Utilisateurs :** [Votre réponse]
**Q4. Stack :** [Votre réponse]
**Q5. Architecture :** [Votre réponse]
**Q6. Dette technique :** [Votre réponse]
**Q7. État projet :** [Votre réponse]
**Q8. Prochaine priorité :** [Votre réponse]
**Q9. Temps disponible :** [Votre réponse]
**Q10. Risques :** [Votre réponse]

---

## 🔍 Analyse des Gaps

### Vision : Code vs Réalité

**Vision reconstituée (depuis code) :**
[Résumé IDEA.md]

**Vision réelle (vos réponses) :**
[Réponse Q1]

**Gap identifié :**
[Analyse de la différence]

**Verdict :**
- [ ] Aligné (continuer comme ça)
- [ ] Petit gap (ajustements mineurs)
- [ ] Gros gap (pivot nécessaire)
- [ ] Perdu (redéfinir complètement)

### Priorités : Code vs Réalité

**Priorités détectées (depuis code) :**
[TODOs/FIXMEs principaux]

**Priorités réelles (vos réponses) :**
[Réponse Q8]

**Gap identifié :**
[Analyse de la différence]

---

## 🚨 Problèmes Critiques (Va dans le mur si pas corrigé)

### Problème 1 : [Titre]
**Criticité :** P0
**Identifié :** [Dans le code / Dans vos réponses]
**Impact :** [Bloquer croissance / Bugs / Users mécontents / Sécurité]
**Délai avant mur :** [X semaines/mois]

**Preuve :**
[Détails depuis analyse code ou réponses]

**Action corrective :**
[Que faire pour éviter le mur]

---

[Répéter pour chaque problème critique]

---

## ✅ Forces à Préserver

**Ce qui marche bien et qu'il ne faut PAS casser :**
1. [Force 1 - depuis code]
2. [Force 2 - depuis réponses]

---

## 📊 Matrice de Priorisation

Basé sur vos réponses, voici la matrice des problèmes/tâches :

```
Impact
Élevé  │ [2] Critiques      │ [1] Quick Wins
       │ Faire ENSUITE      │ 🎯 Faire D'ABORD
       │────────────────────┼────────────────────
Faible │ [4] Ignorer        │ [3] Remplissage
       │ Ne PAS faire       │ Si temps libre
       └────────────────────┴────────────────────
         Élevé              Faible
                   Effort
```

**[1] Quick Wins (P0) - Semaine 1-2 :**
- [Tâche 1 - Fort impact, Faible effort]
- [Tâche 2]

**[2] Critiques (P1) - Mois 1-2 :**
- [Tâche 3 - Fort impact, Fort effort]
- [Tâche 4]

**[3] Remplissage (P2) - Si temps :**
- [Tâche 5 - Faible impact, Faible effort]

**[4] Ignorer (Won't Do) :**
- [Tâche 6 - Faible impact, Fort effort - Ne PAS faire]

---

## 🎯 Recommandations Basées sur Vos Réponses

[Analyse personnalisée selon réponses Q7, Q8, Q9]

---

*Fin Phase 4 - Passer à Phase 5 : Plan d'Amélioration*
```

---

## 🚀 Phase 5/5 : AMÉLIORER - Plan d'Amélioration Personnalisé

### Objectif
Créer une roadmap d'amélioration personnalisée basée sur vos réponses et contraintes.

### Fichier à Générer : specs/IMPROVEMENT_ROADMAP.md

```markdown
# Roadmap d'Amélioration Personnalisée

**Basé sur vos réponses et contraintes**

---

## 🎯 Votre Contexte

**Temps disponible :** [Réponse Q9]
**Priorité actuelle :** [Réponse Q8]
**État projet :** [Réponse Q7]

---

## 📅 Planning Adapté

[SI 100% temps (freeze features) :]

### Planning : Mode Refactoring Complet (3 mois)

**Mois 1 : Stabilisation (P0 critique)**
- Semaine 1-2 : [Tâches sécurité + tests critiques]
- Semaine 3-4 : [Tâches dette P0]

**Mois 2 : Refactoring (P1 important)**
- Semaine 5-8 : [Refactoring modules complexes]

**Mois 3 : Optimisation (P2)**
- Semaine 9-12 : [Performance + Documentation]

---

[SI 50% temps (2 jours/semaine) :]

### Planning : Mode Balanced (6 mois)

**Mois 1-2 : Quick Wins + Tests Critiques**
- [Tâches P0 seulement]

**Mois 3-4 : Refactoring Ciblé**
- [Module par module]

**Mois 5-6 : Finalisation**
- [Performance + Docs]

---

[SI 20% temps (1 jour/semaine) :]

### Planning : Mode Progressif (12 mois)

**Mois 1-3 : Quick Wins uniquement**
- [Tâches P0 faible effort]

**Mois 4-9 : Refactoring Très Progressif**
- [1 module tous les 2 mois]

**Mois 10-12 : Finalisation**
- [Finitions]

---

[SI 0% temps (maintenance only) :]

### ⚠️ ATTENTION : Plan Minimal Critique

Avec 0% temps pour amélioration, **le projet va continuer à se dégrader**.

**Plan minimal critique (4h/mois) :**
1. Fixer CVE de sécurité (obligatoire)
2. Tests sur code qui casse souvent (1 test/mois)
3. Documenter décisions importantes (ADR)

**Sinon :** Dette technique va exploser et forcer réécriture dans 6-12 mois.

**Recommandation :** Allouer au moins 20% temps (1 jour/semaine).

---

## 📋 Actions Immédiates (Cette Semaine)

Basé sur votre priorité (Q8) :

[SI priorité = "Finir feature X" :]

**Plan : Focus Feature**
1. Mettre de côté dette technique (sauf P0 bloquants)
2. Focus : Finir feature X rapidement
3. Ajouter tests minimum sur feature X (critiques uniquement)
4. Planifier refactoring après feature (sprint dédié)

**Tâches cette semaine :**
- [ ] [Tâche 1 pour finir feature]
- [ ] [Tâche 2]

---

[SI priorité = "Fixer dette technique" :]

**Plan : Sprint Stabilisation**
1. Freeze nouvelles features (sauf critiques business)
2. Sprint "Tech Debt" 2 semaines
3. Commencer par Quick Wins (victoires rapides)
4. Puis attaquer problème le plus critique

**Tâches cette semaine :**
- [ ] [Quick Win 1]
- [ ] [Quick Win 2]

---

[SI priorité = "Pivoter" :]

**Plan : Pivot**
1. STOP développement actuel
2. Valider nouveau direction (interviews, POC)
3. Créer nouveau IDEA.md pour pivot
4. Refactorer architecture si nécessaire

**Tâches cette semaine :**
- [ ] Documenter nouvelle vision (IDEA_V2.md)
- [ ] 5 interviews utilisateurs cible
- [ ] POC feature clé du pivot

---

## 📊 Tracking & KPIs

**KPIs à suivre selon votre priorité :**

[Personnalisé selon Q8]

**Dashboard suggéré :**
- Score santé : X/100 → Objectif Y/100 dans [Z] mois
- Coverage tests : X% → Objectif Y%
- Dette P0 : [X] tâches → Objectif 0
- [Autres KPIs personnalisés]

---

## 🔄 Revue & Ajustements

**Fréquence de revue suggérée :**
- [Hebdomadaire si 100% temps]
- [Bi-hebdomadaire si 50% temps]
- [Mensuelle si 20% temps]

**Prochaine revue :** [Date suggérée]

---

*Fin du Plan d'Amélioration - Workflow Terminé*
```

---

### Fichier Supplémentaire : specs/PIVOT_PLAN.md (si pivot détecté)

**Si réponses Q1/Q8 indiquent un pivot :**

```markdown
# Plan de Pivot

## Ancienne Direction (Code Actuel)

**Vision code :**
[IDEA.md reconstitué]

**Features implémentées :**
[Liste depuis PRD.md]

---

## Nouvelle Direction (Vos Réponses)

**Nouvelle vision :**
[Réponse Q1]

**Nouveau problème à résoudre :**
[Réponse Q2]

**Nouveaux utilisateurs :**
[Réponse Q3]

---

## Analyse du Pivot

**Ampleur du pivot :**
- [ ] Pivot mineur (même stack, nouvelles features)
- [ ] Pivot moyen (refactoring important)
- [ ] Pivot majeur (réécriture partielle)
- [ ] Pivot total (nouveau projet)

**Ce qui reste utilisable :**
- [Infrastructure/Stack]
- [Modules réutilisables]

**Ce qui doit changer :**
- [Architecture]
- [Features à retirer]
- [Features à ajouter]

---

## Plan de Migration

**Phase 1 : Validation (Mois 1)**
- [ ] Interviews 10 utilisateurs nouveau segment
- [ ] POC feature clé du pivot
- [ ] Validation business model

**Phase 2 : Préparation (Mois 2)**
- [ ] Nouveau IDEA.md
- [ ] Nouveau PRD.md
- [ ] Architecture cible

**Phase 3 : Migration (Mois 3-6)**
- [ ] Refactoring modules
- [ ] Nouvelles features pivot
- [ ] Tests

**Phase 4 : Lancement (Mois 7)**
- [ ] Beta
- [ ] Production

---

## Risques du Pivot

**Risques identifiés :**
1. [Risque 1]
2. [Risque 2]

**Mitigation :**
- [Plan B]
- [Plan C]
```

---

## 📚 Résumé Final

Une fois le workflow terminé, vous aurez :

**Documentation Générée :**
- ✅ `IDEA.md` (vision - partiellement à compléter)
- ✅ `specs/PRD.md` (features reconnues)
- ✅ `specs/ARCHI.md` (architecture actuelle)
- ✅ `specs/tasks/BACKLOG.md` (tâches restantes)
- ✅ `specs/ANALYSIS_REPORT.md` (audit complet)
- ✅ `specs/STRATEGIC_REVIEW.md` (validation direction)
- ✅ `specs/IMPROVEMENT_ROADMAP.md` (plan personnalisé)
- ✅ `specs/PIVOT_PLAN.md` (si pivot détecté)

**Structure Finale :**
```
votre-projet/
├── IDEA.md                         # Vision (à compléter)
├── specs/
│   ├── PRD.md                      # Features
│   ├── ARCHI.md                    # Architecture
│   ├── ANALYSIS_REPORT.md          # Audit
│   ├── STRATEGIC_REVIEW.md         # Validation
│   ├── IMPROVEMENT_ROADMAP.md      # Plan
│   ├── PIVOT_PLAN.md               # (si pivot)
│   └── tasks/
│       └── BACKLOG.md              # Tâches
```

---

## 🚀 Démarrage du Workflow

**Prêt à commencer ?**

Je vais maintenant :
1. **Phase 1** : Analyser votre projet en profondeur
2. **Phase 2** : Générer toute la documentation
3. **Phase 3** : Vous poser les 10 questions stratégiques
4. **Phase 4** : Créer un diagnostic complet
5. **Phase 5** : Générer votre plan d'amélioration personnalisé

**Flags optionnels :**
- `--skip-questions` : Générer docs seulement (Phase 1-2, skip 3-5)
- `--quick-mode` : Analyse rapide (moins exhaustive)

**Commençons par Phase 1 : EXPLORER votre projet.**
