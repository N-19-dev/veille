#!/usr/bin/env python3
"""
Script pour générer ai_summary.md directement depuis ai_selection.json
sans passer par le LLM, garantissant le bon format pour le parser frontend.
"""
import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone
import yaml

def load_config(config_path: str = "config.yaml"):
    """Charge la configuration."""
    return yaml.safe_load(Path(config_path).read_text(encoding="utf-8"))

def get_category_title(cfg, category_key: str) -> str:
    """Récupère le titre lisible d'une catégorie."""
    for cat in cfg.get("categories", []):
        if cat.get("key") == category_key:
            return cat.get("title", category_key)
    return category_key

def generate_summary_md(selection_json_path: Path, cfg) -> str:
    """Génère le contenu markdown du résumé."""
    data = json.loads(selection_json_path.read_text(encoding="utf-8"))
    
    lines = []
    
    # Aperçu général
    lines.append("## Aperçu général de la semaine")
    lines.append("")
    lines.append("Cette semaine, nous avons sélectionné les articles les plus pertinents dans chaque catégorie.")
    lines.append("")
    
    # Sections par catégorie
    for cat in cfg.get("categories", []):
        cat_key = cat.get("key")
        cat_title = cat.get("title", cat_key)
        
        lines.append(f"## {cat_title}")
        lines.append("")
        
        items = data.get(cat_key, [])
        if not items:
            lines.append("_Rien d'important cette semaine._")
            lines.append("")
            continue
        
        # Trier par score décroissant
        items_sorted = sorted(items, key=lambda x: float(x.get("score", 0)), reverse=True)
        
        for item in items_sorted:
            title = item.get("title", "")
            url = item.get("url", "")
            source = item.get("source_name", "")
            score = item.get("score", 0)
            ts = item.get("published_ts", 0)
            
            # Format date
            date_str = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")
            
            # Format: - [Title](url) — Source · Date · **Score/100**
            lines.append(f"- [{title}]({url}) — {source} · {date_str} · **{score}/100**")
        
        lines.append("")
    
    return "\n".join(lines)

def main(week_offset: int = 0):
    """Génère ai_summary.md pour une semaine donnée."""
    cfg = load_config()
    
    # Calculer le label de semaine
    from veille_tech import week_bounds
    _, _, week_label, _, _ = week_bounds("Europe/Paris", week_offset=week_offset)
    
    # Chemins
    out_root = Path(cfg.get("export", {}).get("out_dir", "export"))
    week_dir = out_root / week_label
    selection_json = week_dir / "ai_selection.json"
    summary_md = week_dir / "ai_summary.md"
    
    if not selection_json.exists():
        print(f"[error] Fichier introuvable: {selection_json}")
        sys.exit(1)
    
    # Générer le résumé
    content = generate_summary_md(selection_json, cfg)
    summary_md.write_text(content, encoding="utf-8")
    
    print(f"[done] Résumé généré: {summary_md}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Génère ai_summary.md depuis ai_selection.json")
    parser.add_argument("--week-offset", type=int, default=0, help="Offset de semaine (0=cette semaine, -1=semaine dernière)")
    args = parser.parse_args()
    main(args.week_offset)
