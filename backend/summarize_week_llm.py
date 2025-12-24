# summarize_week_llm.py
# Lit export/<YYYYwWW>/ai_selection.json et génère un résumé hebdo avec LLM :
# - ai_summary.md (résumé structuré par thèmes)
#
# ⚠️ Ce script ne fait PAS de scoring, il ne fait que résumer les
#     articles déjà sélectionnés par analyze_relevance.py.

import os
import re
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional

import yaml
from dotenv import load_dotenv

from veille_tech import week_bounds  # pour retrouver la semaine courante
from llm_provider import get_provider, LLMProvider

# Charger les variables d'environnement depuis .env
load_dotenv()

# ==========================
#   Helpers pour le résumé
# ==========================

SUMMARY_SYSTEM_PROMPT = """Tu es un assistant de veille techno (data/analytics/BI/ML) en français.
Objectif: produire un résumé hebdomadaire clair, actionnable, concis.

Structure (Markdown):
1) "## Aperçu général de la semaine"
   - EXACTEMENT 2 phrases maximum
   - Résume les ACTUALITÉS principales de la semaine (nouvelles versions, annonces, changements importants)
   - Pas de liste, pas de puces, juste 2 phrases claires sur ce qu'il faut retenir
2) Sections par thèmes (mêmes titres que fournis)
   - Pour chaque section, COPIE EXACTEMENT les liens fournis dans le contexte
   - Format OBLIGATOIRE pour chaque lien : - [Titre](url) — Source · Date
   - Utilise TOUJOURS le tiret "-" (pas "*" ni "•")
   - NE MODIFIE PAS les liens ou dates fournis
   - Tu peux ajouter un court commentaire APRÈS chaque lien si pertinent
   - Termine CHAQUE section par "**À creuser :**" avec quelques liens si disponibles

Règles:
- Français pro, concis. Pas d'invention : s'appuyer sur le contexte donné.
- Ne pas mettre la réponse dans un bloc de code.
- CONSERVE le format EXACT des liens du contexte (ne les réécris pas).
"""


def build_summary_context(
    items: List[Dict[str, Any]],
    links_per_section: int,
) -> str:
    """
    Construit un bloc Markdown de contexte, groupé par titre de catégorie.
    """
    by_cat: Dict[str, List[Dict[str, Any]]] = {}
    for it in items:
        by_cat.setdefault(it["category_title"], []).append(it)

    lines: List[str] = []
    for cat_title, arr in by_cat.items():
        lines.append(f"## {cat_title}")
        # tri par score puis date
        arr_sorted = sorted(
            arr,
            key=lambda x: (x.get("score", 0), x["published_ts"]),
            reverse=True,
        )[:links_per_section]
        for it in arr_sorted:
            dt = datetime.fromtimestamp(it["published_ts"], tz=timezone.utc).strftime("%Y-%m-%d")
            lines.append(
                f"- [{it['title']}]({it['url']}) — {it['source']} · {dt}"
            )
        lines.append("")
    return "\n".join(lines).strip()


def build_highlights(items: List[Dict[str, Any]], max_items: int = 12) -> str:
    """
    Construit un bloc "Highlights" cross-thèmes pour aider le LLM
    à détecter les tendances globales.
    """
    top = sorted(
        items,
        key=lambda x: (int(x.get("score") or 0), int(x["published_ts"])),
        reverse=True,
    )[:max_items]
    lines = ["# Highlights (toutes catégories)"]
    for it in top:
        dt = datetime.fromtimestamp(it["published_ts"], tz=timezone.utc).strftime("%Y-%m-%d")
        lines.append(
            f"- [{it['title']}]({it['url']}) — {it['source']} · {dt}"
        )
    return "\n".join(lines)


def _strip_weird_chars(md: str) -> str:
    md = md.replace("¶", "")
    md = re.sub(r"(?i)à\s*creuser\s*:?$", "**À creuser :**", md, flags=re.MULTILINE)
    md = re.sub(r"(?i)à\s*creuser\s*:\s*", "**À creuser :**\n", md)
    return md.strip()


def _normalize_creuser_lists(block: str) -> str:
    """
    Uniformise le format des listes sous 'À creuser'.
    """
    lines = []
    for raw in block.splitlines():
        if "**À creuser :**" in raw:
            after = raw.split("**À creuser :**", 1)[1].strip()
            links = re.split(r"\s*[\*\u2022]\s*", after) if after else []
            lines.append("**À creuser :**")
            for lk in links:
                lk = lk.strip(" -•*")
                if not lk:
                    continue
                lines.append(f"- {lk}")
        else:
            lines.append(raw)
    return "\n".join(lines)


def ensure_all_sections_ordered(
    md: str,
    expected_titles: List[str],
    placeholder: str,
) -> str:
    """
    Force l'ordre des sections H2 :
    - 1) "Aperçu général de la semaine"
    - 2) chaque titre dans expected_titles (catégories)
    """
    md = _strip_weird_chars(md)
    # Robustesse : si le LLM a mis des H3 (###) au lieu de H2 (##), on corrige
    md = re.sub(r"(?m)^###\s+", "## ", md)
    sections = re.split(r"(?m)^\s*##\s+", md)
    heads = re.findall(r"(?m)^\s*##\s+(.+)$", md)
    content_by_title: Dict[str, str] = {}
    if sections:
        for h, body in zip(heads, sections[1:]):
            body = _normalize_creuser_lists(body.strip())
            # On enlève un éventuel premier titre Hx parasite
            body = re.sub(r"(?m)^\s*#{1,6}\s+.*$", "", body, count=1).strip()
            
            # Supprimer les lignes qui répètent le titre de la section au début du contenu
            # Par exemple, si le titre est "🏛️ Warehouses & Query Engines"
            # et que la première ligne du body est "🏛️ Warehouses & Query Engines", on la supprime
            lines = body.split('\n')
            if lines and lines[0].strip():
                # Nettoyer le titre et la première ligne pour comparaison
                clean_title = re.sub(r'[^\w\s]', '', h.strip().lower())
                clean_first_line = re.sub(r'[^\w\s]', '', lines[0].strip().lower())
                # Si la première ligne est similaire au titre (au moins 70% de correspondance)
                if clean_first_line and clean_title in clean_first_line or clean_first_line in clean_title:
                    lines = lines[1:]  # Supprimer la première ligne
                    body = '\n'.join(lines).strip()
            
            content_by_title[h.strip()] = body

    overview_key = "Aperçu général de la semaine"
    overview_md = content_by_title.get(overview_key, "")
    if not overview_md:
        for k in list(content_by_title.keys()):
            if "aperçu" in k.lower() and "semaine" in k.lower():
                overview_md = content_by_title.pop(k, "")
                break

    final = []
    if overview_md:
        final.append(f"## {overview_key}\n\n{overview_md}")
    else:
        final.append(f"## {overview_key}\n\n_Résumé indisponible cette semaine._")

    def simpl(s: str) -> str:
        return re.sub(r"[\W_]+", " ", s, flags=re.UNICODE).lower().strip()

    # Remet les sections de catégories dans l'ordre voulu
    for title in expected_titles:
        body = None
        if title in content_by_title:
            body = content_by_title[title]
        else:
            stitle = simpl(title)
            for k, v in list(content_by_title.items()):
                if simpl(k) == stitle or stitle in simpl(k):
                    body = v
                    break
        if body and body.strip():
            final.append(f"## {title}\n\n{body.strip()}")
        else:
            final.append(f"## {title}\n\n_{placeholder}_")

    return "\n\n".join(final).strip() + "\n"

# ==========================
#   LLM call
# ==========================

def generate_weekly_summary_openai(
    provider: LLMProvider,
    context_md: str,
    max_sections: int,
    expected_titles: List[str],
    highlights_md: Optional[str] = None,
    temperature: float = 0.2,
    max_tokens: int = 1200,
) -> str:

    high_block = f"[HIGHLIGHTS]\n{highlights_md}\n\n" if highlights_md else ""
    section_list = "\n".join(f"- {t}" for t in expected_titles)

    user_prompt = f"""Voici une sélection d'articles de la semaine.

IMPORTANT pour l'**Aperçu général de la semaine** :
- EXACTEMENT 2 phrases maximum
- Résume les ACTUALITÉS principales : nouvelles versions, annonces importantes, changements majeurs
- Pas de liste à puces, juste 2 phrases claires
- Exemple : "Databricks annonce X et Y cette semaine. Uber partage son REX sur la migration Z."

Ensuite, détaille par thèmes avec les titres H2 ci-dessous (dans cet ordre) :
{section_list}

{high_block}[CONTEXTE PAR THÈMES]
{context_md}
"""

    # Utilise le provider abstrait au lieu du client OpenAI direct
    return provider.chat_completion(
        messages=[
            {"role": "system", "content": SUMMARY_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )

# ==========================
#   Lecture ai_selection.json
# ==========================

def load_selection_items(selection_path: Path, cfg: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Lit export/<week>/ai_selection.json et retourne une liste d'items normalisés :
    {title, url, source, category_key, category_title, score, published_ts}
    """
    data = json.loads(selection_path.read_text(encoding="utf-8"))

    # Map key -> title lisible depuis config
    cat_titles_by_key: Dict[str, str] = {}
    for c in cfg.get("categories", []):
        key = c.get("key")
        title = c.get("title", key)
        if key:
            cat_titles_by_key[key] = title

    items: List[Dict[str, Any]] = []
    for cat_key, arr in data.items():
        cat_title = cat_titles_by_key.get(cat_key, cat_key)
        for it in arr:
            items.append(
                {
                    "title": it.get("title") or "",
                    "url": it.get("url") or "",
                    "source": it.get("source_name") or "",
                    "category_key": cat_key,
                    "category_title": cat_title,
                    "score": float(it.get("score") or 0),
                    "published_ts": int(it.get("published_ts") or 0),
                }
            )
    return items

# ==========================
#   MAIN
# ==========================

def main(config_path: str = "config.yaml", week_offset: Optional[int] = None):
    cfg = yaml.safe_load(Path(config_path).read_text(encoding="utf-8"))

    # Titres attendus pour les sections (dans l'ordre)
    expected_titles = [c.get("title", c.get("key")) for c in cfg.get("categories", [])]

    # Créer le provider LLM depuis config
    llm_cfg = cfg.get("llm", {}) or {}
    try:
        provider = get_provider(llm_cfg)
        print(f"[summary] Provider LLM: {llm_cfg.get('provider', 'groq')} / {provider.model}")
    except (ValueError, RuntimeError) as e:
        print(f"[error] Impossible de créer le provider LLM: {e}")
        return

    temperature = float(llm_cfg.get("temperature", 0.2))
    max_tokens = int(llm_cfg.get("max_tokens", 1200))

    # Summary config
    sum_cfg = cfg.get("summary", {}) or {}
    if not sum_cfg.get("enabled", True):
        print("[info] Résumé désactivé (summary.enabled = false)")
        return
    max_sections = int(sum_cfg.get("max_sections", 8))
    links_per = int(sum_cfg.get("links_per_section", 5))
    min_score = float(sum_cfg.get("min_score", 60))

    # Fenêtre semaine (Europe/Paris) pour retrouver le répertoire
    if week_offset is None:
        week_offset = int(os.getenv("WEEK_OFFSET", "0"))
    _, _, week_label, week_start_h, week_end_h = week_bounds(
        "Europe/Paris", week_offset=week_offset
    )

    out_root = Path(cfg.get("export", {}).get("out_dir", "export"))
    week_dir = out_root / week_label
    selection_path = week_dir / "ai_selection.json"

    if not selection_path.exists():
        raise FileNotFoundError(f"Fichier de sélection introuvable : {selection_path}")

    items = load_selection_items(selection_path, cfg)
    print(f"[diag] items dans ai_selection: {len(items)}")

    # On ne garde que les articles au-dessus d'un seuil global pour le résumé
    items_for_sum = [it for it in items if it["score"] >= min_score]
    if not items_for_sum:
        print("[info] Aucun article au-dessus de min_score pour le résumé.")
        return

    # Contexte + highlights
    context_md = build_summary_context(items_for_sum, links_per)
    highlights_md = build_highlights(items_for_sum, max_items=12)

    # Appel LLM
    weekly_md = generate_weekly_summary_openai(
        provider=provider,
        context_md=context_md,
        max_sections=max_sections,
        expected_titles=expected_titles,
        highlights_md=highlights_md,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    weekly_md = ensure_all_sections_ordered(
        weekly_md,
        expected_titles=expected_titles,
        placeholder="Rien d’important cette semaine.",
    )

    summary_path = week_dir / "ai_summary.md"
    summary_path.write_text(weekly_md, encoding="utf-8")
    print(f"[done] Résumé hebdo IA: {summary_path}")

# ==========================
#   CLI
# ==========================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Résumé hebdo via LLM à partir de ai_selection.json")
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--week-offset", type=int, default=None,
                        help="Décalage de semaine: 0=cette semaine, -1=semaine dernière, etc.")
    args = parser.parse_args()
    main(args.config, week_offset=args.week_offset)