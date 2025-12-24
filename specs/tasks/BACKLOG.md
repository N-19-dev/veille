# Backlog - Ce qui Reste à Faire

*Généré automatiquement depuis analyse du code - Date : 2025-12-20*

## 🔴 CRITICAL - Dette Technique (P0)

**Aucune dette critique détectée** ✅

Le code est globalement de bonne qualité, bien structuré et documenté.

---

## 🟠 HIGH PRIORITY (P1)

### [DEBT-001] Absence de tests frontend
**Type :** Dette Technique
**Priority :** P1
**Estimation :** 13 SP

**Problème actuel :**
Coverage frontend : 0%
Aucun test dans le projet React.

**Impact si non corrigé :**
- Risque de régressions UI non détectées
- Difficile d'ajouter features sans casser l'existant
- Pas de validation des filtres/recherche

**Actions :**
1. Setup Vitest
2. Tests composants critiques (App, SearchBar, CategoryFilter)
3. Tests utils (parse.ts, search.ts)
4. Tests E2E Playwright (search + filter + navigation flows)

**Fichiers concernés :**
- `frontend/` (tous composants)

**Critère de succès :**
- [ ] Coverage > 70%
- [ ] CI fails si coverage baisse
- [ ] Tests E2E couvrent flows principaux

---

### [DEBT-002] Pas de CI/CD pour tests
**Type :** Infrastructure
**Priority :** P1
**Estimation :** 5 SP

**Problème actuel :**
Tests backend existent (37 tests) mais ne tournent pas en CI.
Pas de validation automatique avant merge.

**Impact si non corrigé :**
- Tests manuels uniquement
- Risque de pusher du code cassé
- Pas de coverage tracking

**Actions :**
1. Ajouter step pytest dans `.github/workflows/backend-weekly.yml`
2. Fail workflow si tests échouent
3. Coverage report upload (Codecov ou GitHub Pages)
4. Ajouter step vitest (quand tests existent)

**Fichiers concernés :**
- `.github/workflows/backend-weekly.yml`
- `.github/workflows/deploy-frontend.yml`

**Critère de succès :**
- [ ] pytest tourne automatiquement en CI
- [ ] vitest tourne automatiquement en CI (après DEBT-001)
- [ ] Coverage badges dans README.md

---

### [DEBT-003] Embeddings non cachés (Redis)
**Type :** Performance
**Priority :** P1
**Estimation :** 8 SP

**Problème actuel :**
Embeddings recalculés à chaque run (500-1000 articles/semaine).
Model sentence-transformers chargé à chaque fois.

**Impact si non corrigé :**
- Performance : ~5-10 min gaspillées/run
- Coût CPU inutile
- Pas scalable (si 1000+ articles/semaine)

**Actions :**
1. Setup Redis (Docker local ou cloud)
2. Cache embeddings par hash(content)
3. TTL 30 jours (articles rarement recrawlés)
4. Fallback : calcul si cache miss
5. Monitoring cache hit rate

**Fichiers concernés :**
- `backend/analyze_relevance.py`

**Critère de succès :**
- [ ] Cache hit rate > 80%
- [ ] Temps scoring réduit de 50%
- [ ] Redis cloud gratuit (ex: Upstash free tier)

---

### [DEBT-004] Monitoring/Observability manquant
**Type :** Infrastructure
**Priority :** P1
**Estimation :** 8 SP

**Problème actuel :**
Aucun monitoring production.
Bugs/erreurs non détectés sauf si log crawl manuel.

**Impact si non corrigé :**
- Bugs production silencieux
- Pas d'alertes si feeds down
- Difficile de debugger problèmes users

**Actions :**
1. Intégrer Sentry (backend + frontend)
2. Alertes Slack si erreurs
3. Dashboard métriques (articles/semaine, sources down, erreurs)
4. Health check endpoint `/api/health`

**Fichiers concernés :**
- `backend/main.py` : Sentry init
- `frontend/src/main.tsx` : Sentry init
- `.github/workflows/` : variables Sentry

**Critère de succès :**
- [ ] Erreurs backend remontées dans Sentry
- [ ] Erreurs frontend remontées dans Sentry
- [ ] Alertes Slack si > 10 erreurs/run
- [ ] Dashboard métriques visualisable

---

## 🟡 MEDIUM PRIORITY (P2)

### [DEBT-005] Pas de staging environment
**Type :** Infrastructure
**Priority :** P2
**Estimation :** 5 SP

**Problème actuel :**
Test en production uniquement.
Pas d'environnement de staging pour valider features.

**Impact :**
- Risque de casser production lors de tests
- Pas de validation pre-prod
- Difficile de tester avec users beta

**Actions :**
1. Créer branche `staging`
2. Deploy automatique staging sur push `staging`
3. URL staging : `https://USERNAME.github.io/veille-staging/`
4. Variables env séparées (Sentry projects séparés)

**Critère de succès :**
- [ ] Staging déployé automatiquement
- [ ] Tests pré-prod sur staging avant merge main
- [ ] Users beta accès staging

---

### [DEBT-006] SQLite single-writer (pas de WAL)
**Type :** Performance
**Priority :** P2
**Estimation :** 2 SP

**Problème actuel :**
SQLite en mode journal classique (single-writer).
Contention si accès concurrents (rare mais possible).

**Impact :**
- Performance DB limitée
- Locks potentiels si API serveur activée

**Actions :**
1. Activer WAL mode : `PRAGMA journal_mode=WAL`
2. Configurer checkpoints
3. Tester performance avant/après

**Fichiers concernés :**
- `backend/veille_tech.py` : db_conn()

**Critère de succès :**
- [ ] WAL mode activé
- [ ] Pas de dégradation perf
- [ ] Locks réduits (si API serveur utilisée)

---

### [DEBT-007] Pas de Dependabot (CVE scanning)
**Type :** Sécurité
**Priority :** P2
**Estimation :** 1 SP

**Problème actuel :**
Dépendances non scannées automatiquement.
Risque de CVE non détectées.

**Impact :**
- Vulnérabilités potentielles
- Dépendances obsolètes

**Actions :**
1. Activer Dependabot (GitHub Settings → Security)
2. Configurer `.github/dependabot.yml`
3. Review + merge PRs Dependabot régulièrement

**Critère de succès :**
- [ ] Dependabot actif
- [ ] PRs automatiques pour updates
- [ ] Zéro CVE critiques/élevées

---

### [DEBT-008] Frontend JSON non paginé
**Type :** Performance
**Priority :** P2
**Estimation :** 5 SP

**Problème actuel :**
digest.json peut être > 500 KB si beaucoup d'articles.
Toutes les semaines chargées d'un coup.

**Impact :**
- Performance si > 100 semaines
- Bande passante gaspillée
- UX dégradée (latence)

**Actions :**
1. Paginer weeks.json (ex: 20 semaines/page)
2. Lazy load semaines anciennes
3. Compress JSON (gzip)
4. Virtualisation liste semaines (react-window)

**Fichiers concernés :**
- `frontend/src/App.tsx`
- `backend/analyze_relevance.py`

**Critère de succès :**
- [ ] Charge initiale < 200 KB
- [ ] Lazy load semaines anciennes
- [ ] UX fluide avec 100+ semaines

---

## 📊 Résumé du Backlog

| Catégorie | Nombre | Story Points |
|-----------|--------|--------------|
| Dette P0 (Critical) | 0 | 0 SP |
| Dette P1 (High) | 4 | 34 SP |
| Dette P2 (Medium) | 4 | 13 SP |
| **TOTAL** | **8** | **47 SP** |

**Estimation temps restant :** 2-3 sprints (4-6 semaines)

---

## 📈 Priorisation Suggérée

### Sprint 1 (2 sem) : Qualité & Tests

**Priorité : Stabilisation**

- [DEBT-001] Tests frontend - 13 SP
- [DEBT-002] CI/CD tests - 5 SP

**Total : 18 SP**

---

### Sprint 2 (2 sem) : Performance & Monitoring

**Priorité : Robustesse**

- [DEBT-004] Monitoring Sentry - 8 SP
- [DEBT-003] Cache Redis embeddings - 8 SP

**Total : 16 SP**

---

### Sprint 3 (2 sem) : Optimisations

**Priorité : Améliorations**

- [DEBT-005] Staging env - 5 SP
- [DEBT-006] SQLite WAL - 2 SP
- [DEBT-007] Dependabot - 1 SP
- [DEBT-008] Pagination JSON - 5 SP

**Total : 13 SP**

---

## 🚀 Roadmap Features (Hors Dette)

### v1.1 - Court Terme (après dette P1)

- [ ] Mode sombre - 3 SP
- [ ] Export PDF - 5 SP
- [ ] Notifications Slack - 5 SP
- [ ] Mobile UX fixes - 5 SP

**Total : 18 SP** (~1 sprint)

---

### v2.0 - Long Terme (6+ mois)

- [ ] API REST publique - 13 SP
- [ ] Dashboard analytics (tendances) - 21 SP
- [ ] Personnalisation utilisateur - 13 SP
- [ ] Recommandations ML - 21 SP
- [ ] Application mobile - 40 SP

**Total : 108 SP** (~5 sprints)

---

## 📝 Notes Importantes

### Tracking

**GitHub Projects recommandé :**
1. Créer project "Veille Tech Backlog"
2. Colonnes : Backlog / Sprint Current / In Progress / Review / Done
3. Importer tâches depuis ce fichier
4. Assigner à sprints

### Estimation

**Story Points (Fibonacci) :**
- 1 SP = 1-2h (trivial)
- 2 SP = half-day
- 3 SP = 1 jour
- 5 SP = 2-3 jours
- 8 SP = 1 semaine
- 13 SP = 2 semaines
- 21 SP = 3-4 semaines

### Velocity

**Assumé : 1 personne, 20% temps (1 jour/semaine)**
- Velocity : ~5-8 SP/sprint (2 semaines)
- Sprint 1 (18 SP) : ~4 semaines (si 50% temps)
- Sprint 2 (16 SP) : ~4 semaines (si 50% temps)
- Sprint 3 (13 SP) : ~3 semaines (si 50% temps)

**Total dette : 11 semaines si 50% temps, 22 semaines si 20% temps**

---

*Document généré le : 2025-12-20*
*À mettre à jour après chaque sprint*
