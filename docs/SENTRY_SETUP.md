# 🔍 Setup Sentry - Guide Complet

Ce guide explique comment configurer **Sentry** pour le monitoring d'erreurs du projet Veille Tech Crawling.

## 🎯 Pourquoi Sentry ?

**Sans Sentry** :
- ❌ Bugs silencieux en production
- ❌ Pas d'alerte quand un feed est down
- ❌ Difficile de debugger sans contexte

**Avec Sentry** :
- ✅ **Alertes temps réel** : Notification Slack si > 10 erreurs
- ✅ **Dashboard centralisé** : Toutes les erreurs en un coup d'œil
- ✅ **Contexte complet** : Stack trace, variables, environnement
- ✅ **Proactif** : Vous savez qu'il y a un problème avant les users

---

## 📝 Étape 1 : Créer un Compte Sentry (Gratuit)

1. **Aller sur** : https://sentry.io
2. **Créer un compte** (gratuit jusqu'à 5,000 erreurs/mois)
3. **Créer une Organisation** (ex: "veille-tech")

---

## 🐍 Étape 2 : Créer le Projet Backend (Python)

1. **Dans Sentry Dashboard** → Cliquer "Create Project"
2. **Sélectionner** : Platform = **Python**
3. **Nom du projet** : `veille-tech-backend`
4. **Alert frequency** : "Alert me on every new issue"
5. **Cliquer** "Create Project"

### Récupérer le DSN Backend

Après création, Sentry affiche :
```python
sentry_sdk.init(
    dsn="https://xxxxx@o0000.ingest.us.sentry.io/0000000",
    ...
)
```

**Copier le DSN** (l'URL `https://...`) → C'est votre `SENTRY_DSN_BACKEND`

**Ou retrouver le DSN plus tard** :
1. Settings → Projects → veille-tech-backend
2. Client Keys (DSN)
3. Copier le "DSN"

---

## ⚛️ Étape 3 : Créer le Projet Frontend (React)

1. **Dans Sentry Dashboard** → Cliquer "Create Project"
2. **Sélectionner** : Platform = **React**
3. **Nom du projet** : `veille-tech-frontend`
4. **Alert frequency** : "Alert me on every new issue"
5. **Cliquer** "Create Project"

### Récupérer le DSN Frontend

Même processus que backend, copier le DSN → C'est votre `SENTRY_DSN_FRONTEND`

---

## 🔧 Étape 4 : Configuration Locale

### Backend (.env)

Créer/éditer `backend/.env` :

```bash
# Sentry Backend (monitoring erreurs Python)
SENTRY_DSN_BACKEND=https://xxxxx@o0000.ingest.us.sentry.io/0000000
```

### Frontend (.env.local)

Créer `frontend/.env.local` :

```bash
# Sentry Frontend (monitoring erreurs React)
VITE_SENTRY_DSN_FRONTEND=https://yyyyy@o1111.ingest.us.sentry.io/1111111
```

**Note** : Les variables Vite doivent commencer par `VITE_`

---

## ☁️ Étape 5 : Configuration GitHub Actions

Pour que Sentry fonctionne en production (GitHub Actions), ajouter les secrets :

### Ajouter les Secrets GitHub

1. **Aller dans** : Votre repo GitHub → Settings → Secrets and variables → Actions
2. **Cliquer** "New repository secret"
3. **Ajouter** :
   - Name : `SENTRY_DSN_BACKEND`
   - Secret : (coller votre DSN backend)
4. **Répéter** pour :
   - Name : `SENTRY_DSN_FRONTEND`
   - Secret : (coller votre DSN frontend)

### Vérifier les Workflows

Les workflows GitHub Actions sont déjà configurés pour utiliser ces secrets :

**`.github/workflows/backend-weekly.yml`** :
```yaml
env:
  GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
  SENTRY_DSN_BACKEND: ${{ secrets.SENTRY_DSN_BACKEND }}
```

**`.github/workflows/deploy-frontend.yml`** :
```yaml
env:
  VITE_SENTRY_DSN_FRONTEND: ${{ secrets.SENTRY_DSN_FRONTEND }}
```

---

## 🔔 Étape 6 : Configurer les Alertes (Optionnel)

### Alertes Email

Par défaut, Sentry envoie un email à chaque nouvelle erreur.

**Configurer** :
1. Settings → Projects → veille-tech-backend → Alerts
2. "Create Alert Rule"
3. Condition : "When an issue is first seen"
4. Action : "Send a notification via email"

### Alertes Slack (Recommandé)

1. **Dans Sentry** : Settings → Integrations
2. **Chercher** "Slack" → Install
3. **Autoriser** Sentry à accéder à votre workspace Slack
4. **Créer Alert Rule** :
   - Condition : "When > 10 events in 1 hour"
   - Action : "Send a notification via Slack to #tech-alerts"

**Résultat** : Si > 10 erreurs en 1h, vous recevez :
```
⚠️ Sentry Alert: veille-tech-backend
25 errors in the last hour
ConnectionError: Feed "Databricks Blog" unreachable
View in Sentry →
```

---

## ✅ Étape 7 : Tester l'Installation

### Test Backend (Python)

Créer un fichier `test_sentry.py` :

```python
from sentry_init import init_sentry, capture_exception

# Initialiser Sentry
init_sentry(environment="development")

# Tester avec une erreur volontaire
try:
    1 / 0
except Exception as e:
    capture_exception(e)
    print("Erreur envoyée à Sentry !")
```

```bash
cd backend
source .venv/bin/activate
python test_sentry.py
```

**Vérifier** :
1. Aller dans Sentry Dashboard → veille-tech-backend → Issues
2. Vous devriez voir : "ZeroDivisionError: division by zero"
3. Cliquer dessus pour voir stack trace complète

### Test Frontend (React)

Ajouter un bouton de test dans `App.tsx` :

```typescript
<button onClick={() => {
  throw new Error("Test Sentry Frontend");
}}>
  Test Sentry
</button>
```

**Vérifier** :
1. Lancer `npm run dev`
2. Cliquer le bouton "Test Sentry"
3. Aller dans Sentry Dashboard → veille-tech-frontend → Issues
4. Vous devriez voir : "Error: Test Sentry Frontend"

---

## 📊 Utilisation Quotidienne

### Dashboard Sentry

**Tous les jours** (ou après chaque run du pipeline) :
1. Aller sur https://sentry.io
2. Vérifier le dashboard :
   - **Zéro erreur** ✅ → Tout va bien
   - **Nouvelles erreurs** 🔴 → Investiguer

### Exemples d'Erreurs à Surveiller

**Backend** :
- `ConnectionError` : Feed down → Retirer temporairement
- `Rate Limit` : Groq API saturée → Switcher vers OpenAI
- `JSONDecodeError` : LLM retourne JSON invalide → Améliorer prompt

**Frontend** :
- `TypeError` : Bug UI → Fix React component
- `Network Error` : JSON malformé → Fix backend export

---

## 💰 Limites du Plan Gratuit

**Gratuit (Developer Plan)** :
- ✅ Jusqu'à **5,000 erreurs/mois**
- ✅ **30 jours** de rétention
- ✅ **1 utilisateur**
- ✅ **Alertes email + Slack**

**Largement suffisant pour votre projet** (estimé : 50-200 erreurs/mois).

**Si dépassement** :
- Les erreurs les plus anciennes sont supprimées
- Upgrader vers plan payant : $26/mois (50K erreurs, 90 jours rétention)

---

## 🎯 Bonnes Pratiques

### 1. **Tags Custom**

Ajouter des tags pour filtrer les erreurs :

```python
from sentry_init import set_tag

set_tag("source", "databricks-blog")
set_tag("week_offset", "-1")
```

**Résultat** : Filter Sentry par `source=databricks-blog`

### 2. **Context Custom**

Ajouter du contexte pour débugger :

```python
from sentry_init import set_context

set_context("article", {
    "url": article_url,
    "title": article_title,
    "category": category_key
})
```

**Résultat** : En cas d'erreur, Sentry affiche ces infos

### 3. **Ignorer Certaines Erreurs**

Éditer `sentry_init.py` :

```python
ignore_errors=[
    KeyboardInterrupt,
    "ConnectionAbortedError",  # Erreurs réseau bénignes
]
```

### 4. **Environnements Séparés**

Distinguer dev vs prod :

```python
# Development
init_sentry(environment="development")

# Production
init_sentry(environment="production")
```

**Filter Sentry** : `environment:production`

---

## 🚀 Résultat Final

**Avant Sentry** :
```bash
$ cat logs/veille_tech.log | grep ERROR
[ERROR] Something went wrong...
# Vous découvrez le bug 1 semaine plus tard
```

**Après Sentry** :
```
📧 Email : "New issue: ConnectionError in veille_tech.py"
💬 Slack : "⚠️ 5 errors in the last 10 minutes"
📊 Dashboard : Graphique montrant spike d'erreurs
🔍 Cliquer → Stack trace + variables + solution suggérée
✅ Fix en 5 minutes au lieu de 1 semaine
```

---

## ❓ FAQ

**Q : Est-ce que Sentry ralentit l'application ?**
R : Non, overhead < 1ms par requête. Invisible pour l'utilisateur.

**Q : Mes données sensibles sont-elles envoyées à Sentry ?**
R : Par défaut, `send_default_pii=False` → Pas de données personnelles.
Vous contrôlez ce qui est envoyé via `set_context()`.

**Q : Puis-je self-host Sentry ?**
R : Oui, Sentry est open-source. Mais le SaaS gratuit suffit pour ce projet.

**Q : Que se passe-t-il si Sentry est down ?**
R : Votre app continue de fonctionner normalement. Les erreurs sont simplement loggées localement.

---

**✅ Setup terminé !**

Sentry est maintenant configuré. Les erreurs backend et frontend sont automatiquement capturées et vous recevez des alertes en temps réel.

**Prochaine étape** : Laisser tourner le pipeline et vérifier le dashboard Sentry régulièrement. 📊
