# Roadmap d'Amélioration Personnalisée - Veille Tech Crawling

**Date :** 2025-12-20
**Basé sur vos réponses et contraintes**
**Stratégie :** Excellence UX → Engagement Utilisateurs → Monétisation (Optionnelle)

---

## 🎯 Votre Contexte & Contraintes

**Objectif #1 (PRIORITÉ ABSOLUE) :**
> **"Faire un site utile avec une vraie bonne expérience pour mes utilisateurs"**

**Cela signifie 2 piliers indissociables :**
1. 🎨 **Expérience utilisateur (UX)** - Site rapide, agréable, accessible
2. 📊 **Qualité du contenu & Pertinence** - Articles vraiment utiles, moins de bruit, meilleur scoring

**Sans pertinence du contenu, l'UX ne sert à rien.**
**Sans bonne UX, même le meilleur contenu ne sera pas utilisé.**

Tout le reste est secondaire. La monétisation viendra naturellement si l'expérience ET le contenu sont excellents.

**Décisions Stratégiques :**
- **Timeline :** Flexible, pas de deadline monétisation
- **Temps disponible :** 20% (1 jour/semaine) = ~5-8 SP/sprint (2 semaines)
- **Stratégie :** UX First - Perfectionner l'expérience utilisateur avant tout
- **Scope :** Complet, focus qualité et utilité réelle
- **Objectif final :** Site que les utilisateurs adorent utiliser chaque semaine

**État Actuel :**
- Phase : Production avec users réels
- Priorité #1 : **Expérience utilisateur excellente**
- Priorité #2 : Stabilité + qualité technique
- Dette tech : Ralentit tout (critique)
- Risque #1 : Dépendance Groq 100%

**Critères Succès (UX + Contenu) :**
- ✅ **Pertinence articles > 90%** (feedback users - critère #1)
- ✅ **Ratio signal/bruit élevé** (articles vraiment utiles vs fluff)
- ✅ Users trouvent la veille utile chaque semaine
- ✅ Zéro bugs signalés users
- ✅ Performance > 90 Lighthouse (desktop + mobile)
- ✅ Temps de recherche < 2 secondes
- ✅ Catégorisation précise (> 95%)

---

## 📅 Planning Adapté : Approche "UX Excellence First"

### Phase 1 : FONDATIONS (UX + CONTENU) & QUALITÉ TECHNIQUE (Mois 1-3)

**Objectif :** Site fiable, rapide, agréable + Articles pertinents - Fondations solides

**Focus :** Dette technique + Performance + Stabilité + Quick wins UX + Amélioration pertinence

**Timeline :** 12 semaines (si 20% temps = 5-8 SP/sprint)
**Total SP :** ~52 SP (47 SP dette + 5 SP pertinence)

---

#### Mois 1 (Semaines 1-4) : Quick Wins + Fondations

**Sprint 1 (Sem 1-2) : Mitigation Risques - 8 SP**

**Semaine 1-2 :**
- [P0] **Abstraction LLM Provider** (3 SP) ⚠️ **CRITIQUE**
  - Créer interface `LLMProvider` (ABC)
  - Implémenter `GroqProvider`, `OpenAIProvider`, `OllamaProvider`
  - Config YAML : `llm.provider: groq` (switchable)
  - Tests : switch provider en config
  - **Deliverable :** Risque Groq mitigé, projet survivable

- [P1] **Setup Monitoring Sentry** (5 SP)
  - Intégrer Sentry backend (`main.py`, `veille_tech.py`)
  - Intégrer Sentry frontend (`main.tsx`)
  - Configurer alertes Slack (si > 10 erreurs/run)
  - Variables GitHub Secrets (`SENTRY_DSN_BACKEND`, `SENTRY_DSN_FRONTEND`)
  - **Deliverable :** Bugs détectés automatiquement

**Sprint 2 (Sem 3-4) : Tests Frontend Critiques - 5 SP**

**Semaine 3-4 :**
- [P1] **Tests Frontend Vitest** (5 SP)
  - Setup Vitest + @testing-library/react
  - Tests `App.tsx` : filtrage multi-couches (3 tests)
  - Tests `CategoryFilter.tsx` : sélection catégorie (2 tests)
  - Tests `lib/parse.ts` : parsing digest.json (2 tests)
  - **Deliverable :** Coverage frontend 40-50%

---

#### Mois 2 (Semaines 5-8) : CI/CD + Performance + Pertinence

**Sprint 2.5 (Sem 5-6, Partie 1) : 🎯 Amélioration Pertinence & Scoring - 5 SP**

**Bénéfice Utilisateur :** Moins de bruit, plus d'articles vraiment utiles, meilleure sélection

**Semaine 5 (2-3 jours dédiés pertinence) :**
- [CONTENU] **Optimisation Scoring & Filtrage** (5 SP)
  - **Audit pertinence actuelle** (1 SP)
    - Analyser 100 derniers articles sélectionnés
    - Identifier faux positifs (bruit, marketing, beginner)
    - Identifier faux négatifs (bons articles ratés)

  - **Améliorer anti-bruit filtering** (2 SP)
    - Affiner seuils `tech_level` (beginner detection)
    - Améliorer `marketing_score` (promo content)
    - Blacklist keywords marketing ("sponsored", "partner", etc.)
    - Test sur 1000 articles crawlés

  - **Optimiser seuils par catégorie** (1 SP)
    - Analyser distribution scores par catégorie
    - Ajuster `category_thresholds` (config.yaml)
    - Ex: News 60 → 65, Warehouses 45 → 50

  - **Ajouter sources pertinentes** (1 SP)
    - Research 5-10 nouvelles sources qualité (blogs experts) comme reddit ou X ou l'on peut trouver des bon artciles/Rex / explication
    - Configurer RSS feeds (config.yaml)
    - Pondération source (`source_weight`)

  - **Deliverable :** Ratio signal/bruit amélioré de 20-30%

---

**Sprint 3 (Sem 6-7) : CI/CD Tests Automatiques - 5 SP**

**Semaine 6-7 :**
- [P1] **CI/CD Tests** (5 SP)
  - GitHub Actions : step pytest (backend-weekly.yml)
  - GitHub Actions : step vitest (deploy-frontend.yml)
  - Fail workflow si tests échouent
  - Coverage report (Codecov ou artifact)
  - Badge coverage README.md
  - **Deliverable :** Tests automatiques en CI

**Sprint 4 (Sem 8) : Cache Redis Embeddings - 8 SP**

**Semaine 8 :**
- [P1] **Cache Redis** (8 SP)
  - Setup Redis (Upstash free tier ou Docker local)
  - Cache embeddings par `hash(content)`, TTL 30 jours
  - Fallback : calcul si cache miss
  - Config YAML : `cache.redis_url` (optionnel)
  - Monitoring cache hit rate (logs)
  - **Deliverable :** -50% temps scoring (5 min → 2.5 min)

---

#### Mois 3 (Semaines 9-12) : Polish Qualité + Tests E2E

**Sprint 5 (Sem 9-10) : Tests E2E Playwright - 8 SP**

**Semaine 9-10 :**
- [P1] **Tests E2E Playwright** (8 SP)
  - Setup Playwright
  - Test flow : Navigation semaines (1 test)
  - Test flow : Recherche + résultats (1 test)
  - Test flow : Filtres catégories (1 test)
  - Test flow : Onglets type contenu (1 test)
  - Test flow : Click article → open new tab (1 test)
  - **Deliverable :** Flows critiques couverts

**Sprint 6 (Sem 11-12) : Polish UX & Optimisations - 13 SP**

**Semaine 11-12 :**
- [UX] **Mobile UX Audit & Fixes** (3 SP)
  - Audit responsive design (iPhone, iPad, Android)
  - Fix touch targets < 48px
  - Améliorer navigation mobile (burger menu si nécessaire)
  - Test scroll performance
  - **Deliverable :** Mobile Lighthouse score > 85

- [UX] **Accessibilité (a11y) Basics** (2 SP)
  - Audit WAVE (WebAIM)
  - Contraste couleurs (WCAG AA)
  - Labels ARIA manquants
  - Navigation clavier (Tab order)
  - **Deliverable :** Zéro erreurs a11y critiques

- [P2] **Infrastructure & Perf** (8 SP)
  - Activer Dependabot (1 SP)
  - Créer branche staging + deploy auto (5 SP)
  - Audit Lighthouse + fixes (atteindre > 90) (2 SP)
  - **Deliverable :** Perf Desktop > 90, Mobile > 85

---

### 🏁 Fin Phase 1 (Mois 3) : Checkpoint (UX + Contenu) & Qualité

**Résultats Attendus (Technique) :**
- ✅ Abstraction LLM (risque Groq mitigé)
- ✅ Monitoring Sentry actif (zéro bugs silencieux)
- ✅ Tests frontend 40-50% + E2E flows
- ✅ CI/CD tests automatiques
- ✅ Cache Redis (-50% temps scoring)
- ✅ Staging environment
- ✅ Dependabot CVE scanning

**Résultats Attendus (UX) :**
- ✅ Performance Desktop > 90 Lighthouse
- ✅ Performance Mobile > 85 Lighthouse
- ✅ Mobile UX fluide (touch, scroll, responsive)
- ✅ Accessibilité basics (zéro erreurs critiques)
- ✅ Temps recherche < 2 secondes
- ✅ Zéro bugs utilisateurs signalés

**Résultats Attendus (Contenu & Pertinence) :**
- ✅ **Ratio signal/bruit amélioré de 20-30%** (vs baseline)
- ✅ Seuils scoring optimisés par catégorie (moins de faux positifs)
- ✅ Anti-bruit filtering affiné (marketing, beginner)
- ✅ 5-10 nouvelles sources pertinentes ajoutées
- ✅ Audit pertinence 100 articles (documentation faux positifs/négatifs)

**Score Santé Projeté :** 73/100 → **87/100** ✅ (gain +2 points grâce pertinence)

**Décision Go/No-Go :**
- [ ] UX, contenu et qualité satisfaisants → Passer Phase 2 (Features Avancées)
- [ ] Pertinence insuffisante → +1 sprint amélioration scoring
- [ ] Besoin polish UX supplémentaire → +1 mois
- [ ] Feedback users négatif → Itérer avant Phase 2

---

### Phase 2 : EXPÉRIENCE UTILISATEUR AVANCÉE (Mois 4-7)

**Objectif :** Personnaliser l'expérience, comprendre les besoins users, rendre le site indispensable

**Focus :** Personnalisation, Engagement, User Insights, Feedback loops

**Pourquoi ces features :**
- **Auth/Accounts** → Sauvegarder préférences utilisateur, synchroniser entre devices
- **Personnalisation** → Veille adaptée aux intérêts de chacun (vs générique)
- **Analytics** → Comprendre ce qui marche, améliorer continuellement
- *(Bonus: infrastructure billing préparée mais optionnelle, non activée)*

**Timeline :** 16 semaines (si 20% temps)
**Total SP :** ~68 SP

---

#### Mois 4 (Semaines 13-16) : Comptes Utilisateurs & Préférences Sauvegardées

**Sprint 7-8 (Sem 13-16) : User Accounts (UX Benefit: Sync préférences) - 21 SP**

**Bénéfice Utilisateur :** Sauvegarder ses préférences (catégories favorites, filtres), synchroniser entre devices (mobile/desktop)

**Semaine 13-16 (4 semaines) :**
- [UX] **NextAuth.js Integration** (21 SP)
  - Setup NextAuth.js (providers : Email, Google, GitHub)
  - User model (id, email, name, image, préférences)
  - Session management (JWT)
  - Sauvegarde préférences par user (catégories, filtres)
  - Synchronisation automatique entre devices
  - *(Bonus: Workspace/Team support préparé pour futur partage)*
  - **Deliverable :** Users peuvent créer compte, sauvegarder préférences, sync entre devices

---

#### Mois 5 (Semaines 17-20) : Veille Personnalisée à Vos Intérêts

**Sprint 9-10 (Sem 17-20) : Personnalisation Avancée (UX Benefit: Pertinence 100%) - 13 SP**

**Bénéfice Utilisateur :** Articles adaptés à VOS intérêts, pas une veille générique. Gain de temps maximum.

**Semaine 17-20 (4 semaines) :**
- [CONTENU + UX] **Personnalisation Intelligente** (13 SP)
  - **Profil utilisateur** : topics préférés (ML, Orchestration, Cloud, etc.)
  - **Sources custom** (ajouter vos propres feeds RSS)
  - **Scoring personnalisé** : boost topics préférés dans calcul `final_score`
    - Exemple: Si user préfère "ML", articles ML reçoivent bonus +10 points
    - Seuils adaptatifs par user (vs seuils globaux)
  - **Filtres sauvegardés** ("Mes recherches") - accès rapide
  - **Digest email optionnel** (résumé hebdo personnalisé dans inbox)
  - **Mode "Focus"** : uniquement vos catégories favorites
  - **Blacklist keywords** : masquer sujets non pertinents pour vous
  - **Deliverable :** Chaque user voit SA veille, pertinence 100% personnalisée

---

#### Mois 6 (Semaines 21-24) : Comprendre les Utilisateurs & Améliorer

**Sprint 11-12 (Sem 21-24) : User Insights & Feedback (UX Benefit: Amélioration Continue) - 13 SP**

**Bénéfice Utilisateur :** Site qui s'améliore chaque semaine basé sur ce que VOUS utilisez réellement.

**Semaine 21-24 (4 semaines) :**
- [CONTENU + UX] **User Insights & Feedback Loops** (13 SP)
  - **Feedback pertinence** : bouton "Article utile ?" (👍/👎) sur chaque article
    - Stockage feedback par article_id
    - Analyse articles mal notés (faux positifs à éliminer)
    - Réajustement scoring basé sur feedback réel
  - **Tracking anonyme** : articles populaires, recherches fréquentes
  - **Dashboard insights** : quels topics/sources intéressent le plus
  - **Sondages optionnels** ("Trop de bruit ?", "Catégories manquantes ?")
  - **Changelog public** (voir les améliorations scoring/sources chaque semaine)
  - **Privacy-first** : opt-out tracking, zéro data vendue
  - **Amélioration ML scoring** : utiliser feedback pour fine-tuner embeddings
  - **Deliverable :** Boucle feedback → amélioration pertinence continue basée sur usage réel

---

#### Mois 7 (Semaines 25-28) : ⚙️ Infrastructure Optionnelle (Billing - Optionnel)

**Sprint 13-14 (Sem 25-28) : [OPTIONNEL] Préparation Monétisation Future - 21 SP**

**Note :** Cette étape est **100% optionnelle** et peut être **skippée** ou **reportée après M9**.
Elle prépare l'infrastructure pour monétiser un jour, SI vous décidez de le faire. Pas obligatoire pour excellente UX.

**Alternative recommandée si pas prioritaire :**
- **Skip** et passer directement à Phase 3 (Polish UX Continu)
- Ou investir ces 21 SP dans **plus de features UX** (mode sombre, export PDF, notifications, mobile app, etc.)

**Si vous voulez quand même préparer billing (pour future optionnalité) :**
- [INFRA] **Stripe Integration (Code Ready, OFF)** (21 SP)
  - Stripe integration (Checkout, Customer Portal)
  - Plans conceptuels : Free, Pro, Team (pricing à définir plus tard)
  - Paywalls code (dormants, jamais activés)
  - **CRITIQUE :** Code ready MAIS billing **100% disabled** (env var `BILLING_ENABLED=false`)
  - **Deliverable :** Infrastructure dormante, activation possible en 1 ligne (si besoin un jour)

---

### 🏁 Fin Phase 2 (Mois 7) : Checkpoint (UX + Contenu) Avancée

**Résultats Attendus (UX) :**
- ✅ Comptes utilisateurs fonctionnels (sync préférences)
- ✅ Personnalisation complète (filtres, sauvegardes, mode focus)
- ✅ Feedback loops actifs (users peuvent améliorer le site)
- ✅ Insights sur usage réel (améliorations data-driven)
- ✅ Changelog public (transparence sur améliorations)
- (Optionnel) Billing infrastructure préparée (dormante)

**Résultats Attendus (Contenu & Pertinence) :**
- ✅ **Scoring personnalisé** par user (boost topics préférés)
- ✅ **Sources custom** par user (ajout RSS personnels)
- ✅ **Feedback pertinence** actif (👍/👎 sur articles)
- ✅ **Amélioration ML scoring** basée sur feedback réel
- ✅ Blacklist keywords par user (masquer sujets non pertinents)
- ✅ **Pertinence perçue > 90%** (mesure via feedback)

**État Produit :** 🎯 **Site Indispensable pour Users** - Personnalisé (UX + Contenu), amélioration continue

**Critères Succès :**
- ✅ Users reviennent chaque semaine (rétention > 70%)
- ✅ **"Veille utile cette semaine" > 80%** (sondage hebdo)
- ✅ Feedback positif global (NPS > 50)
- ✅ **Feedback pertinence articles > 90%** (ratio 👍/👎)
- ✅ Temps passé par session en hausse
- ✅ Articles ouverts/affichés > 30%

**Décision Phase 3 :**
- [ ] UX + Contenu excellents, users adorent → Polish continu (Phase 3)
- [ ] Pertinence insuffisante → +1 sprint amélioration scoring/sources
- [ ] Users veulent plus features → Backlog features (UX + Contenu) additionnelles
- [ ] Opportunité monétisation évidente → Optionnellement activer billing (pas obligatoire)

---

### Phase 3 : POLISH CONTINU & FEATURES UX BONUS (Mois 8-9+)

**Objectif :** Améliorer l'expérience continuellement, ajouter features demandées par users

**Focus :** UX polish, Features bonus, Amélioration continue basée feedback users

**Timeline :** Flexible, continu
**Total SP :** Dépend des priorités users

**Options pour Phase 3 (choisir selon feedback Phase 2) :**

---

#### Option A : Features UX Bonus (Recommandé)

**Focus :** Ajouter features que les users demandent le plus (basé sur feedback Phase 2)

**Exemples Features (UX + Contenu) - Choisir 3-4 selon demande users :**

**Sprint 15-16 (Sem 29-32) : Features Bonus Populaires - 18-23 SP**

**Catégorie UX :**
- **Mode Sombre** (3 SP)
  - Toggle dark/light mode
  - Préférence sauvegardée par user
  - Design moderne et accessible

- **Export PDF Digest Hebdo** (5 SP)
  - Générer PDF du digest hebdo
  - Partage facile avec équipe
  - Branding configurable

- **Notifications Slack/Discord** (5 SP)
  - Webhook résumé hebdo dans Slack
  - Configuré par user (optionnel)
  - Résumé top articles de la semaine

- **Bookmarks & Collections** (5 SP)
  - Sauvegarder articles favoris
  - Organiser en collections ("À lire", "Références", etc.)
  - Synchronisé entre devices

- **Mobile PWA** (8 SP)
  - Progressive Web App (installable)
  - Offline support (service worker)
  - Notifications push (optionnel)

- **Partage Social Optimisé** (3 SP)
  - Open Graph tags
  - Twitter Cards
  - Copy link with preview

**Catégorie Contenu & Pertinence :**
- **🎯 Amélioration Résumés LLM** (5 SP)
  - Résumés plus concis et structurés
  - Extraction points clés (bullets)
  - Détection code snippets importants
  - A/B test différents prompts LLM

- **🎯 Expansion Sources Automatique** (5 SP)
  - Crawler GitHub trending repos (data engineering)
  - Intégrer Reddit r/dataengineering hot posts
  - Hacker News (tag: data/databases)
  - Auto-découverte RSS via OPML import

- **🎯 Détection Tendances** (8 SP)
  - Identifier topics montants (spike mentions)
  - Section "Trending This Week"
  - Alertes sur technologies émergentes
  - Graph évolution popularité tools

- **🎯 Amélioration Classification LLM** (3 SP)
  - Fine-tuning prompts basé sur feedback users
  - Multi-label categories (vs single)
  - Confidence score affiché
  - Permettre recatégorisation manuelle

**Deliverable :** Features bonus (UX + Contenu) demandées par users

---

#### Option B : Monétisation (100% Optionnel)

**⚠️ IMPORTANT :** Cette option n'est recommandée QUE SI :
- Users demandent explicitement des features payantes
- Vous avez besoin de financer infrastructure (coûts serveur élevés)
- Opportunité commerciale évidente

**Sinon, préférer Option A (Features UX) ou continuer gratuitement.**

**Si vous choisissez quand même de monétiser :**

**Sprint 15 (Sem 29-30) : Activation Billing (si billing préparé en M7) - 5 SP**
- Activer `BILLING_ENABLED=true`
- Onboarding flow payant
- Pricing page simple
- FAQ billing

**Sprint 16 (Sem 31-32) : Marketing Soft Launch - 3 SP**
- Annonce communauté existante
- Post Reddit/LinkedIn
- Outreach beta users

---

#### Mois 9+ : Amélioration Continue (Permanent)

**Sprint 17-18+ (Sem 33-36+) : Itération Basée Feedback Users**

**Mode permanent : Amélioration continue chaque semaine**

**Boucle hebdomadaire recommandée :**
1. **Lundi** : Review feedback users semaine précédente
2. **Mardi-Jeudi** : Implémenter 1-2 quick wins UX
3. **Vendredi** : Test + deploy améliorations
4. **Samedi-Dimanche** : Repos (ou monitoring passif)

**Exemples itérations continues :**
- **Quick Fixes UX** (basé feedback)
  - Améliorer contraste couleurs (a11y)
  - Optimiser recherche (pertinence)
  - Fixer bugs signalés
  - Améliorer onboarding

- **Optimisations Contenu & Pertinence** (prioritaire chaque semaine)
  - Analyser feedback pertinence articles (👍/👎)
  - Ajuster seuils scoring basé sur faux positifs/négatifs
  - Ajouter/retirer sources selon qualité réelle
  - Améliorer prompts LLM (classification + résumés)
  - Tester nouveaux feeds RSS découverts
  - Affiner anti-bruit filtering (marketing, beginner)

- **Optimisations Performance Technique**
  - Réduire temps chargement
  - Optimiser crawling (parallélisation)
  - Cache warming

- **Nouvelles Features Légères** (demandes users)
  - Nouveaux filtres
  - Export formats additionnels
  - Intégrations (Notion, Obsidian, etc.)

**Métriques Suivi (UX + Contenu) :**
- **Pertinence** : Ratio 👍/👎 sur articles (> 90%)
- **Pertinence** : % articles ouverts vs affichés (> 30%)
- **Rétention** : Hebdomadaire (> 70%)
- **Satisfaction** : NPS (Net Promoter Score > 50)
- **Engagement** : Temps passé par session
- **Qualité sélection** : Feedback "veille utile cette semaine" (> 80%)

---

### 🏁 Fin Phase 3 (Mois 9+) : Site d'Excellence UX

**Résultats Attendus (UX Excellence) :**
- ✅ Site fiable, rapide, agréable à utiliser
- ✅ Personnalisation complète par user
- ✅ Feedback loops actifs (amélioration continue)
- ✅ Features bonus demandées implémentées
- ✅ Communauté active et satisfaite
- (Optionnel) Monétisation activée si pertinent

**Métriques Succès (UX + Contenu) :**
- 🎯 **Pertinence articles > 90%** (ratio 👍/👎 feedback users)
- 🎯 **"Veille utile cette semaine" > 80%** (sondage hebdo)
- 🎯 Rétention hebdomadaire > 70%
- 🎯 NPS (Net Promoter Score) > 50
- 🎯 Performance Lighthouse > 90 (desktop + mobile)
- 🎯 Temps passé par visite en hausse
- 🎯 % articles ouverts vs affichés > 30%
- 🎯 Bouche-à-oreille positif (partages, recommandations)
- 🎯 Zéro bugs critiques signalés

**État Final :** 🌟 **Site Indispensable** - Les utilisateurs ne peuvent plus s'en passer
- **Contenu pertinent** : Articles vraiment utiles, zéro bruit
- **Expérience excellente** : Rapide, agréable, accessible

---

## 📊 Vue d'Ensemble Timeline (Flexible, UX + Contenu First)

```
Mois 1-3 : FONDATIONS (UX + CONTENU) & QUALITÉ 🏗️
├─ M1 : Abstraction LLM + Monitoring + Tests frontend
├─ M2 : 🎯 Amélioration Pertinence + CI/CD + Cache Redis
│       • Audit scoring, anti-bruit, seuils, sources
└─ M3 : Tests E2E + Staging + Mobile UX + Accessibilité
Résultat : Site fiable, rapide, accessible + Articles pertinents ✅

Mois 4-7 : EXPÉRIENCE UTILISATEUR AVANCÉE (UX + CONTENU) 🎯
├─ M4 : Comptes utilisateurs (sync préférences)
├─ M5 : Personnalisation (scoring adapté, sources custom)
├─ M6 : Feedback loops (👍/👎 pertinence, amélioration ML)
└─ M7 : [OPTIONNEL] Billing infrastructure (dormante)
Résultat : Site personnalisé, pertinence 100%, indispensable ✅

Mois 8-9+ : POLISH CONTINU & FEATURES BONUS 🌟
├─ M8-9 : Option A (Recommandé) - Features UX + Contenu
│         • UX: Mode sombre, Export PDF, PWA, Bookmarks
│         • Contenu: Résumés améliorés, Détection tendances, Sources auto
│
└─ M8-9 : Option B (Optionnel) - Monétisation si pertinent
          • Activation billing, Marketing soft launch

Résultat : Site d'excellence (UX + Contenu), users adorent ✅
```

**Timeline : Flexible** - Pas de deadline monétisation
**Objectif #1 :** Faire un site utile avec une vraie bonne expérience pour les utilisateurs

**2 Piliers Indissociables :**
1. 🎨 **Expérience Utilisateur** - Site rapide, agréable, accessible
2. 📊 **Qualité Contenu & Pertinence** - Articles vraiment utiles, zéro bruit

---

## 🎯 Actions Immédiates (Cette Semaine)

### Semaine 1 : Abstraction LLM (P0 CRITIQUE) ⚠️

**Pourquoi maintenant :**
- Risque mortel (Groq discontinué = projet mort)
- Quick Win (3 SP = 1-2 jours)
- Bloque rien d'autre (peut paralléliser après)

**Étapes :**

**Jour 1 : Design + Interface**
1. Créer `backend/llm_provider.py` :
```python
from abc import ABC, abstractmethod
from typing import Dict, Any

class LLMProvider(ABC):
    """Interface pour providers LLM interchangeables."""

    @abstractmethod
    def classify(self, title: str, summary: str, categories: list) -> Dict[str, Any]:
        """Classifie un article.

        Returns:
            {
                "category_key": str,
                "confidence": float,
                "reasoning": str
            }
        """
        pass

    @abstractmethod
    def summarize(self, context: str, instructions: str) -> str:
        """Génère un résumé.

        Returns:
            str: Résumé markdown formaté
        """
        pass


class GroqProvider(LLMProvider):
    """Provider Groq (actuel)."""

    def __init__(self, api_key: str, model: str = "llama-3.1-8b-instant"):
        import openai
        self.client = openai.OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=api_key
        )
        self.model = model

    def classify(self, title, summary, categories):
        # Code existant classify_llm.py
        ...

    def summarize(self, context, instructions):
        # Code existant summarize_week_llm.py
        ...


class OpenAIProvider(LLMProvider):
    """Provider OpenAI (fallback si Groq down)."""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        import openai
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model

    def classify(self, title, summary, categories):
        # Même logique que Groq
        ...

    def summarize(self, context, instructions):
        # Même logique que Groq
        ...


class OllamaProvider(LLMProvider):
    """Provider Ollama (local, zéro coût)."""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.1"):
        import openai
        self.client = openai.OpenAI(
            base_url=f"{base_url}/v1",
            api_key="ollama"  # Dummy key
        )
        self.model = model

    def classify(self, title, summary, categories):
        # Même logique
        ...

    def summarize(self, context, instructions):
        # Même logique
        ...


def get_provider(config: dict) -> LLMProvider:
    """Factory pour créer le bon provider depuis config.

    Args:
        config: config.yaml parsé (section llm)

    Returns:
        LLMProvider instance

    Example config.yaml:
        llm:
          provider: groq  # ou openai, ou ollama
          groq:
            api_key_env: GROQ_API_KEY
            model: llama-3.1-8b-instant
          openai:
            api_key_env: OPENAI_API_KEY
            model: gpt-4o-mini
          ollama:
            base_url: http://localhost:11434
            model: llama3.1
    """
    provider_name = config.get("provider", "groq")

    if provider_name == "groq":
        import os
        api_key = os.getenv(config["groq"]["api_key_env"])
        model = config["groq"].get("model", "llama-3.1-8b-instant")
        return GroqProvider(api_key, model)

    elif provider_name == "openai":
        import os
        api_key = os.getenv(config["openai"]["api_key_env"])
        model = config["openai"].get("model", "gpt-4o-mini")
        return OpenAIProvider(api_key, model)

    elif provider_name == "ollama":
        base_url = config["ollama"].get("base_url", "http://localhost:11434")
        model = config["ollama"].get("model", "llama3.1")
        return OllamaProvider(base_url, model)

    else:
        raise ValueError(f"Unknown LLM provider: {provider_name}")
```

**Jour 2 : Refactor + Config + Tests**

2. Refactor `classify_llm.py` :
```python
from llm_provider import get_provider

# Load config
with open("config.yaml") as f:
    config = yaml.safe_load(f)

# Get provider
provider = get_provider(config["llm"])

# Use provider
result = provider.classify(title, summary, categories)
```

3. Refactor `summarize_week_llm.py` (même pattern)

4. Update `config.yaml` :
```yaml
llm:
  provider: groq  # Switchable ici
  groq:
    api_key_env: GROQ_API_KEY
    model: llama-3.1-8b-instant
  openai:
    api_key_env: OPENAI_API_KEY
    model: gpt-4o-mini
  ollama:
    base_url: http://localhost:11434
    model: llama3.1
```

5. Tests :
```python
# test_llm_provider.py
def test_switch_provider_groq():
    config = {"provider": "groq", "groq": {...}}
    provider = get_provider(config)
    assert isinstance(provider, GroqProvider)

def test_switch_provider_openai():
    # ...

def test_fallback_if_groq_down():
    # Mock Groq failure → switch OpenAI
    # ...
```

6. Documentation README :
```markdown
## LLM Provider Configuration

Le système supporte 3 providers LLM interchangeables :

**Groq (défaut, gratuit) :**
```yaml
llm:
  provider: groq
  groq:
    api_key_env: GROQ_API_KEY
```

**OpenAI (fallback si Groq down) :**
```yaml
llm:
  provider: openai
  openai:
    api_key_env: OPENAI_API_KEY
    model: gpt-4o-mini  # Moins cher que gpt-4
```

**Ollama (local, zéro coût) :**
1. Install Ollama : https://ollama.com
2. Download model : `ollama pull llama3.1`
3. Config :
```yaml
llm:
  provider: ollama
  ollama:
    base_url: http://localhost:11434
    model: llama3.1
```

**Liverable Semaine 1 :**
- ✅ Abstraction LLM provider
- ✅ 3 providers (Groq, OpenAI, Ollama)
- ✅ Config YAML switchable
- ✅ Tests provider switching
- ✅ Docs README
- ✅ **Risque Groq mitigé** ⚠️ → ✅

---

## 📈 Tracking & KPIs par Phase

### Phase 1 (Mois 1-3) : Qualité

**KPIs Techniques :**
- Score Santé : 73/100 → 85/100
- Coverage tests : Backend 60% + Frontend 50% + E2E flows
- Performance Lighthouse : 70-80 → 90+
- Monitoring : 0 erreurs silencieuses (Sentry actif)
- Temps scoring : 10 min → 5 min (cache Redis)

**Deliverables :**
- [ ] Abstraction LLM (risque mitigé)
- [ ] Monitoring Sentry actif
- [ ] Tests > 70% coverage
- [ ] CI/CD tests automatiques
- [ ] Cache Redis functional
- [ ] Perf > 90 Lighthouse
- [ ] Staging env déployé

---

### Phase 2 (Mois 4-7) : Expérience Utilisateur Avancée

**KPIs UX :**
- Comptes créés : 10+ users inscrits (opt-in)
- Personnalisation : 80%+ users configurent profil
- Feedback actif : 50%+ users donnent feedback
- Rétention : 70%+ users reviennent chaque semaine
- Satisfaction : NPS > 50

**Deliverables :**
- [ ] Comptes utilisateurs (sync préférences)
- [ ] Personnalisation complète
- [ ] Feedback loops actifs
- [ ] User insights dashboards
- (Optionnel) Billing infrastructure préparée

---

### Phase 3 (Mois 8-9+) : Polish Continu & Features Bonus

**KPIs UX :**
- Rétention hebdomadaire : > 70%
- NPS : > 50 (utilisateurs très satisfaits)
- Performance : Lighthouse > 90 maintenu
- Engagement : Temps par visite en hausse
- Bouche-à-oreille : Partages/recommandations organiques
- Features utilisées : > 80% users utilisent personnalisation

**Deliverables (Option A - Recommandé) :**
- [ ] Mode sombre implémenté
- [ ] Export PDF fonctionnel
- [ ] PWA installable
- [ ] Bookmarks & collections
- [ ] Notifications configurables
- [ ] Améliorations continues basées feedback

**Deliverables (Option B - Optionnel) :**
- [ ] Billing activé (si pertinent)
- [ ] Marketing soft launch
- [ ] Support communauté

---

## 🔄 Revue & Ajustements

### Fréquence de Revue

**Hebdomadaire (Chaque Lundi) :**
- Review tasks semaine précédente
- Plan semaine suivante
- Ajuster si blocages

**Mensuelle (Fin de Mois) :**
- Review sprint/phase
- Métriques KPIs
- Décision Go/No-Go phase suivante

**Prochaine revue majeure :** Fin Mois 3 (Phase 1 Qualité)
- Décider si qualité suffisante → Go Phase 2
- Ou besoin +1 mois polish

---

## 🎯 Résumé Exécutif

**Objectif #1 (PRIORITÉ ABSOLUE) :**
> **"Faire un site utile avec une vraie bonne expérience pour mes utilisateurs"**

**Cela signifie 2 piliers indissociables :**
1. 🎨 **Expérience Utilisateur (UX)** - Site rapide, agréable, accessible
2. 📊 **Qualité Contenu & Pertinence** - Articles vraiment utiles, moins de bruit, meilleur scoring

**Stratégie :** Excellence (UX + Contenu) → Engagement Utilisateurs → (Optionnel) Monétisation

**Timeline :** Flexible, pas de deadline monétisation

**Phases :**
1. **Mois 1-3 :** Fondations (UX + Contenu) & Qualité
   - Dette tech, tests, perf, mobile, a11y
   - 🎯 **Amélioration pertinence** (audit scoring, anti-bruit, seuils, sources)
2. **Mois 4-7 :** Expérience Utilisateur Avancée (UX + Contenu)
   - Personnalisation (scoring adapté, sources custom)
   - Feedback loops (👍/👎 pertinence, amélioration ML)
3. **Mois 8-9+ :** Polish Continu & Features Bonus
   - UX: Mode sombre, Export PDF, PWA, Bookmarks
   - Contenu: Résumés améliorés, Détection tendances, Sources auto

**Quick Win Immédiat :** Abstraction LLM (Semaine 1, 3 SP) ⚠️

**Effort Estimé :**
- Phase 1 : ~65 SP (qualité + UX basics + pertinence)
- Phase 2 : ~47 SP (UX + Contenu avancés, billing optionnel)
- Phase 3 : Variable (selon demandes users)

**Velocity :** 5-8 SP/sprint (20% temps)

**Date "Site d'Excellence" Projeté :** 7-9 mois (flexible)

**Monétisation :** Optionnelle, quand/si pertinent - Pas une priorité

---

**🚀 Prochaine Action Immédiate : Abstraction LLM (Cette Semaine)**

Voir détails "Actions Immédiates (Cette Semaine)" ci-dessus.

---

*Roadmap créée le : 2025-12-20*
*Mise à jour : 2025-12-20 (Alignement sur objectif UX-First)*
*Basée sur : Vos 10 réponses + 4 décisions stratégiques + clarification objectif #1*
*Revue prochaine : Fin Mois 3 (checkpoint UX & qualité)*

---

## 📝 Note sur le Changement de Stratégie

**Version initiale (avant clarification) :**
- Focus : Produit commercial prêt en 9 mois
- Phases : Qualité → Features Commerciales → Monétisation
- Deadline : Lancement commercial M9

**Version mise à jour (après clarification objectif #1) :**
- **Focus : "Faire un site utile avec une vraie bonne expérience pour mes utilisateurs"**
- **2 Piliers :** 🎨 UX (Site rapide, agréable) + 📊 Contenu (Articles pertinents, zéro bruit)
- Phases : Excellence (UX + Contenu) → Engagement Utilisateurs → (Optionnel) Monétisation
- Timeline : Flexible, pas de deadline monétisation
- Monétisation : Optionnelle, quand/si pertinent - Pas une priorité

**Changements clés :**
1. ✅ **Ajout pilier Contenu & Pertinence** (équivalent importance vs UX)
2. ✅ Phase 1 enrichie : Ajout Mobile UX + Accessibilité + **Sprint Amélioration Pertinence (5 SP)**
3. ✅ Phase 2 renommée : "Features Commerciales" → "Expérience Utilisateur Avancée (UX + Contenu)"
4. ✅ Phase 2 reframed : Auth/Personnalisation/Analytics présentées comme features UX + Contenu
5. ✅ Phase 2 M5 : Personnalisation inclut **scoring adapté** (boost topics préférés)
6. ✅ Phase 2 M6 : Feedback loops incluent **feedback pertinence** (👍/👎 articles)
7. ✅ Phase 2 M7 : Billing infrastructure devenue 100% optionnelle (peut être skippée)
8. ✅ Phase 3 complètement revue : "Monétisation" → "Polish Continu & Features (UX + Contenu)"
9. ✅ Phase 3 Options Contenu : Résumés améliorés, Détection tendances, Expansion sources auto
10. ✅ KPIs changés : MRR/Churn → Rétention/NPS/Engagement/**Pertinence articles > 90%**
11. ✅ Critères succès : "Commercial-Ready" → "Site Indispensable (UX + Contenu)"

**Philosophie :**
> Construire le meilleur site de veille tech pour Data Engineers.
> **Sans pertinence du contenu, l'UX ne sert à rien.**
> **Sans bonne UX, même le meilleur contenu ne sera pas utilisé.**
> Si l'expérience ET le contenu sont excellents, la monétisation viendra naturellement (ou pas, et c'est ok).

**Vous gardez toute flexibilité :**
- Monétiser plus tard si besoin de financer infrastructure
- Rester gratuit si vous préférez (open source, communauté)
- Décider au fil de l'eau selon feedback users
