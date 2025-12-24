# Product Vision - Veille Tech Simplifiée

**Date** : 2025-12-24
**Branche** : exploration/simplified-daily-push
**Auteur** : Réflexion stratégique sur la direction produit

## Le Problème

### État actuel
Le système propose une interface riche avec :
- 20-30 articles par semaine
- 8 catégories filtrables
- Search fuzzy
- Filtres par type de contenu (Technical / REX)
- Archive complète

### Le paradoxe identifié
**L'objectif est de faciliter la veille tech, mais on crée une nouvelle surcharge cognitive.**

Les utilisateurs doivent :
1. Se connecter au site
2. Parcourir 20-30 articles
3. Choisir ce qui les intéresse
4. Filtrer, chercher, explorer

→ C'est exactement le problème qu'on essaie de résoudre !

### Exemples qui fonctionnent
Les produits de veille à succès font l'inverse :

| Produit | Format | Volume | Engagement |
|---------|--------|--------|------------|
| Morning Brew | Email quotidien | 3-5 articles | ~40% open rate |
| TLDR | Email quotidien | 3-5 articles | ~45% open rate |
| ByteByteGo | Email hebdo | 1 article long | ~35% open rate |
| Hacker Newsletter | Email hebdo | Top 10 | ~25% open rate |

**Pattern commun** : Push proactif + volume limité = engagement élevé

## Vision Simplifiée

### Principe directeur
**"Faire une chose, mais vraiment bien"**

Au lieu de donner tous les choix à l'utilisateur, faire le travail de curation jusqu'au bout :
- L'algo sélectionne le meilleur
- L'utilisateur reçoit une notification
- Action simple : Lire / Sauver / Skip

### Concept "Daily Tech Push"

```
┌─────────────────────────────────────────┐
│  📡 Ton article tech du jour            │
│                                         │
│  "ClickHouse vs DuckDB: When to Use    │
│   Each for Analytics"                   │
│                                         │
│  📊 Score: 92/100                       │
│  ⏱️  8 min de lecture                   │
│  🏷️  Warehouses & Query Engines        │
│                                         │
│  [Lire maintenant]  [Sauver]  [Skip]   │
│                                         │
│  Voir les 2 autres du jour →           │
└─────────────────────────────────────────┘
```

**Timing** : Notif à 8h00 (début de journée pro)

### Avantages

1. **Habitude claire** : Routine quotidienne vs visite occasionnelle
2. **Engagement mesurable** : Open rate, read time, skip patterns
3. **Différenciation** : Pas un agrégateur de plus, mais un coach tech
4. **Personnalisation progressive** : Apprend des skips/reads
5. **Moins de FOMO** : "Je n'ai qu'un article à lire" vs "J'ai raté 30 articles"

### Risques à gérer

| Risque | Mitigation |
|--------|------------|
| Article non pertinent = forte déception | Scoring + feedback loop |
| Monotonie catégorielle | Round-robin intelligent |
| Channel de notification (email fatigue) | PWA + push notifications |
| Personnalisation complexe | Onboarding simple (3-4 intérêts max) |

## Roadmap Progressive

### Phase 1 : Simplifier l'existant (Court terme - 1 semaine)

**Objectif** : Réduire la surcharge cognitive sans toucher au backend

**Actions** :
- Par défaut : afficher UNIQUEMENT le Top 3 de la semaine
- Bouton "Voir toute la sélection (XX articles)" pour explorateurs
- Supprimer la search bar (contre-productif)
- Simplifier les filtres (catégories uniquement, pas de content type tabs)
- Hero plus impactant : "Les 3 articles essentiels de la semaine"

**Impact** : UX plus claire, focus sur le meilleur contenu

### Phase 2 : Daily Digest Email (Moyen terme - 1 mois)

**Objectif** : Modèle push actif

**Spec technique** :
```yaml
schedule:
  frequency: daily
  time: "08:00"
  days: [mon, tue, wed, thu, fri]

content:
  main_article: 1  # Score le plus élevé non envoyé
  secondary: 1-2   # Round-robin des catégories

format:
  - Title + summary (100 chars)
  - Score badge
  - Read time
  - CTA : "Lire sur le site"

footer:
  - "Voir les archives"
  - "Gérer mes préférences"
```

**Backend changes** :
- Nouvelle table `user_preferences` (catégories préférées)
- Nouvelle table `sent_articles` (éviter doublons)
- Script `daily_digest.py` (sélection + email)
- Integration SendGrid/Mailgun

**Frontend changes** :
- Page `/preferences` pour gérer catégories
- Page `/unsubscribe`
- Archive accessible via email links

### Phase 3 : Personnalisation Adaptive (Long terme - 3 mois)

**Objectif** : Chaque utilisateur reçoit SON meilleur article

**Features** :
1. **Onboarding** :
   ```
   "Bienvenue ! Quels sujets t'intéressent ?"
   [Warehouses] [Orchestration] [ML/AI] [Python]
   (Choix : 2-4 max)
   ```

2. **Feedback loop** :
   - Track clicks (article ouvert = +1)
   - Track skips (skip = -0.5)
   - Adjust scoring weights par utilisateur

3. **Smart selection** :
   ```python
   final_score_personalized = (
       base_final_score * 0.7 +
       category_preference * 0.2 +
       click_history_similarity * 0.1
   )
   ```

4. **PWA + Push notifications** :
   - Alternative à l'email
   - Notification native mobile/desktop
   - Offline reading

## Options de Pivots

### Option A : Daily Push Radical
- 1 seul article par jour
- Email + PWA notification
- Archive minimaliste
- Focus sur la qualité absolue

**Pour** : Différenciation maximale, engagement fort
**Contre** : Risque si l'article ne plaît pas

### Option B : Hybrid Intelligent
- Email quotidien (1-2 articles)
- Site reste accessible pour exploration
- Best of both worlds

**Pour** : Flexibilité, phase de transition
**Contre** : Peut diluer le message

### Option C : Weekly Premium Digest
- 1 email le lundi avec Top 5 de la semaine
- Très curated, très qualitatif
- Analyse/synthesis ajoutée

**Pour** : Moins intrusif, meilleure curation
**Contre** : Moins d'habitude, engagement plus faible

## Recommandations

### Approche suggérée

**1. Court terme (cette branche)** : Implémenter Phase 1
- Simplifier le frontend drastiquement
- A/B test avec quelques utilisateurs
- Mesurer bounce rate + time on page

**2. Validation (2-4 semaines)** :
- Si Phase 1 améliore l'engagement → go Phase 2
- Sinon, itérer sur le format (weekly digest ?)

**3. Moyen terme** : Phase 2 avec email quotidien
- Commencer simple : 1 article/jour, pas de perso
- Mesurer open rate + click rate
- Si >25% open rate → go Phase 3

**4. Long terme** : Personnalisation si croissance utilisateurs
- Nécessite base utilisateurs significative (>100)
- Coût infra à considérer (emails, notifs push)

### Metrics de succès

| Metric | Actuel (estimé) | Target Phase 1 | Target Phase 2 |
|--------|----------------|----------------|----------------|
| Session duration | 2-3 min | 5-8 min | N/A (email) |
| Bounce rate | 60% | 40% | N/A |
| Email open rate | N/A | N/A | 30% |
| Click-through rate | N/A | N/A | 15% |

## Next Steps

1. **Valider la vision** avec stakeholders/early users
2. **Prototyper Phase 1** sur cette branche
3. **A/B test** : Version actuelle vs version simplifiée
4. **Décider** : Pivot complet ou évolution progressive

---

## Annexe : Concurrence

### Agrégateurs actuels
- Hacker News : Submersion d'info, pas de curation
- Reddit /r/programming : Idem
- Google Alerts : Spam, 0 intelligence
- Feedly : Outil, pas service

### Notre différenciation potentielle
- **Curation intelligente** : LLM + embeddings + scoring
- **Push proactif** : On vient à l'utilisateur
- **Volume maîtrisé** : 1-3 articles max/jour
- **Spécialisé data engineering** : Niche claire

---

**Conclusion** : La réflexion initiale est juste. Simplifier drastiquement et faire du push quotidien est probablement la meilleure direction. Cette branche sert à explorer cette hypothèse.
