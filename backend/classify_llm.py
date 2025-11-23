# classify_llm.py
# Re-classification des articles par LLM (Groq/OpenAI-compat)
#
# Objectif :
# 1. Lire les items de la semaine (ou tout item sans 'llm_category_checked')
# 2. Envoyer titre + résumé + source au LLM
# 3. Le LLM choisit la meilleure catégorie parmi celles de config.yaml
#    ou "hors_sujet" si ça ne matche rien.
# 4. Update DB : category_key = nouvelle clé, et on marque l'item comme vérifié.

import os
import json
import asyncio
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional

from openai import OpenAI
from pydantic import BaseModel

from veille_tech import db_conn, week_bounds

# -----------------------
# Models
# -----------------------

class ClassificationResult(BaseModel):
    category_key: str
    confidence: int  # 0-100
    reasoning: str

# -----------------------
# DB Helpers
# -----------------------

def ensure_classification_columns(db_path: str):
    with db_conn(db_path) as conn:
        cols = [r[1] for r in conn.execute("PRAGMA table_info(items)").fetchall()]
        if "llm_classified" not in cols:
            # 0 = non, 1 = oui
            conn.execute("ALTER TABLE items ADD COLUMN llm_classified INTEGER DEFAULT 0")
        if "original_category_key" not in cols:
            conn.execute("ALTER TABLE items ADD COLUMN original_category_key TEXT")

def fetch_unclassified_items(db_path: str, min_ts: int, max_ts: int, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    with db_conn(db_path) as conn:
        q = """
        SELECT id, title, summary, content, source_name, category_key, url
        FROM items
        WHERE published_ts >= ? AND published_ts < ?
          AND (llm_classified IS NULL OR llm_classified = 0)
        ORDER BY published_ts DESC
        """
        params = [min_ts, max_ts]
        if limit:
            q += " LIMIT ?"
            params.append(limit)
        rows = conn.execute(q, params).fetchall()
    
    return [
        {
            "id": r[0], "title": r[1], "summary": r[2], "content": r[3],
            "source_name": r[4], "category_key": r[5], "url": r[6]
        }
        for r in rows
    ]

def update_item_category(db_path: str, item_id: str, new_cat: str, old_cat: str):
    with db_conn(db_path) as conn:
        conn.execute("""
            UPDATE items
            SET category_key = ?, original_category_key = ?, llm_classified = 1
            WHERE id = ?
        """, (new_cat, old_cat, item_id))

def mark_as_processed(db_path: str, item_id: str):
    """Marque comme traité même si pas de changement (ou erreur)"""
    with db_conn(db_path) as conn:
        conn.execute("UPDATE items SET llm_classified = 1 WHERE id = ?", (item_id,))

# -----------------------
# LLM Logic
# -----------------------

CLASSIFY_SYSTEM_PROMPT = """Tu es un expert en classification d'articles tech (Data Engineering, IA, Cloud).
Ta tâche est d'assigner la catégorie la plus pertinente à un article.

Voici les catégories disponibles (clé : description) :
{categories_desc}

Règles :
1. Choisis UNE seule clé parmi la liste.
2. Si l'article ne parle PAS de tech/data ou est du pur marketing/spam, utilise la clé 'hors_sujet'.
3. Sois précis. Un article sur "Kafka" va dans "Orchestration/Streaming" (ou équivalent), pas juste "News".
4. Réponds au format JSON : {{ "category_key": "...", "confidence": 80, "reasoning": "..." }}
"""

async def classify_items(
    items: List[Dict[str, Any]],
    categories: List[Dict[str, Any]],
    base_url: str,
    api_key_env: str,
    model: str,
    db_path: str,
    concurrency: int = 5
):
    api_key = os.getenv(api_key_env)
    if not api_key:
        print(f"[warn] {api_key_env} manquant, skip classification.")
        return

    client = OpenAI(base_url=base_url, api_key=api_key)
    
    # Construit la description des catégories pour le prompt
    cat_desc_lines = []
    valid_keys = set()
    for c in categories:
        k = c["key"]
        t = c.get("title", k)
        kws = ", ".join(c.get("keywords", [])[:5])
        cat_desc_lines.append(f"- {k}: {t} (ex: {kws})")
        valid_keys.add(k)
    
    cat_desc_lines.append("- hors_sujet: Contenu non pertinent, spam, ou hors scope Data/IA.")
    valid_keys.add("hors_sujet")
    
    system_prompt = CLASSIFY_SYSTEM_PROMPT.format(categories_desc="\n".join(cat_desc_lines))
    
    sem = asyncio.Semaphore(concurrency)

    async def process_one(it: Dict[str, Any]):
        async with sem:
            text_snippet = (it.get("title") or "") + "\n" + (it.get("summary") or "")
            content_snippet = (it.get("content") or "")[:1000]
            
            user_msg = f"""Titre: {it['title']}
Source: {it['source_name']}
URL: {it['url']}
Catégorie actuelle (mots-clés): {it['category_key']}

Contenu (extrait):
{text_snippet}
---
{content_snippet}
"""
            retries = 3
            for attempt in range(retries):
                try:
                    resp = await asyncio.to_thread(
                        client.chat.completions.create,
                        model=model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_msg}
                        ],
                        temperature=0.0,
                        response_format={"type": "json_object"}
                    )
                    raw = resp.choices[0].message.content
                    res = json.loads(raw)
                    
                    new_key = res.get("category_key")
                    if new_key not in valid_keys:
                        new_key = it["category_key"]
                    
                    if new_key != it["category_key"]:
                        update_item_category(db_path, it["id"], new_key, it["category_key"])
                        print(f"[CHANGE] {it['title'][:30]}... : {it['category_key']} -> {new_key}")
                    else:
                        mark_as_processed(db_path, it["id"])
                    
                    # Success, break retry loop
                    break

                except Exception as e:
                    is_rate_limit = "429" in str(e) or "Rate limit" in str(e)
                    if is_rate_limit and attempt < retries - 1:
                        wait_time = (attempt + 1) * 5  # 5s, 10s, 15s
                        print(f"[WARN] Rate limit for {it['id']}, waiting {wait_time}s...")
                        await asyncio.sleep(wait_time)
                    else:
                        print(f"[ERR] {it['id']} : {e}")
                        break

    await asyncio.gather(*[process_one(it) for it in items])

# -----------------------
# Main
# -----------------------

async def main(config_path: str = "config.yaml", limit: Optional[int] = None, force: bool = False):
    cfg = yaml.safe_load(Path(config_path).read_text(encoding="utf-8"))
    db_path = cfg["storage"]["sqlite_path"]
    
    ensure_classification_columns(db_path)
    
    # Config LLM
    llm_cfg = cfg.get("llm", {})
    base_url = llm_cfg.get("base_url", "https://api.groq.com/openai/v1")
    api_key_env = llm_cfg.get("api_key_env", "GROQ_API_KEY")
    model = llm_cfg.get("model", "llama-3.1-8b-instant")
    
    # Fenêtre temporelle
    week_offset = int(os.getenv("WEEK_OFFSET", "0"))
    start_ts, end_ts, _, _, _ = week_bounds("Europe/Paris", week_offset=week_offset)
    
    if force:
        print(f"[classify] FORCE: Réinitialisation du statut 'llm_classified' pour la semaine.")
        with db_conn(db_path) as conn:
            conn.execute(
                "UPDATE items SET llm_classified = 0 WHERE published_ts >= ? AND published_ts < ?",
                (start_ts, end_ts)
            )

    items = fetch_unclassified_items(db_path, start_ts, end_ts, limit=limit)
    print(f"[classify] {len(items)} items à classifier (semaine courante).")
    
    if items:
        await classify_items(
            items, 
            cfg["categories"], 
            base_url, 
            api_key_env, 
            model, 
            db_path,
            concurrency=2
        )

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--week-offset", type=int, default=None)
    parser.add_argument("--force", action="store_true", help="Force re-classification of all items")
    args = parser.parse_args()
    
    if args.week_offset is not None:
        os.environ["WEEK_OFFSET"] = str(args.week_offset)
        
    asyncio.run(main(args.config, limit=args.limit, force=args.force))
