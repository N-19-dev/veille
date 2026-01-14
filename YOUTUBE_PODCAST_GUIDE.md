# Guide : Ajouter des Sources YouTube et Podcast

## Vue d'ensemble

Le système de veille tech supporte maintenant les sources **YouTube** et **Podcast** en plus des articles de blog classiques. Ces sources utilisent leurs flux RSS et exploitent les titres et descriptions pour la classification et le scoring, sans avoir besoin de transcription (gratuit).

## Comment ça fonctionne

### Pour les sources classiques (articles)
1. Récupération du flux RSS
2. Extraction du lien de l'article
3. **Fetch du contenu complet** de la page web
4. Extraction avec Readability
5. Classification et scoring

### Pour YouTube et Podcast (nouveau)
1. Récupération du flux RSS
2. **Utilisation directe du titre + description** (pas de fetch supplémentaire)
3. Classification et scoring sur la base du titre + description
4. Pas de filtres éditoriaux de path (désactivés pour ces sources)

**Avantages** :
- ✅ **Gratuit** (pas d'API, pas de transcription)
- ✅ **Rapide** (pas de fetch de page supplémentaire)
- ✅ **Suffisant** pour la veille (les descriptions YouTube/Podcast sont souvent détaillées)

## Ajouter une chaîne YouTube

### 1. Trouver l'ID de la chaîne

**Option A : Via l'URL de la chaîne**
- URL moderne : `youtube.com/@username` → Inspecter la page source et chercher `"channelId"`
- URL legacy : `youtube.com/channel/CHANNEL_ID` → l'ID est directement dans l'URL
- URL custom : `youtube.com/c/customname` → Inspecter la page source

**Option B : Via une vidéo de la chaîne**
1. Ouvrir une vidéo de la chaîne
2. Clic droit sur le nom de la chaîne → "Copier l'adresse du lien"
3. L'ID est dans l'URL : `youtube.com/channel/CHANNEL_ID`

### 2. Construire l'URL du flux RSS

Format :
```
https://www.youtube.com/feeds/videos.xml?channel_id=CHANNEL_ID
```

Exemple :
```
https://www.youtube.com/feeds/videos.xml?channel_id=UCmLGJ3VYBcfRaWbP6JLJcpA
```

### 3. Ajouter dans config.yaml

```yaml
sources:
  - name: Seattle Data Guy (YouTube)
    url: https://www.youtube.com/feeds/videos.xml?channel_id=UCmLGJ3VYBcfRaWbP6JLJcpA
    type: youtube
```

### 4. Ajouter un poids de source (optionnel mais recommandé)

```yaml
relevance:
  source_weights:
    Seattle Data Guy (YouTube): 0.9  # Ajuster entre 0.5 et 1.0
```

## Ajouter un Podcast

### 1. Trouver l'URL du flux RSS

La plupart des podcasts publient leur flux RSS publiquement :
- Site web du podcast (chercher "RSS" ou icône RSS)
- Apple Podcasts : Clic droit sur le podcast → "Copier l'adresse du flux"
- Spotify : Utiliser un service comme `podcast-feed.net` ou chercher le feed sur le site du podcast
- Rechercher `[nom du podcast] rss feed` sur Google

### 2. Tester le flux

```bash
curl -I "https://example.com/podcast/feed"
# Doit retourner Content-Type: application/rss+xml ou application/xml
```

### 3. Ajouter dans config.yaml

```yaml
sources:
  - name: Data Engineering Podcast
    url: https://www.dataengineeringpodcast.com/feed/mp3/
    type: podcast
```

### 4. Ajouter un poids de source

```yaml
relevance:
  source_weights:
    Data Engineering Podcast: 0.95  # Haute autorité pour les podcasts spécialisés
```

## Exemples de sources configurées

### YouTube Data Engineering

```yaml
# Chaînes YouTube Data Engineering populaires
- name: Seattle Data Guy (YouTube)
  url: https://www.youtube.com/feeds/videos.xml?channel_id=UCmLGJ3VYBcfRaWbP6JLJcpA
  type: youtube

- name: Advancing Analytics (YouTube)
  url: https://www.youtube.com/feeds/videos.xml?channel_id=UCQ3xgpVZYYvFKXsVRb7gWLw
  type: youtube

- name: Data with Zach (YouTube)
  url: https://www.youtube.com/feeds/videos.xml?channel_id=UCQ5xYp8_UzYdVXuogsPWyOQ
  type: youtube
```

### Podcasts Data Engineering

```yaml
# Podcasts spécialisés Data Engineering
- name: Data Engineering Podcast
  url: https://www.dataengineeringpodcast.com/feed/mp3/
  type: podcast

- name: Analytics Power Hour
  url: https://analyticshour.io/feed/podcast/
  type: podcast
```

## Limitations et considérations

### Contenu limité
- Les descriptions YouTube/Podcast sont plus courtes que les articles complets
- Le scoring sémantique peut être moins précis
- ➡️ **Solution** : Ajuster les poids de source pour compenser

### Pas de filtres éditoriaux
- Les filtres de path (`path_allow_regex`, `path_deny_regex`) sont **désactivés** pour YouTube/Podcast
- Toutes les vidéos/épisodes dans la fenêtre temporelle seront traitées
- ➡️ **Solution** : Choisir des chaînes/podcasts pertinents dès le départ

### Fenêtre temporelle
- Seules les vidéos/épisodes publiés dans la semaine courante sont traités
- Les flux RSS YouTube contiennent généralement les 15 dernières vidéos
- Les flux podcast contiennent généralement les 10-50 derniers épisodes

## Dépannage

### Le flux RSS ne contient aucune entrée
```bash
# Tester manuellement
python3 << 'EOF'
import feedparser
feed = feedparser.parse("URL_DU_FLUX")
print(f"Entries: {len(feed.entries)}")
if feed.entries:
    print(f"Latest: {feed.entries[0].title}")
EOF
```

### Les vidéos/épisodes ne sont pas récupérés
- Vérifier que la date de publication est dans la fenêtre temporelle (semaine ISO)
- Vérifier que le flux RSS retourne bien des timestamps valides
- Vérifier les logs : `logs/veille_tech.log`

### Description trop courte
- Certaines chaînes YouTube ont des descriptions très courtes
- ➡️ **Solution future** : Ajouter une option de transcription sélective pour les sources à description courte

## Évolutions futures possibles

1. **Transcription sélective** : Si `description_length < 200`, déclencher une transcription (Whisper API)
2. **Métadonnées enrichies** : Extraire la durée, les vues, les likes depuis le feed RSS
3. **Filtrage par durée** : Exclure les shorts (<1min) ou les très longues vidéos (>2h)
4. **Support de playlists YouTube** : Monitorer une playlist spécifique plutôt qu'une chaîne entière

## Coût

- **YouTube RSS** : Gratuit, pas de quota
- **Podcast RSS** : Gratuit, pas de quota
- **Transcription (si ajoutée)** : ~$0.006/min (Whisper API)

Pour 20 vidéos/podcasts par semaine (30 min moyenne) avec transcription optionnelle :
- **Sans transcription** : **$0/mois** ✅
- **Avec transcription** : ~$15/mois

## Support

Pour toute question ou problème, consulter :
- [CLAUDE.md](./CLAUDE.md) - Documentation principale du projet
- [GitHub Issues](https://github.com/nathansornet/veille_tech_crawling/issues)
