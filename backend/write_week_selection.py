# backend/write_week_selection.py
# Backfill: insère dans la DB la sélection d'une semaine
# depuis export/<YYYYwWW>/ai_selection.json
#
# Usage:
#   python write_week_selection.py 2025w42 [veille.db] [export_dir]
#
# Effets:
#   - crée/maintient tables weeks + weekly_selection
#   - calcule les bornes exactes de la semaine (Europe/Paris) depuis le label YYYYwWW
#   - insère la sélection (classée) en reliant via items.url -> items.id
#   - si une URL n’est pas trouvée dans la fenêtre, tente hors fenêtre (fallback)

import re
import sys
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

from veille_tech import db_conn

# -----------------------
# Helpers DB (autonomes)
# -----------------------

def ensure_selection_schema(db_path: str):
    with db_conn(db_path) as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS weeks(
          week_label   TEXT PRIMARY KEY,
          start_ts     INTEGER NOT NULL,
          end_ts       INTEGER NOT NULL,
          start_date   TEXT NOT NULL,
          end_date     TEXT NOT NULL,
          created_ts   INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS weekly_selection(
          week_label   TEXT NOT NULL,
          item_id      TEXT NOT NULL,
          category_key TEXT NOT NULL,
          rank_in_cat  INTEGER NOT NULL,
          score        INTEGER,
          PRIMARY KEY (week_label, item_id)
        );
        CREATE INDEX IF NOT EXISTS idx_weekly_selection_week
          ON weekly_selection(week_label);
        CREATE INDEX IF NOT EXISTS idx_weekly_selection_week_cat_rank
          ON weekly_selection(week_label, category_key, rank_in_cat);
        """)

def upsert_week(db_path: str, week_label: str, start_ts: int, end_ts: int,
                start_date: str, end_date: str):
    now = int(datetime.now(tz=timezone.utc).timestamp())
    with db_conn(db_path) as conn:
        conn.execute("""
            INSERT INTO weeks(week_label, start_ts, end_ts, start_date, end_date, created_ts)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(week_label) DO UPDATE SET
              start_ts=excluded.start_ts,
              end_ts=excluded.end_ts,
              start_date=excluded.start_date,
              end_date=excluded.end_date
        """, (week_label, start_ts, end_ts, start_date, end_date, now))

def write_weekly_selection(db_path: str, week_label: str,
                           groups: dict,
                           min_ts: int, max_ts: int):
    """
    groups: dict {cat_key: [ {url, title, score?, ...}, ... ]}
    On relie chaque entrée à items.id via URL. On privilégie la fenêtre hebdo,
    sinon fallback sans fenêtre.
    """
    with db_conn(db_path) as conn:
        # Map URL -> (id, score) dans la fenêtre
        rows = conn.execute("""
            SELECT id, url, COALESCE(final_score, llm_score) as score
            FROM items
            WHERE published_ts >= ? AND published_ts < ?
        """, (min_ts, max_ts)).fetchall()
        by_url_week = {r[1]: (r[0], r[2]) for r in rows}

        # Purge de la semaine
        conn.execute("DELETE FROM weekly_selection WHERE week_label=?", (week_label,))

        for cat, arr in groups.items():
            for rank, it in enumerate(arr, start=1):
                url = it.get("url")
                item_id = None
                score = it.get("score")

                # 1) recherche dans la fenêtre
                if url in by_url_week:
                    item_id, s = by_url_week[url]
                    if s is not None:
                        score = s
                else:
                    # 2) fallback global par URL exacte
                    row = conn.execute("""
                        SELECT id, COALESCE(final_score, llm_score) as score
                        FROM items WHERE url=? LIMIT 1
                    """, (url,)).fetchone()
                    if row:
                        item_id, s = row[0], row[1]
                        if s is not None:
                            score = s

                if item_id:
                    conn.execute("""
                        INSERT INTO weekly_selection(week_label, item_id, category_key, rank_in_cat, score)
                        VALUES(?, ?, ?, ?, ?)
                    """, (week_label, item_id, cat, rank, int(score) if score is not None else None))

# -----------------------
# Semaine depuis label
# -----------------------

def week_bounds_from_label(label: str, tz_name: str = "Europe/Paris"):
    """
    Convertit 'YYYYwWW' en bornes [lundi 00:00, lundi+7 00:00[ en UTC,
    et renvoie (start_ts, end_ts, start_str, end_str) avec dates locales ISO.
    """
    m = re.fullmatch(r"(\d{4})w(\d{2})", label)
    if not m:
        raise ValueError(f"Label de semaine invalide: {label}")
    year = int(m.group(1))
    week = int(m.group(2))
    tz = ZoneInfo(tz_name)

    # Lundi (1) de cette semaine ISO en heure locale
    monday_local = datetime.fromisocalendar(year, week, 1).replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=tz)
    end_local = monday_local + timedelta(days=7)

    start_ts = int(monday_local.astimezone(timezone.utc).timestamp())
    end_ts = int(end_local.astimezone(timezone.utc).timestamp())
    return start_ts, end_ts, monday_local.strftime("%Y-%m-%d"), end_local.strftime("%Y-%m-%d")

# -----------------------
# Main
# -----------------------

def main(week_label: str, db_path: str = "veille.db", export_root: str = "export"):
    export_dir = Path(export_root) / week_label
    sel_path = export_dir / "ai_selection.json"
    if not sel_path.exists():
        print(f"[err] Fichier introuvable: {sel_path}")
        sys.exit(1)

    # Charger la sélection
    groups = json.loads(sel_path.read_text(encoding="utf-8"))
    # Calculer bornes à partir du label (fiable)
    start_ts, end_ts, start_str, end_str = week_bounds_from_label(week_label, "Europe/Paris")

    ensure_selection_schema(db_path)
    upsert_week(db_path, week_label, start_ts, end_ts, start_str, end_str)
    write_weekly_selection(db_path, week_label, groups, start_ts, end_ts)

    print(f"[done] weekly_selection insérée pour {week_label}")
    print(f"       semaine: {start_str} → {end_str} (label {week_label})")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python write_week_selection.py <YYYYwWW> [veille.db] [export_dir]")
        sys.exit(1)
    week_label = sys.argv[1]
    db_path = sys.argv[2] if len(sys.argv) > 2 else "veille.db"
    export_dir = sys.argv[3] if len(sys.argv) > 3 else "export"
    main(week_label, db_path=db_path, export_root=export_dir)