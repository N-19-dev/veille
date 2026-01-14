# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an automated tech watch system that crawls RSS feeds, classifies articles using LLM, scores relevance via embeddings, and generates weekly summaries. The backend runs as a GitHub Action every Monday at 06:00 UTC, and results are displayed on a React frontend hosted on GitHub Pages.

## Development Commands

### Backend (Python)

```bash
cd backend
source .venv/bin/activate  # Activate virtual environment

# Run full pipeline for current week
python main.py

# Run for previous week
WEEK_OFFSET=-1 python main.py

# Run individual steps
python veille_tech.py --config config.yaml --week-offset 0
python classify_llm.py --config config.yaml --week-offset 0
python analyze_relevance.py --config config.yaml --week-offset 0
python summarize_week_llm.py --config config.yaml --week-offset 0

# Run tests
pytest                              # All tests
pytest test_veille_tech.py         # Specific test file
pytest -m unit                      # Only unit tests
pytest -m integration              # Only integration tests
pytest --cov=. --cov-report=html   # With coverage

# Utility scripts
python regenerate_weeks.py         # Regenerate last 3 weeks
python regenerate_weeks.py --skip-llm  # Skip LLM steps (faster)
python api_server.py               # Start FastAPI server (optional, for dev)
uvicorn api_server:app --reload    # Alternative way to run API

# Daily Email Digest (Phase 2)
python migrate_add_sent_articles.py  # Create sent_articles table (one-time)
python daily_digest.py               # Send daily digest emails (manual trigger)
```

### Frontend (React + Vite)

```bash
cd frontend

# Development
npm run prepare:export  # Copy export data to public/export
npm run dev            # Start dev server (http://localhost:5173)

# Build
npm run build          # Production build (CI skips prepare:export)
npm run preview        # Preview production build
npm run lint           # ESLint check
```

## Architecture

### Backend Pipeline (main.py)

The backend runs 4 sequential steps:

1. **veille_tech.py** - Crawling
   - Fetches RSS/Atom feeds (70+ sources including YouTube & Podcasts)
   - Auto-discovers feeds from website URLs
   - Extracts full content using readability (for regular articles)
   - **YouTube/Podcast support**: Uses title + description directly (no page fetch)
   - Filters by editorial path patterns (blogs/posts/articles) - disabled for YouTube/Podcast
   - Deduplicates by hash (URL + title)
   - Stores in SQLite with initial category classification by keywords

2. **classify_llm.py** - LLM Classification
   - Corrects/improves category classification using Groq LLM
   - Uses llama-3.1-8b-instant model
   - Multi-category support (8 categories: warehouses, orchestration, ML, etc.)

3. **analyze_relevance.py** - Relevance Scoring
   - Calculates `final_score` (0-100) combining:
     - **semantic** (55%): sentence-transformers embeddings vs profile
     - **source** (20%): source reputation weights
     - **quality** (15%): article length, code blocks
     - **tech** (10%): keyword matches
   - Applies per-category thresholds (config: `category_thresholds`)
   - **Diversity filter**: max 2 articles per source per category
   - Exports: `ai_selection.json`, `ai_selection.md`, `top3.md`, `range.txt`

4. **summarize_week_llm.py** - Weekly Summary
   - Generates overview and category summaries using LLM
   - Exports: `digest.json`, `digest.md`, `summary.json`

5. **daily_digest.py** - Daily Email Notifications (Phase 2)
   - Runs Mon-Fri at 08:00 (via GitHub Actions)
   - Selects best article (highest score, not recently sent)
   - Round-robin categories for diversity
   - Sends via SendGrid API (HTML + text templates)
   - Tracks sent articles in `sent_articles` table to avoid duplicates
   - Config: `config.yaml` → `email_digest`
   - Setup: See `DAILY_DIGEST_SETUP.md`

### Content Type Classification

Articles are classified into two types (content_classifier.py):

- **Technical**: Tutorials, guides, documentation
- **REX & All Hands**: Experience reports, post-mortems, case studies

Classification uses keyword matching from `config.yaml` → `content_types.rex_keywords`. The frontend (ContentTypeTabs.tsx) provides tabs to filter by type.

### YouTube & Podcast Support (Phase 2.5)

The system now supports **YouTube channels** and **Podcasts** as sources, using their RSS feeds:

**How it works:**
- YouTube/Podcast feeds are parsed using `feedparser` (same as regular RSS)
- **Title + Description** are used as content (no page fetch, no transcription)
- Editorial path filters are **disabled** for these source types
- Classification and scoring work the same way as regular articles

**Benefits:**
- ✅ **Free** (no API keys, no transcription costs)
- ✅ **Fast** (no additional HTTP requests per item)
- ✅ **Sufficient** (YouTube descriptions are typically 700+ chars, podcast descriptions 50k+ chars)

**Configuration:**
```yaml
sources:
  - name: Seattle Data Guy (YouTube)
    url: https://www.youtube.com/feeds/videos.xml?channel_id=CHANNEL_ID
    type: youtube  # Optional type field

  - name: Data Engineering Podcast
    url: https://example.com/feed/mp3/
    type: podcast
```

**Adding sources:** See [YOUTUBE_PODCAST_GUIDE.md](./YOUTUBE_PODCAST_GUIDE.md) for detailed instructions on:
- Finding YouTube channel IDs and constructing RSS URLs
- Finding podcast RSS feeds
- Recommended source weights
- Troubleshooting

**Future enhancements:**
- Optional transcription for short descriptions (<200 chars) using Whisper API ($0.006/min)
- Extracting metadata (duration, views, likes) from feed
- Playlist support for YouTube

### Data Flow

```
GitHub Actions (Monday 06:00 UTC)
  ↓
Backend Pipeline (Python)
  ↓
export/<YYYYwWW>/  ← JSON/MD files
  ↓
Git commit + push
  ↓
Frontend Build (Vite)
  ↓
GitHub Pages Deploy
```

### Storage

- **SQLite**: `backend/veille.db` (gitignored)
  - **items** table: Articles with scoring (id, url, title, summary, content, published_ts, source_name, category_key, final_score, semantic_score, source_weight, quality_score, tech_score, content_type, tech_level, marketing_score)
    - Index: `idx_items_cat_pub` on (category_key, published_ts DESC)
  - **sent_articles** table: Email digest tracking (article_id, email_recipient, sent_at, digest_type)
    - Prevents sending duplicate articles to users
    - Indexes: `idx_sent_articles_email`, `idx_sent_articles_article`

- **Exports**: `export/<YYYYwWW>/`
  - `digest.json` - Weekly digest with overview + sections (used by frontend)
  - `selection.json` - Filtered articles by category (legacy)
  - `summary.json` - LLM-generated summaries (intermediate file)
  - `digest.md` / `ai_selection.md` - Markdown versions (human-readable)
  - `top3.md` - Top 3 articles of the week
  - `range.txt` - Week date range (e.g., "2025-01-06 → 2025-01-12")

  **digest.json structure:**
  ```json
  {
    "overview": "LLM-generated weekly summary",
    "top3": [{"title": "...", "url": "...", "source": "...", "score": 95}],
    "sections": [
      {
        "title": "🏛️ Warehouses & Query Engines",
        "category_key": "warehouses_engines",
        "items": [{"title": "...", "url": "...", "source": "...", "score": 87, "content_type": "technical"}]
      }
    ]
  }
  ```

- **Symlink**: `export/latest` → current week (for backward compat)

- **Index**: `export/weeks.json` - List of all weeks with metadata

### Frontend Components

- **App.tsx** - Main component with search, filtering, and content type tabs
- **Hero.tsx** - Header with title and description
- **WeekPicker.tsx** - Dropdown to select week
- **SearchBar.tsx** - Fuzzy search using Fuse.js
- **CategoryFilter.tsx** - Filter by category chips
- **ContentTypeTabs.tsx** - Toggle between Technical / REX & All Hands / All
- **Top3.tsx** - Top 3 articles of the week
- **Overview.tsx** - LLM-generated weekly summary
- **SectionCard.tsx** - Category section with articles
- **ArticleCard.tsx** - Individual article card with score badge

### Configuration (config.yaml)

Key sections:
- `categories`: 8 categories with keywords (warehouses, orchestration, governance, lakes, cloud, python, ai, news)
- `sources`: 60+ RSS/Atom feeds
- `category_thresholds`: Per-category final_score thresholds (default 45, news 60)
- `relevance`: Scoring weights, profile text, source weights
- `content_types`: REX keywords and scoring (rex_title_bonus: 30, rex_min_score: 40)
- `crawl`: Rate limiting, user agent, path filters
- `llm`: Groq API config (llama-3.1-8b-instant, temp 0.2)

## Environment Variables

Required in `backend/.env`:
- `GROQ_API_KEY` - Groq API key (free at https://console.groq.com)

Optional:
- `SENDGRID_API_KEY` - SendGrid API key for daily digest emails (Phase 2, see DAILY_DIGEST_SETUP.md)
- `SLACK_WEBHOOK_URL` - Slack notifications
- `WEEK_OFFSET` - Run for N weeks ago (default 0)

## Key Patterns

### Week Calculation
Uses ISO week format (Europe/Paris timezone). Week runs Monday-Sunday. Helper function: `week_bounds(week_offset: int)` in veille_tech.py returns (start_ts, end_ts, week_id).

### Async Crawling
Uses aiohttp + AsyncLimiter for per-host rate limiting. Default: 12 concurrent requests, 1.5 RPS per host.

### Robots.txt Respect
Implements robotparser to respect robots.txt before crawling.

### URL Path Filtering
Articles are filtered by URL patterns (config.yaml):
- **path_allow_regex**: Include URLs matching blog/posts/articles patterns
  - Example: `(?i)(/blog|/posts?|/articles?|/p/|^/@|/tag/|/stories?)`
- **path_deny_regex**: Exclude forums, docs, jobs, changelogs
  - Example: `(?i)(forum|docs?|jobs|careers|events|release[-_ ]?notes|changelog)`
- **min_text_length**: Minimum article length (default 300 chars)

### Feed Auto-discovery
If a source URL is not a feed, attempts to discover RSS/Atom feed from HTML `<link>` tags.

### LLM Integration
Uses OpenAI-compatible API (Groq) via `openai` Python package. Endpoint: `https://api.groq.com/openai/v1`.

### Logging
Structured logging via custom logger.py (wraps Python logging). Logs to `logs/veille_tech.log`. MetricsCollector tracks feeds processed, failed, errors.

### Testing
Uses pytest with markers: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.slow`. Asyncio mode: auto.

## Optional REST API

The backend includes an optional FastAPI server (api_server.py) for development:

```bash
cd backend
uvicorn api_server:app --reload  # http://localhost:8000
```

**Endpoints:**
- `GET /weeks` - List all available weeks
- `GET /week/{week_id}` - Get data for a specific week
- `GET /categories` - List all categories
- `GET /search?q=term` - Search articles

**CORS:** Configured to allow frontend (localhost:5173 + GitHub Pages)

**Note:** The production frontend uses static JSON files from export/, not the API.

## Utility Scripts

Beyond the main pipeline, several utility scripts are available:

- **regenerate_weeks.py** - Regenerates last 3 weeks (useful after config changes)
  - Use `--skip-llm` flag to skip expensive LLM calls
- **write_week_selection.py** - Manually write week selection data
- **generate_summary_from_selection.py** - Generate summary from existing selection
- **convert_to_summary_json.py** - Convert old formats to summary.json

## Deployment Notes

GitHub Actions workflows (not currently present in .github/workflows):
- **backend-weekly.yml**: Runs Monday 06:00 UTC, executes main.py, commits to export/
- **deploy-frontend.yml**: Builds frontend on push to main, deploys to GitHub Pages

Required GitHub secrets:
- `GROQ_API_KEY`
- `PAT_TOKEN` (repo + workflow scope)

GitHub Pages must be enabled with source: GitHub Actions.

## Important URLs

User-Agent in config.yaml references: `https://github.com/nathansornet/veille_tech_crawling`
