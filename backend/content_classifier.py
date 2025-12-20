# content_classifier.py
"""
Classification des articles en deux types :
- "technical" : Articles techniques, tutoriels, documentation
- "rex" : Retours d'expérience (REX), All Hands, Post-mortems
"""

from typing import Dict, Any, List


def detect_content_type(title: str, summary: str, content: str, config: Dict[str, Any], source_name: str = "") -> str:
    """
    Détermine si un article est un REX/All Hands ou un article technique standard.

    Args:
        title: Titre de l'article
        summary: Résumé de l'article
        content: Contenu complet (premiers caractères)
        config: Configuration avec les mots-clés REX
        source_name: Nom de la source (pour filtrer les sources communautaires)

    Returns:
        "rex" ou "technical"
    """
    content_config = config.get("content_types", {})

    # Vérifier que la source est communautaire
    community_sources = content_config.get("community_sources", [])
    if source_name and community_sources:
        if source_name in community_sources:
            # Source communautaire = toujours "rex" (inclut newsletters, tutoriels, REX)
            return "rex"
        else:
            # Source corporate = toujours "technical"
            return "technical"

    # Si pas de liste de sources communautaires définie, fallback sur les patterns
    rex_keywords = content_config.get("rex_keywords", [])
    rex_title_bonus = content_config.get("rex_title_bonus", 30)
    rex_min_score = content_config.get("rex_min_score", 40)

    # Texte à analyser (titre + résumé + début du contenu)
    full_text = f"{title} {summary} {content[:500]}".lower()
    title_lower = title.lower()

    rex_score = 0

    # Compter les occurrences de mots-clés REX
    for keyword in rex_keywords:
        keyword_lower = keyword.lower()

        # Si dans le titre, bonus important
        if keyword_lower in title_lower:
            rex_score += rex_title_bonus

        # Si dans le texte complet
        count = full_text.count(keyword_lower)
        if count > 0:
            rex_score += count * 10  # 10 points par occurrence

    # Patterns supplémentaires pour REX (avec scoring différencié)
    # Patterns forts = mots-clés qui indiquent presque certainement un REX
    strong_rex_patterns = [
        "how we",
        "why we",
        "we migrated",
        "we scaled",
        "we built",
        "we learned",
        "our experience",
        "our approach",
        "our journey",
        "our story",
        "retour d'expérience",
        "all hands",
        "postmortem",
        "post-mortem",
        "incident report",
        "lessons learned",
        "what we learned",
        "year in review",
        "retrospective",
    ]

    # Patterns moyens = indicateurs possibles de REX
    medium_rex_patterns = [
        "building",
        "scaling",
        "migrating",
        "moving to",
        "switching to",
        "adopting",
        "implementing at",
        "journey to",
        "at scale",
        "in production",
        "real-world",
        "from the trenches",
        "in the wild",
        "battle-tested",
        "looking back",
        "deep dive into our",
        "inside",
        "behind the scenes",
    ]

    # Score pour patterns forts
    for pattern in strong_rex_patterns:
        if pattern in full_text:
            # Bonus titre important si dans le titre
            if pattern in title_lower:
                rex_score += 35  # Fort bonus titre
            else:
                rex_score += 20  # Fort bonus texte

    # Score pour patterns moyens
    for pattern in medium_rex_patterns:
        if pattern in full_text:
            # Bonus titre modéré si dans le titre
            if pattern in title_lower:
                rex_score += 20  # Moyen bonus titre
            else:
                rex_score += 8   # Moyen bonus texte

    # Décision finale
    if rex_score >= rex_min_score:
        return "rex"
    else:
        return "technical"


def get_content_type_emoji(content_type: str) -> str:
    """Retourne un emoji pour le type de contenu."""
    return "📖" if content_type == "rex" else "🔧"


def get_content_type_label(content_type: str) -> str:
    """Retourne un label lisible pour le type de contenu."""
    labels = {
        "rex": "REX / All Hands",
        "technical": "Article technique"
    }
    return labels.get(content_type, "Inconnu")


def split_by_content_type(items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Sépare une liste d'articles par type de contenu.

    Args:
        items: Liste d'articles avec un champ "content_type"

    Returns:
        {"technical": [...], "rex": [...]}
    """
    result = {
        "technical": [],
        "rex": []
    }

    for item in items:
        content_type = item.get("content_type", "technical")
        if content_type in result:
            result[content_type].append(item)

    return result


# ===========================================================================
# NOUVEAUTÉS : Filtrage anti-bruit et niveau technique (Phase 1 - Quick Wins)
# ===========================================================================

# Mots-clés indiquant du contenu débutant (à exclure selon retours utilisateurs)
BEGINNER_KEYWORDS = [
    # Anglais
    "introduction to", "getting started", "tutorial for beginners",
    "hello world", "step-by-step guide", "from scratch",
    "for dummies", "basics of", "fundamentals of",
    "beginner's guide", "crash course", "101",
    "easy tutorial", "simple guide", "quick start",
    # Français
    "introduction à", "débuter avec", "pour débutants",
    "premier pas", "guide simple", "les bases de",
    "initiation à", "découvrir", "comprendre en 5 minutes"
]

# Mots-clés indiquant du contenu promotionnel/marketing (à pénaliser)
MARKETING_KEYWORDS = [
    # Superlatifs exagérés
    "game-changer", "revolutionary", "disruptive",
    "transform", "revolutionize", "unlock the power",
    "next generation", "cutting-edge", "groundbreaking",
    "industry-leading", "world-class", "best-in-class",
    # Contenu sponsorisé
    "sponsored", "partner content", "in partnership with",
    "affiliate", "powered by", "brought to you by",
    # Call-to-action commercial
    "sign up now", "get started today", "free trial",
    "limited offer", "exclusive access", "special discount"
]

# Mots-clés indiquant du contenu avancé/expert
ADVANCED_KEYWORDS = [
    # Architecture & Performance
    "optimization", "performance tuning", "scaling",
    "distributed systems", "fault tolerance", "high availability",
    "load balancing", "sharding", "partitioning",
    "consensus algorithms", "raft", "paxos",
    # Bas niveau
    "internals", "under the hood", "deep dive",
    "implementation details", "source code analysis",
    "memory layout", "garbage collection", "jit compilation",
    # Production & SRE
    "production-grade", "production-ready", "battle-tested",
    "incident response", "postmortem", "runbook",
    "monitoring at scale", "observability patterns",
    # Concepts avancés
    "distributed tracing", "service mesh", "zero-downtime",
    "blue-green deployment", "canary release"
]


def detect_beginner_content(title: str, summary: str, content: str) -> bool:
    """
    Détecte si l'article est de niveau débutant.

    Retourne True si l'article contient des patterns "débutant" dans le titre
    ou de manière répétée dans le contenu.

    Args:
        title: Titre de l'article
        summary: Résumé
        content: Contenu (premiers caractères)

    Returns:
        True si contenu débutant, False sinon
    """
    title_lower = title.lower()
    full_text = f"{title} {summary} {content[:1000]}".lower()

    # Si un mot-clé débutant est dans le titre, c'est très probablement du contenu débutant
    for keyword in BEGINNER_KEYWORDS:
        if keyword in title_lower:
            return True

    # Compter les occurrences dans le texte complet
    beginner_count = sum(1 for keyword in BEGINNER_KEYWORDS if keyword in full_text)

    # Si 2+ mots-clés débutants dans le texte, c'est probablement du contenu débutant
    return beginner_count >= 2


def calculate_marketing_score(title: str, summary: str, content: str) -> int:
    """
    Calcule un score de marketing/promotion (0-100).

    Plus le score est élevé, plus le contenu est promotionnel.

    Args:
        title: Titre de l'article
        summary: Résumé
        content: Contenu (premiers caractères)

    Returns:
        Score de 0 à 100 (0 = pas marketing, 100 = très marketing)
    """
    full_text = f"{title} {summary} {content[:1000]}".lower()
    title_lower = title.lower()

    score = 0

    # Mots-clés marketing dans le titre : +15 points chacun
    for keyword in MARKETING_KEYWORDS:
        if keyword in title_lower:
            score += 15

    # Mots-clés marketing dans le contenu : +5 points chacun
    for keyword in MARKETING_KEYWORDS:
        if keyword in full_text and keyword not in title_lower:
            score += 5

    # Détecter les patterns de lien affilié
    if "affiliate" in full_text or "sponsored" in full_text:
        score += 30

    # Détecter les call-to-action répétés
    cta_patterns = ["sign up", "get started", "free trial", "click here"]
    cta_count = sum(full_text.count(pattern) for pattern in cta_patterns)
    score += min(cta_count * 10, 30)  # Max 30 points pour CTA

    return min(score, 100)


def calculate_technical_level(title: str, summary: str, content: str) -> str:
    """
    Détermine le niveau technique de l'article.

    Returns:
        "beginner", "intermediate", ou "advanced"
    """
    # Si c'est du contenu débutant, arrêt immédiat
    if detect_beginner_content(title, summary, content):
        return "beginner"

    full_text = f"{title} {summary} {content[:1000]}".lower()

    # Compter les indicateurs de contenu avancé
    advanced_count = sum(1 for keyword in ADVANCED_KEYWORDS if keyword in full_text)

    # Si 3+ indicateurs avancés, c'est du contenu expert
    if advanced_count >= 3:
        return "advanced"

    # Si 1-2 indicateurs avancés, c'est du contenu intermédiaire
    if advanced_count >= 1:
        return "intermediate"

    # Par défaut, contenu intermédiaire (sauf si déjà classé débutant)
    return "intermediate"


def should_exclude_article(title: str, summary: str, content: str, min_quality_score: int = 50) -> tuple[bool, str]:
    """
    Détermine si un article doit être exclu du feed (filtrage anti-bruit).

    Args:
        title: Titre de l'article
        summary: Résumé
        content: Contenu
        min_quality_score: Score minimum pour accepter l'article (0-100)

    Returns:
        (should_exclude: bool, reason: str)
    """
    # 1. Exclure le contenu débutant (demande utilisateur #1)
    if detect_beginner_content(title, summary, content):
        return (True, "beginner_content")

    # 2. Exclure le contenu trop promotionnel
    marketing_score = calculate_marketing_score(title, summary, content)
    if marketing_score >= 50:  # Threshold configurable
        return (True, "promotional_content")

    # 3. Pénaliser légèrement le contenu avec un peu de marketing
    quality_penalty = marketing_score // 10  # -1 point par tranche de 10 points de marketing
    effective_quality = min_quality_score - quality_penalty

    if effective_quality < 40:  # En-dessous de 40, on exclut
        return (True, "low_quality_with_marketing")

    return (False, "")


def get_level_badge_info(level: str) -> Dict[str, str]:
    """
    Retourne les informations de style pour le badge de niveau.

    Returns:
        {"color": "...", "label": "...", "emoji": "..."}
    """
    badges = {
        "beginner": {
            "color": "green",
            "label": "Débutant",
            "emoji": "🟢"
        },
        "intermediate": {
            "color": "yellow",
            "label": "Intermédiaire",
            "emoji": "🟡"
        },
        "advanced": {
            "color": "red",
            "label": "Avancé",
            "emoji": "🔴"
        }
    }
    return badges.get(level, badges["intermediate"])
