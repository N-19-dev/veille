# analyze_relevance.py
# Scoring de pertinence (embeddings + règles) + sélection hebdo
#
# Exporte dans export/<YYYYwWW>/ :
#  - ai_selection.json / ai_selection.md  (articles filtrés par score/thresholds)
#  - top3.md (Top 3 de la semaine, toutes catégories confondues)
#  - range.txt (dates de la semaine)
#  - met à jour export/weeks.json
#  - met à jour le lien export/latest → export/<YYYYwWW>
#
# Aucune dépendance à un LLM ici.
# Un autre script pourra ensuite consommer ai_selection.json ou top3.md
# pour générer un résumé avec un LLM.

import os
import re
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict, Any

import yaml
from sentence_transformers import SentenceTransformer, util

from veille_tech import db_conn, week_bounds  # mêmes bornes de semaine que le crawler

# ==========================
#   DB helpers
# ==========================

def ensure_relevance_columns(db_path: str):
    """
    S'assure que les colonnes nécessaires au scoring de pertinence existent.
    final_score = score combiné (0–100)
    Les autres colonnes servent au debug/analyses ultérieures.
    """
    with db_conn(db_path) as conn:
        cols = [r[1] for r in conn.execute("PRAGMA table_info(items)").fetchall()]
        needed = ["semantic_score", "source_weight", "quality_score", "tech_score", "final_score"]
        for col in needed:
            if col not in cols:
                conn.execute(f"ALTER TABLE items ADD COLUMN {col} REAL")


def group_filtered_with_thresholds(
    db_path: str,
    min_ts: int,
    max_ts: int,
    thresholds: Dict[str, int],
    default_threshold: int,
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Regroupe par catégorie en appliquant un seuil par catégorie sur final_score.
    Trie par score puis date.
    """
    out: Dict[str, List[Dict[str, Any]]] = {}
    with db_conn(db_path) as conn:
        cats = [r[0] for r in conn.execute("SELECT DISTINCT category_key FROM items")]
        for c in cats:
            thr = int(thresholds.get(c, default_threshold))
            rows = conn.execute(
                """
                SELECT url, title, summary, published_ts, source_name, final_score
                FROM items
                WHERE category_key=? AND published_ts>=? AND published_ts<?
                      AND final_score IS NOT NULL AND final_score >= ?
                ORDER BY final_score DESC, published_ts DESC
                """,
                (c, min_ts, max_ts, thr),
            ).fetchall()
            
            # Diversity filter: max 2 items per source
            source_counts = {}
            selected_rows = []
            for row in rows:
                src = row[4]
                if source_counts.get(src, 0) >= 2:
                    continue
                source_counts[src] = source_counts.get(src, 0) + 1
                selected_rows.append(row)
            
            out[c] = [
                dict(
                    url=row[0],
                    title=row[1],
                    summary=row[2],
                    published_ts=row[3],
                    source_name=row[4],
                    score=row[5],
                )
                for row in selected_rows
            ]
    return out


def fetch_items_for_top(
    db_path: str,
    min_ts: int,
    max_ts: int,
    min_score: int,
) -> List[Dict[str, Any]]:
    """
    Récupère tous les items au-dessus d'un seuil, pour calculer un Top K global.
    """
    with db_conn(db_path) as conn:
        rows = conn.execute(
            """
            SELECT title, url, source_name, category_key, final_score, published_ts
            FROM items
            WHERE published_ts >= ? AND published_ts < ?
              AND final_score IS NOT NULL
              AND final_score >= ?
            ORDER BY final_score DESC, published_ts DESC
            """,
            (min_ts, max_ts, min_score),
        ).fetchall()
    
    # Diversity: max 1 per source for Top 3
    seen_sources = set()
    final_rows = []
    for r in rows:
        src = r[2]
        if src in seen_sources:
            continue
        seen_sources.add(src)
        final_rows.append(r)

    keys = ["title", "url", "source", "category", "score", "published_ts"]
    return [dict(zip(keys, r)) for r in final_rows]


def to_markdown(groups: Dict[str, List[Dict[str, Any]]]) -> str:
    """
    Rend un Markdown simple de la sélection, groupée par catégorie_key.
    (les titres lisibles viendront de la UI ou d'un autre script si besoin)
    """
    lines = ["# Sélection — Semaine\n"]
    for key, items in groups.items():
        if not items:
            continue
        lines.append(f"## {key}\n")
        for it in items:
            dt = datetime.fromtimestamp(it["published_ts"], tz=timezone.utc).strftime("%Y-%m-%d")
            score = it.get("score", 0) or 0
            lines.append(
                f"- [{it['title']}]({it['url']}) — {it['source_name']} · {dt} · **{score:.0f}/100**"
            )
        lines.append("")
    return "\n".join(lines)

# ==========================
#   Relevance config helpers
# ==========================

def get_relevance_cfg(cfg: Dict[str, Any]) -> Dict[str, Any]:
    return cfg.get("relevance", {}) or {}

# ==========================
#   Semantic model (global cache)
# ==========================

_model_semantic: Optional[SentenceTransformer] = None
_profile_embedding = None

def get_semantic_model() -> SentenceTransformer:
    global _model_semantic
    if _model_semantic is None:
        _model_semantic = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return _model_semantic

def get_profile_embedding(profile_text: str):
    global _profile_embedding
    if _profile_embedding is None:
        model = get_semantic_model()
        _profile_embedding = model.encode(profile_text, convert_to_tensor=True)
    return _profile_embedding

# ==========================
#   Scoring components
# ==========================

def compute_semantic_score(row: Dict[str, Any], profile_text: str) -> float:
    """
    Retourne un score 0-100 basé sur la similarité cosine
    entre l'article et un profil de veille.
    """
    text = " ".join(
        [
            row.get("title") or "",
            row.get("summary") or "",
            (row.get("content") or "")[:4000],
        ]
    ).strip()
    if not text:
        return 0.0

    model = get_semantic_model()
    emb_profile = get_profile_embedding(profile_text)
    emb_art = model.encode(text, convert_to_tensor=True)

    sim = float(util.cos_sim(emb_profile, emb_art).item())  # typiquement [0,1]
    sim = max(-1.0, min(1.0, sim))
    return (sim + 1.0) * 50.0  # map [-1,1] -> [0,100]


def compute_source_weight(row: Dict[str, Any], source_weights_cfg: Dict[str, float]) -> float:
    """
    Poids de la source en [0,100].
    """
    src = (row.get("source_name") or row.get("source") or "").strip()
    w = source_weights_cfg.get(src, 0.4)  # défaut : 0.4
    w = max(0.0, min(1.0, w))
    return w * 100.0


def compute_quality_score(row: Dict[str, Any], qcfg: Dict[str, Any]) -> float:
    """
    Score simple de qualité éditoriale (longueur + présence de code).
    """
    content = row.get("content") or ""
    text_len = len(content)
    score = 0.0

    min_len_good = int(qcfg.get("min_len_good", 1500))
    bonus_good_len = float(qcfg.get("bonus_good_len", 20.0))
    bonus_has_code = float(qcfg.get("bonus_has_code", 10.0))

    if text_len > min_len_good:
        score += bonus_good_len

    snippet = content[:4000].lower()
    if "```" in snippet or "<code" in snippet:
        score += bonus_has_code

    return max(0.0, min(100.0, score))


def compute_tech_score(row: Dict[str, Any], tcfg: Dict[str, Any]) -> float:
    """
    Score de technicité basé sur la présence de mots-clés techniques.
    """
    kws = [k.lower() for k in tcfg.get("keywords", [])]
    if not kws:
        return 0.0
    max_points = float(tcfg.get("max_points", 20.0))

    text = " ".join(
        [
            (row.get("title") or "").lower(),
            (row.get("content") or "").lower(),
        ]
    )

    hits = 0
    for k in kws:
        if k in text:
            hits += 1

    hits_eff = min(hits, 10)
    raw = (hits_eff / 10.0) * max_points  # [0,max_points]
    # Normalisation en [0,100]
    if max_points <= 0:
        return 0.0
    return max(0.0, min(100.0, raw * (100.0 / max_points)))


def compute_relevance(row: Dict[str, Any], cfg: Dict[str, Any]) -> Dict[str, float]:
    """
    Calcule tous les composants + le score final 0–100.
    Pas de fraîcheur : la fenêtre temporelle est gérée par les requêtes DB.
    """
    rcfg = get_relevance_cfg(cfg)
    w_cfg = rcfg.get("weights", {}) or {}
    profile_text = rcfg.get("profile_text", "")
    source_weights_cfg = rcfg.get("source_weights", {}) or {}
    qcfg = rcfg.get("quality", {}) or {}
    tcfg = rcfg.get("tech", {}) or {}

    w_sem = float(w_cfg.get("semantic", 0.55))
    w_src = float(w_cfg.get("source", 0.20))
    w_qlt = float(w_cfg.get("quality", 0.15))
    w_tech = float(w_cfg.get("tech", 0.10))

    total_w = max(1e-6, (w_sem + w_src + w_qlt + w_tech))
    w_sem /= total_w
    w_src /= total_w
    w_qlt /= total_w
    w_tech /= total_w

    sem = compute_semantic_score(row, profile_text)            # 0–100
    srcw = compute_source_weight(row, source_weights_cfg)      # 0–100
    qlt = compute_quality_score(row, qcfg)                     # 0–100
    tech = compute_tech_score(row, tcfg)                       # 0–100

    final_score = (
        w_sem * sem +
        w_src * srcw +
        w_qlt * qlt +
        w_tech * tech
    )

    return {
        "semantic_score": sem,
        "source_weight": srcw,
        "quality_score": qlt,
        "tech_score": tech,
        "final_score": max(0.0, min(100.0, final_score)),
    }

# ==========================
#   Top K
# ==========================

def build_top_k_md(items: List[Dict[str, Any]], k: int = 3) -> str:
    """
    Construit une section Markdown 'Top k' à partir d'une liste d'items scorés.
    Tri: score desc puis date desc.
    """
    if not items:
        return "## 🏆 Top 3 de la semaine\n\n_Aucun article cette semaine._\n"

    top = sorted(
        items,
        key=lambda x: (int(x.get("score") or 0), int(x["published_ts"])),
        reverse=True,
    )[:k]

    lines = ["## 🏆 Top 3 de la semaine", ""]
    for i, it in enumerate(top, start=1):
        dt = datetime.fromtimestamp(it["published_ts"], tz=timezone.utc).strftime("%Y-%m-%d")
        title = it["title"]
        url = it["url"]
        src = it["source"]
        score = it.get("score", "?")
        lines.append(f"- **{i}.** [{title}]({url}) — {src} · {dt} · **{score}/100**")
    lines.append("")
    return "\n".join(lines)

# ==========================
#   Weeks index
# ==========================

def write_weeks_index(out_root: Path):
    """
    Génère export/weeks.json listant toutes les semaines (YYYYwWW),
    avec les chemins vers top3/selection et la plage de dates si dispo.
    (plus de résumé IA ici, ce sera fait par un autre script)
    """
    weeks = []
    for p in out_root.iterdir():
        if p.is_dir() and re.fullmatch(r"\d{4}w\d{2}", p.name):
            weeks.append(p.name)
    weeks.sort(reverse=True)  # plus récentes d'abord

    meta = []
    for w in weeks:
        week_dir = out_root / w
        range_txt = ""
        rp = week_dir / "range.txt"
        if rp.exists():
            range_txt = rp.read_text(encoding="utf-8").strip()

        meta.append({
            "week": w,
            "range": range_txt,
            "top3_md": f"export/{w}/top3.md",
            "selection_json": f"export/{w}/ai_selection.json",
            "selection_md": f"export/{w}/ai_selection.md",
        })

    (out_root / "weeks.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"[done] Index des semaines: {out_root / 'weeks.json'}")

# ==========================
#   Search Index
# ==========================

def build_search_index(db_path: str, out_root: Path):
    """
    Génère un fichier JSON plat contenant tous les articles pertinents (score > 0)
    pour la recherche client-side (Fuse.js).
    """
    with db_conn(db_path) as conn:
        rows = conn.execute("""
            SELECT id, title, url, source_name, published_ts, category_key, summary, final_score
            FROM items
            WHERE final_score IS NOT NULL AND final_score > 0
            ORDER BY published_ts DESC
        """).fetchall()
    
    index = []
    for r in rows:
        # On tronque le résumé pour ne pas faire un fichier de 50Mo
        summary = (r[6] or "")[:300]
        index.append({
            "id": r[0],
            "t": r[1],          # title (short key)
            "u": r[2],          # url
            "s": r[3],          # source
            "d": r[4],          # date (ts)
            "c": r[5],          # category
            "x": summary,       # excerpt
            "sc": int(r[7])     # score
        })
    
    out_path = out_root / "search.json"
    out_path.write_text(json.dumps(index, ensure_ascii=False), encoding="utf-8")
    print(f"[done] Index de recherche ({len(index)} items): {out_path}")

# ==========================
#   MAIN
# ==========================

def main(config_path: str = "config.yaml", limit: Optional[int] = None):
    cfg = yaml.safe_load(Path(config_path).read_text(encoding="utf-8"))

    db_path = cfg["storage"]["sqlite_path"]
    ensure_relevance_columns(db_path)

    relevance_cfg = cfg.get("relevance", {}) or {}
    default_threshold = int(relevance_cfg.get("score_threshold", 60))
    thresholds = cfg.get("category_thresholds", {}) or {}

    # Fenêtre semaine (Europe/Paris)
    week_offset = int(os.getenv("WEEK_OFFSET", "0"))
    week_start_ts, week_end_ts, week_label, week_start_h, week_end_h = week_bounds(
        "Europe/Paris", week_offset=week_offset
    )

    # --- Calcul / recalcul de la pertinence pour tous les items de la semaine ---
    with db_conn(db_path) as conn:
        rows = conn.execute(
            """
            SELECT id, url, source_name, title, summary, content, published_ts
            FROM items
            WHERE published_ts >= ? AND published_ts < ?
            ORDER BY published_ts DESC
            """,
            (week_start_ts, week_end_ts),
        ).fetchall()

        print(f"[diag] items dans la semaine: {len(rows)}")

        if limit is not None:
            rows = rows[:limit]

        for id_, url, src, title, summary, content, ts in rows:
            row = {
                "url": url,
                "source_name": src,
                "title": title,
                "summary": summary,
                "content": content,
            }
            scores = compute_relevance(row, cfg)
            conn.execute(
                """
                UPDATE items
                SET semantic_score=?, source_weight=?, quality_score=?, tech_score=?, final_score=?
                WHERE id=?
                """,
                (
                    scores["semantic_score"],
                    scores["source_weight"],
                    scores["quality_score"],
                    scores["tech_score"],
                    scores["final_score"],
                    id_,
                ),
            )

    # --- Comptage / stats ---
    with db_conn(db_path) as conn:
        recent_scored = conn.execute(
            """
            SELECT COUNT(*) FROM items
            WHERE published_ts >= ? AND published_ts < ? AND final_score IS NOT NULL
            """,
            (week_start_ts, week_end_ts),
        ).fetchone()[0]
    print(f"[diag] items avec final_score (semaine): {recent_scored}")

    # --- Dossier hebdo ---
    out_root = Path(cfg.get("export", {}).get("out_dir", "export"))
    week_dir = out_root / week_label
    week_dir.mkdir(parents=True, exist_ok=True)

    # --- Export sélection (seuils par catégorie) ---
    groups = group_filtered_with_thresholds(
        db_path=db_path,
        min_ts=week_start_ts,
        max_ts=week_end_ts,
        thresholds=thresholds,
        default_threshold=default_threshold,
    )
    json_path = week_dir / "ai_selection.json"
    md_path = week_dir / "ai_selection.md"
    json_path.write_text(json.dumps(groups, indent=2, ensure_ascii=False), encoding="utf-8")
    md_path.write_text(to_markdown(groups), encoding="utf-8")
    kept = sum(len(v) for v in groups.values())
    print(f"[done] Sélection (semaine {week_label}): {kept} items ≥ seuils")
    print(f" - {json_path}\n - {md_path}")

    # --- Top 3 global ---
    top_items = fetch_items_for_top(
        db_path, week_start_ts, week_end_ts, min_score=default_threshold
    )
    top_md = build_top_k_md(top_items, k=3)
    top3_path = week_dir / "top3.md"
    top3_path.write_text(top_md, encoding="utf-8")
    print(f"[done] Top 3: {top3_path}")

    # --- lien symbolique "latest" → cette semaine (best effort) ---
    latest = out_root / "latest"
    try:
        if latest.is_symlink() or latest.exists():
            latest.unlink()
        latest.symlink_to(week_dir, target_is_directory=True)
    except Exception:
        pass

    # --- range lisible pour la semaine ---
    range_path = week_dir / "range.txt"
    range_path.write_text(f"{week_start_h} → {week_end_h}\n", encoding="utf-8")

    # --- index global des semaines ---
    write_weeks_index(out_root)

    # --- index de recherche global ---
    build_search_index(db_path, out_root)

# ==========================
#   CLI
# ==========================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Analyse de pertinence (hebdomadaire, sans LLM)")
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--week-offset", type=int, default=None)
    args = parser.parse_args()
    if args.week_offset is not None:
        os.environ["WEEK_OFFSET"] = str(args.week_offset)
    main(args.config, limit=args.limit)