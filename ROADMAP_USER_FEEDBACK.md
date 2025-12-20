# Roadmap d'implémentation - Retours utilisateurs
**Date**: 2025-12-18
**Basé sur**: 14 réponses utilisateurs

## 📊 État des lieux : CE QUI EXISTE DÉJÀ

### ✅ Points forts actuels

**Sources & Contenu**
- ✅ **69 sources configurées** (blogs tech, engineering blogs, newsletters)
- ✅ **12 sources communautaires** de qualité (Joe Reis, Seattle Data Guy, etc.)
- ✅ **Détection REX automatique** (34 patterns : "how we built", "our experience", etc.)
- ✅ **Classification technique/rex** : articles communautaires vs corporate

**Catégorisation**
- ✅ **8 catégories thématiques** alignées avec les besoins utilisateurs :
  - 🏛️ Warehouses & Query Engines (Modern Data Stack)
  - 🔄 Orchestration, ETL & Data Movement
  - 📐 Data Modeling, Governance & Quality
  - 🗄️ Data Lakes, Storage & Formats
  - ☁️ Cloud, Infra & Observability
  - 🐍 Python, Analytics & Tools
  - 🤖 AI for Data Engineering (AI/LLM)
  - 📰 Tech / Cloud / IA News

**Filtrage qualité**
- ✅ **Scoring multi-critères** : sémantique (55%), source (20%), qualité (15%), tech (10%)
- ✅ **Seuils par catégorie** (55-58 pour le contenu principal, 70+ pour news)
- ✅ **Filtrage hors sujet** automatique (threshold 100)

**Interface**
- ✅ **Filtrage par type** : REX / Technical
- ✅ **Recherche** dans tous les articles
- ✅ **Top 3 hebdomadaire**

---

## ❌ CE QUI MANQUE (Demandes utilisateurs)

### 🔴 Priorité 1 - Filtrage "Anti-Bruit"

**Problème identifié par 64% des répondants** : tutos débutants et pubs indésirables

#### 1.1 Détecter et exclure les tutos débutants
- ❌ Mots-clés à détecter : "introduction to", "getting started", "tutorial for beginners", "hello world", "débuter avec"
- ❌ Patterns à filtrer : "step-by-step guide", "from scratch", "for dummies"
- ❌ Badge de niveau : Débutant/Intermédiaire/Avancé

#### 1.2 Détecter et exclure les publicités déguisées
- ❌ Identifier : mentions répétées de produits commerciaux
- ❌ Filtrer : liens affiliés, contenu sponsorisé
- ❌ Détecter : langage marketing ("révolutionnaire", "game-changer")

#### 1.3 Filtrer les news business non techniques
- ❌ Exclure : levées de fonds, acquisitions, nominations
- ❌ Conserver : annonces de nouvelles versions/features techniques

### 🟠 Priorité 2 - Nouvelles sources (50% utilisent ces plateformes)

- ❌ **Reddit** r/dataengineering (mentionné par 7 répondants)
- ❌ **HackerNews** (mentionné par 7 répondants)
- ❌ **LinkedIn posts** d'influenceurs Data (mentionné par 9 répondants)
- ❌ **YouTube** chaînes techniques (mentionné par quelques répondants)

### 🟡 Priorité 3 - Améliorations UX

- ❌ **Sources visibles** : afficher la source de chaque article
- ❌ **Filtres avancés** : par source, par niveau, par date
- ❌ **Bookmarks** : sauvegarder les articles intéressants
- ❌ **Mode digest** : newsletter hebdomadaire personnalisée
- ❌ **Historique de lecture** : marquer les articles lus

---

## 🎯 PLAN D'IMPLÉMENTATION PROGRESSIF

### Phase 1️⃣ : Quick Wins (Semaine 1-2)

**Objectif** : Améliorer le filtrage sans changer l'architecture

#### 1. Filtrage anti-bruit niveau débutant
```python
# Ajouter dans content_classifier.py
BEGINNER_KEYWORDS = [
    "introduction to", "getting started", "tutorial for beginners",
    "hello world", "step-by-step", "from scratch", "for dummies",
    "débuter avec", "introduction à", "premier pas"
]

def detect_beginner_content(title: str, content: str) -> bool:
    """Détecte si l'article est niveau débutant"""
    text = (title + " " + content).lower()
    return any(keyword in text for keyword in BEGINNER_KEYWORDS)
```

#### 2. Détection de contenu promotionnel
```python
MARKETING_KEYWORDS = [
    "game-changer", "revolutionary", "disruptive",
    "unlock", "transform", "revolutionize",
    "sponsored", "partner content", "affiliate"
]

def detect_promotional_content(title: str, content: str) -> int:
    """Score de marketing : 0-100"""
    text = (title + " " + content).lower()
    score = sum(10 for keyword in MARKETING_KEYWORDS if keyword in text)
    return min(score, 100)
```

#### 3. Badge de niveau technique dans le frontend
```typescript
// Ajouter dans ArticleCard.tsx
type TechLevel = 'beginner' | 'intermediate' | 'advanced';

const LevelBadge = ({ level }: { level: TechLevel }) => {
  const colors = {
    beginner: 'bg-green-100 text-green-800',
    intermediate: 'bg-yellow-100 text-yellow-800',
    advanced: 'bg-red-100 text-red-800'
  };
  return <span className={`badge ${colors[level]}`}>{level}</span>;
};
```

**Livrables** :
- [x] Détection automatique niveau débutant
- [x] Filtre anti-publicité
- [x] Badge de niveau visible sur chaque article
- [x] Exclusion automatique du contenu débutant

---

### Phase 2️⃣ : Nouvelles sources (Semaine 3-4)

**Objectif** : Intégrer Reddit et HackerNews

#### 1. Scraper Reddit r/dataengineering
```python
# Nouveau fichier: scrapers/reddit_scraper.py
import praw

def fetch_reddit_posts(subreddit: str, limit: int = 50):
    """Récupère les top posts de r/dataengineering"""
    reddit = praw.Reddit(...)
    posts = reddit.subreddit(subreddit).hot(limit=limit)

    return [{
        'title': post.title,
        'url': post.url,
        'score': post.score,
        'comments': post.num_comments,
        'created': post.created_utc
    } for post in posts]
```

#### 2. Scraper HackerNews
```python
# Nouveau fichier: scrapers/hackernews_scraper.py
import requests

def fetch_hackernews_top(limit: int = 50):
    """Récupère les top stories HackerNews"""
    top_stories = requests.get('https://hacker-news.firebaseio.com/v0/topstories.json').json()

    articles = []
    for story_id in top_stories[:limit]:
        story = requests.get(f'https://hacker-news.firebaseio.com/v0/item/{story_id}.json').json()
        if story.get('url'):
            articles.append(story)

    return articles
```

**Livrables** :
- [ ] Intégration Reddit avec filtrage par upvotes
- [ ] Intégration HackerNews avec filtrage par score
- [ ] Déduplication des URLs entre sources
- [ ] Crawl automatique quotidien

---

### Phase 3️⃣ : Améliorations UX (Semaine 5-6)

**Objectif** : Interface plus riche et personnalisable

#### 1. Affichage des sources
```typescript
// Améliorer ArticleCard.tsx
<div className="source-info">
  <img src={faviconUrl} alt={source} />
  <span>{source}</span>
  <LevelBadge level={level} />
</div>
```

#### 2. Filtres avancés
```typescript
// Nouveau composant: AdvancedFilters.tsx
const AdvancedFilters = () => {
  return (
    <div className="filters">
      <FilterBySource sources={allSources} />
      <FilterByLevel levels={['beginner', 'intermediate', 'advanced']} />
      <FilterByDate range={['today', 'week', 'month']} />
      <FilterByCategory categories={allCategories} />
    </div>
  );
};
```

#### 3. Bookmarks (localStorage)
```typescript
// Nouveau hook: useBookmarks.ts
export const useBookmarks = () => {
  const [bookmarks, setBookmarks] = useState<string[]>([]);

  useEffect(() => {
    const saved = localStorage.getItem('bookmarks');
    if (saved) setBookmarks(JSON.parse(saved));
  }, []);

  const addBookmark = (articleUrl: string) => {
    const updated = [...bookmarks, articleUrl];
    setBookmarks(updated);
    localStorage.setItem('bookmarks', JSON.stringify(updated));
  };

  return { bookmarks, addBookmark };
};
```

**Livrables** :
- [ ] Sources visibles et cliquables
- [ ] Filtres avancés multi-critères
- [ ] Système de bookmarks
- [ ] Historique de lecture (localStorage)

---

### Phase 4️⃣ : Features avancées (Semaine 7-8)

**Objectif** : Personnalisation et engagement

#### 1. Mode digest personnalisé
```python
# Nouveau fichier: generate_digest.py
def generate_personalized_digest(user_preferences: dict):
    """Génère un digest personnalisé basé sur les préférences"""
    articles = query_articles(
        categories=user_preferences['categories'],
        sources=user_preferences['sources'],
        level=user_preferences['level'],
        exclude_beginner=user_preferences['exclude_beginner']
    )

    return format_digest_email(articles)
```

#### 2. LinkedIn posts scraping
```python
# Scraper LinkedIn (nécessite authentification)
# Option 1: Via API LinkedIn (payant)
# Option 2: Via RSS des profils publics (limité)
# Option 3: Via scraping (risqué, TOS violation)
```

**Livrables** :
- [ ] Digest hebdomadaire personnalisé
- [ ] Système de préférences utilisateur
- [ ] LinkedIn posts (si faisable légalement)
- [ ] Export vers Notion/Obsidian

---

## 🎯 MÉTRIQUES DE SUCCÈS

Pour valider que les améliorations répondent aux attentes :

### Métriques quantitatives
- **Taux de satisfaction** : NPS > 50
- **Articles lus/session** : > 3 articles
- **Taux de retour** : > 40% reviennent chaque semaine
- **Temps moyen** : > 5 min par visite
- **Bookmarks** : > 20% des articles bookmarkés

### Métriques qualitatives
- **Feedback sur filtrage** : "Le contenu est plus pertinent"
- **Réduction du bruit** : "Moins de tutos débutants"
- **Découvrabilité** : "J'ai trouvé des contenus que je n'aurais pas vus ailleurs"

---

## 🚀 COMMENCER PAR OÙ ?

### Quick Wins immédiats (Cette semaine)

1. **Ajouter le filtrage anti-débutant** dans `content_classifier.py`
2. **Détecter le contenu promotionnel** avec un score marketing
3. **Afficher les badges de niveau** dans le frontend
4. **Améliorer l'affichage des sources** dans ArticleCard

### Prochaines itérations

1. **Reddit & HackerNews** : Nouvelles sources très demandées
2. **Filtres avancés** : Permettre personnalisation
3. **Bookmarks** : Feature d'engagement essentielle

---

## 📝 NOTES IMPORTANTES

### Alignement avec les retours utilisateurs

✅ **64% rejettent les tutos débutants** → Priorité 1 : filtrage anti-bruit
✅ **50% utilisent Reddit/HackerNews** → Priorité 2 : nouvelles sources
✅ **57% intéressés Modern Data Stack** → Déjà couvert par catégories existantes
✅ **50% rejettent les pubs** → Priorité 1 : détection promotionnelle

### Contraintes techniques

⚠️ **LinkedIn scraping** : Risque de violation TOS, nécessite API officielle
⚠️ **YouTube** : Complexe (transcription, qualité variable), à prioriser plus tard
⚠️ **Reddit API** : Rate limits (60 req/min), nécessite authentification OAuth
⚠️ **HackerNews API** : Pas de rate limit mais 1 req par item (lent)

---

## 🎉 OBJECTIF FINAL

Devenir **LA référence en veille Data Engineering** avec :

- ✅ Contenu 100% pertinent (pas de bruit)
- ✅ Sources fiables et reconnues
- ✅ Filtrage intelligent et personnalisable
- ✅ Interface riche et agréable
- ✅ Communauté engagée et satisfaite

**Prochaine étape** : Implémenter la Phase 1 (Quick Wins) cette semaine.
