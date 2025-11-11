# api_server.py
# REST API read-only pour exposer la veille depuis veille.db
import os
import sqlite3
from pathlib import Path
from typing import Dict, Any, List, Optional

import yaml
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# ---------- Config / DB helpers ----------
ROOT = Path(__file__).parent
CONFIG_PATH = ROOT / "config.yaml"
CFG = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))

DB_PATH = ROOT / CFG["storage"]["sqlite_path"]

# map key -> title (pour jolis titres de sections)
CAT_TITLES = {c.get("key"): c.get("title", c.get("key")) for c in CFG.get("categories", [])}

def row_factory(cursor, row):
    return {col[0]: row[i] for i, col in enumerate(cursor.description)}

def db():
    if not DB_PATH.exists():
        raise RuntimeError(f"DB introuvable: {DB_PATH}")
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = row_factory
    return conn

# ---------- FastAPI ----------
app = FastAPI(title="Veille Tech API", version="1.0")

# CORS: autorise le front local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # serre plus fin si besoin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Endpoints ----------

@app.get("/api/health")
def health():
    return {"ok": True}

@app.get("/api/weeks")
def list_weeks() -> List[Dict[str, Any]]:
    """
    Liste des semaines disponibles depuis la table weeks (créée par analyze_llm / write_week_selection).
    Format: [{week, range}]
    """
    with db() as conn:
        try:
            rows = conn.execute(
                "SELECT week_label AS week, start_date || ' → ' || end_date AS range "
                "FROM weeks ORDER BY week_label DESC"
            ).fetchall()
        except sqlite3.OperationalError:
            # fallback: dériver depuis weekly_selection si weeks manque
            rows = conn.execute(
                "SELECT DISTINCT week_label AS week, '' AS range "
                "FROM weekly_selection ORDER BY week DESC"
            ).fetchall()
    return rows

@app.get("/api/week/{week_label}/top3")
def get_top3(week_label: str) -> List[Dict[str, Any]]:
    """
    Top 3 par score puis date pour une semaine.
    """
    with db() as conn:
        rows = conn.execute("""
            SELECT i.title, i.url, i.source_name AS source,
                   datetime(i.published_ts, 'unixepoch') AS published_iso,
                   COALESCE(ws.score, i.final_score, i.llm_score) AS score
            FROM weekly_selection ws
            JOIN items i ON i.id = ws.item_id
            WHERE ws.week_label=?
            ORDER BY ws.score DESC, i.published_ts DESC
            LIMIT 3
        """, (week_label,)).fetchall()
    # format léger
    out = []
    for r in rows:
        out.append({
            "title": r["title"],
            "url": r["url"],
            "source": r["source"],
            "date": (r["published_iso"] or "")[:10],
            "score": r["score"],
        })
    return out

@app.get("/api/week/{week_label}/sections")
def get_sections(week_label: str) -> Dict[str, Any]:
    """
    Regroupe les articles sélectionnés par catégorie, classés par rank_in_cat.
    Retour: { sections: [ { title, items: [ {title,url,source,score} ] } ] }
    """
    with db() as conn:
        rows = conn.execute("""
            SELECT ws.category_key, ws.rank_in_cat,
                   i.title, i.url, i.source_name AS source,
                   COALESCE(ws.score, i.final_score, i.llm_score) AS score
            FROM weekly_selection ws
            JOIN items i ON i.id = ws.item_id
            WHERE ws.week_label=?
            ORDER BY ws.category_key ASC, ws.rank_in_cat ASC
        """, (week_label,)).fetchall()

    by_cat: Dict[str, List[Dict[str, Any]]] = {}
    for r in rows:
        by_cat.setdefault(r["category_key"], []).append({
            "title": r["title"],
            "url": r["url"],
            "source": r["source"],
            "score": r["score"],
        })

    sections = [{
        "title": CAT_TITLES.get(cat, cat),
        "items": items
    } for cat, items in by_cat.items()]

    # tri optionnel: sections les plus fournies d'abord
    sections.sort(key=lambda s: len(s["items"]), reverse=True)
    return {"sections": sections}

@app.get("/api/week/latest")
def get_latest_week():
    """
    Renvoie la semaine la plus récente {week, range}
    """
    with db() as conn:
        row = conn.execute(
            "SELECT week_label AS week, start_date || ' → ' || end_date AS range "
            "FROM weeks ORDER BY week_label DESC LIMIT 1"
        ).fetchone()
    if not row:
        raise HTTPException(404, "Aucune semaine disponible")
    return row