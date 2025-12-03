# test_veille_tech.py
"""
Tests unitaires pour les fonctions critiques de veille_tech.py
Utilise pytest pour les tests.

Usage: pytest test_veille_tech.py -v
"""

import pytest
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from veille_tech import (
    classify,
    normalize_ts,
    week_bounds,
    hash_id,
    is_editorial_article,
    Category,
)


# -----------------------
# Tests pour classify()
# -----------------------

def test_classify_with_matching_keywords():
    """Test classification avec des mots-clés correspondants."""
    categories = [
        Category(key="python", title="Python", keywords=["python", "pandas", "numpy"]),
        Category(key="data", title="Data", keywords=["data", "analytics", "etl"]),
    ]

    title = "Building ETL pipelines with Python and Pandas"
    summary = "A comprehensive guide to data engineering"

    result = classify(title, summary, categories)

    # Devrait matcher "python" car plus de hits (python + pandas vs data + etl)
    assert result == "python"


def test_classify_no_match():
    """Test classification sans correspondance."""
    categories = [
        Category(key="python", title="Python", keywords=["python", "pandas"]),
    ]

    title = "Learning JavaScript basics"
    summary = "Introduction to web development"

    result = classify(title, summary, categories)
    assert result is None


def test_classify_case_insensitive():
    """Test que la classification est insensible à la casse."""
    categories = [
        Category(key="ml", title="Machine Learning", keywords=["machine learning", "ML"]),
    ]

    title = "MACHINE LEARNING Tutorial"
    summary = "Learn ML basics"

    result = classify(title, summary, categories)
    assert result == "ml"


# -----------------------
# Tests pour normalize_ts()
# -----------------------

def test_normalize_ts_with_published_parsed():
    """Test normalisation avec published_parsed."""
    entry = {
        "published_parsed": (2024, 11, 15, 10, 30, 0, 0, 0, 0)
    }

    result = normalize_ts(entry)

    expected = datetime(2024, 11, 15, 10, 30, 0, tzinfo=timezone.utc)
    assert result == int(expected.timestamp())


def test_normalize_ts_with_published_string():
    """Test normalisation avec published en string RFC 2822."""
    entry = {
        "published": "Fri, 15 Nov 2024 10:30:00 +0000"
    }

    result = normalize_ts(entry)
    assert result is not None
    assert isinstance(result, int)


def test_normalize_ts_no_date():
    """Test normalisation sans date disponible."""
    entry = {
        "title": "Some article",
        "summary": "Some content"
    }

    result = normalize_ts(entry)
    assert result is None


# -----------------------
# Tests pour week_bounds()
# -----------------------

def test_week_bounds_current_week():
    """Test calcul des bornes de la semaine courante."""
    start_ts, end_ts, label, start_str, end_str = week_bounds("Europe/Paris", week_offset=0)

    # Vérifications de base
    assert start_ts < end_ts
    assert end_ts - start_ts == 7 * 24 * 3600  # 7 jours
    assert label.startswith("2024w") or label.startswith("2025w")
    assert len(label) == 7  # Format: YYYYwWW


def test_week_bounds_previous_week():
    """Test calcul de la semaine précédente."""
    current_start, _, _, _, _ = week_bounds("Europe/Paris", week_offset=0)
    prev_start, _, _, _, _ = week_bounds("Europe/Paris", week_offset=-1)

    # La semaine précédente doit être 7 jours avant
    assert current_start - prev_start == 7 * 24 * 3600


def test_week_bounds_label_format():
    """Test le format du label de semaine."""
    _, _, label, _, _ = week_bounds("Europe/Paris", week_offset=0)

    # Format YYYYwWW
    year_part = label[:4]
    week_part = label[5:7]

    assert label[4] == "w"
    assert year_part.isdigit()
    assert week_part.isdigit()
    assert 1 <= int(week_part) <= 53


# -----------------------
# Tests pour hash_id()
# -----------------------

def test_hash_id_consistency():
    """Test que hash_id est déterministe."""
    url = "https://example.com/article"
    title = "Test Article"

    hash1 = hash_id(url, title)
    hash2 = hash_id(url, title)

    assert hash1 == hash2
    assert len(hash1) == 64  # SHA256 = 64 caractères hex


def test_hash_id_different_inputs():
    """Test que des inputs différents produisent des hashes différents."""
    hash1 = hash_id("https://example.com/article1", "Title 1")
    hash2 = hash_id("https://example.com/article2", "Title 2")

    assert hash1 != hash2


def test_hash_id_unicode():
    """Test hash_id avec des caractères Unicode."""
    url = "https://example.com/article"
    title = "Titre avec émojis 🚀 et accents éàù"

    result = hash_id(url, title)
    assert len(result) == 64


# -----------------------
# Tests pour is_editorial_article()
# -----------------------

def test_is_editorial_article_allowed_path():
    """Test qu'un article avec un chemin valide est accepté."""
    cfg = {
        "crawl": {
            "path_allow_regex": r"(?i)(/blog|/posts?|/articles?)",
            "min_text_length": 100
        }
    }

    url = "https://example.com/blog/my-article"
    text = "A" * 150  # Texte de 150 caractères

    result = is_editorial_article(url, cfg, text)
    assert result is True


def test_is_editorial_article_denied_path():
    """Test qu'un article avec un chemin interdit est rejeté."""
    cfg = {
        "crawl": {
            "path_deny_regex": r"(?i)(forum|jobs|careers)",
        }
    }

    url = "https://example.com/forum/topic-123"

    result = is_editorial_article(url, cfg, "")
    assert result is False


def test_is_editorial_article_too_short():
    """Test qu'un article trop court est rejeté."""
    cfg = {
        "crawl": {
            "min_text_length": 500
        }
    }

    url = "https://example.com/blog/article"
    text = "A" * 100  # Trop court

    result = is_editorial_article(url, cfg, text)
    assert result is False


def test_is_editorial_article_blacklist():
    """Test que les domaines blacklistés sont rejetés."""
    cfg = {
        "crawl": {
            "blacklist_domains": ["spam.com", "ads.example.com"]
        }
    }

    url = "https://spam.com/article"

    result = is_editorial_article(url, cfg, "")
    assert result is False


# -----------------------
# Tests d'intégration
# -----------------------

def test_full_classification_workflow():
    """Test du workflow complet de classification."""
    categories = [
        Category(key="ai", title="AI", keywords=["ai", "machine learning", "llm"]),
        Category(key="cloud", title="Cloud", keywords=["aws", "azure", "cloud"]),
    ]

    # Cas 1: Article AI
    result1 = classify(
        "Building LLM applications with machine learning",
        "Deep dive into AI and ML techniques",
        categories
    )
    assert result1 == "ai"

    # Cas 2: Article Cloud
    result2 = classify(
        "Deploying on AWS",
        "Guide to cloud infrastructure on Azure",
        categories
    )
    assert result2 == "cloud"

    # Cas 3: Article non pertinent
    result3 = classify(
        "Cooking recipes",
        "How to make pasta",
        categories
    )
    assert result3 is None


# -----------------------
# Fixtures pytest
# -----------------------

@pytest.fixture
def sample_categories():
    """Fixture avec des catégories d'exemple."""
    return [
        Category(key="python", title="Python", keywords=["python", "django", "flask"]),
        Category(key="javascript", title="JavaScript", keywords=["javascript", "react", "node"]),
        Category(key="devops", title="DevOps", keywords=["docker", "kubernetes", "ci/cd"]),
    ]


@pytest.fixture
def sample_config():
    """Fixture avec une config d'exemple."""
    return {
        "crawl": {
            "path_allow_regex": r"(?i)(/blog|/posts?|/articles?)",
            "path_deny_regex": r"(?i)(forum|jobs|careers)",
            "min_text_length": 300,
            "blacklist_domains": ["spam.com"],
            "whitelist_domains": [],
        }
    }


def test_with_fixtures(sample_categories, sample_config):
    """Test utilisant les fixtures."""
    # Test classification
    result = classify("Python Django tutorial", "Learn web dev", sample_categories)
    assert result == "python"

    # Test filtrage
    assert is_editorial_article("https://example.com/blog/test", sample_config, "A" * 400)
    assert not is_editorial_article("https://example.com/jobs", sample_config, "A" * 400)
