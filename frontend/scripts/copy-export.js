// frontend/scripts/copy-export.js
import { existsSync, rmSync, mkdirSync, readdirSync, lstatSync, readFileSync, cpSync } from "fs";
import { resolve, join } from "path";

const SRC = resolve(process.cwd(), "..", "backend", "export"); // <-- export/ côté backend
const DST = resolve(process.cwd(), "public", "export");

function isWeekDir(name) {
  return /^\d{4}w\d{2}$/.test(name);
}

function pickLatestWeek(srcDir) {
  // 1) essaie via weeks.json (plus fiable)
  const weeksJson = join(srcDir, "weeks.json");
  if (existsSync(weeksJson)) {
    try {
      const arr = JSON.parse(readFileSync(weeksJson, "utf-8"));
      if (Array.isArray(arr) && arr.length) {
        // weeks.json est déjà trié desc dans ton backend, sinon on trie
        const sorted = [...arr].sort((a, b) => (a.week < b.week ? 1 : -1));
        return sorted[0].week;
      }
    } catch {}
  }
  // 2) fallback : prend le max lexicographique des dossiers YYYYwWW
  const entries = readdirSync(srcDir, { withFileTypes: true })
    .filter(d => d.isDirectory() && isWeekDir(d.name))
    .map(d => d.name)
    .sort()
    .reverse();
  return entries[0] || null;
}

function copyDir(src, dst) {
  cpSync(src, dst, { recursive: true });
}

(function main() {
  if (!existsSync(SRC)) {
    console.error(`[copy-export] ❌ Source introuvable: ${SRC}. Lance d'abord: python backend/main.py`);
    process.exit(1);
  }

  // reset destination
  if (existsSync(DST)) rmSync(DST, { recursive: true, force: true });
  mkdirSync(DST, { recursive: true });

  // 1) copie tout SAUF le symlink "latest"
  const entries = readdirSync(SRC, { withFileTypes: true });
  for (const ent of entries) {
    const srcPath = join(SRC, ent.name);
    const dstPath = join(DST, ent.name);
    if (ent.name === "latest") {
      // on saute le lien symbolique
      continue;
    }
    // copie fichiers (weeks.json, etc.) et dossiers semaines
    if (ent.isSymbolicLink && ent.name === "latest") continue;
    copyDir(srcPath, dstPath);
  }

  // 2) (re)crée un dossier "latest" *réel* en dupliquant la dernière semaine
  const latestWeek = pickLatestWeek(SRC);
  if (!latestWeek) {
    console.warn("[copy-export] ⚠️ Aucune semaine détectée, pas de latest/");
  } else {
    const srcWeek = join(SRC, latestWeek);
    const dstLatest = join(DST, "latest");
    mkdirSync(dstLatest, { recursive: true });
    copyDir(srcWeek, dstLatest);
    console.log(`[copy-export] ✅ latest → ${latestWeek} (copié en dossier réel)`);
  }

  console.log(`[copy-export] ✅ Copié ${SRC} → ${DST}`);
})();