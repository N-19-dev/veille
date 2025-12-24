// src/lib/parse.ts

export type WeekMeta = { week: string; range?: string };
export type TopItem = { title: string; url: string; source?: string; date?: string; score?: string|number; tech_level?: string; marketing_score?: number };
export type SectionItem = { title: string; url: string; source?: string; score?: string|number; content_type?: string; tech_level?: string; marketing_score?: number };
export type SummarySection = { title: string; items: SectionItem[] };

// Types pour les données JSON brutes
type RawSelectionItem = {
  title?: string;
  url?: string;
  source_name?: string;
  score?: number | string;
  content_type?: string;
  tech_level?: string;
  marketing_score?: number;
};

// ---------- helpers de chargement (inchangés si tu es en statique) ----------
async function loadText(relativePath: string): Promise<string> {
  const cleanPath = relativePath.startsWith("/") ? relativePath.slice(1) : relativePath;
  const base = typeof document !== "undefined" ? document.baseURI : "/";
  const finalUrl = new URL(cleanPath, base).toString();
  const res = await fetch(finalUrl, { cache: "no-store" });
  if (!res.ok) throw new Error(`Impossible de charger ${finalUrl} (${res.status})`);
  return new TextDecoder().decode(await res.arrayBuffer());
}

export async function loadWeeksIndex() {
  try {
    const txt = await loadText("export/weeks.json");
    const arr = JSON.parse(txt) as Array<{ week: string; range?: string; summary_md?: string }>;
    return (arr || []).sort((a, b) => (a.week < b.week ? 1 : -1));
  } catch {
    return [{ week: "latest", range: "" }];
  }
}

function summaryPath(meta: { week: string; summary_md?: string }): string {
  if (meta.summary_md) return meta.summary_md.replace(/^export\//, "export/");
  return meta.week === "latest" ? "export/latest/ai_summary.md" : `export/${meta.week}/ai_summary.md`;
}

// ---------- PARSING ----------
// 👉 Extrait le bloc "Aperçu général de la semaine"
function parseOverview(md: string): string {
  const rx = /(^|\n)##\s*(?:🟦\s*)?Aperçu général de la semaine\s*\n([\s\S]*?)(\n##\s|$)/i;
  const m = md.match(rx);
  return m ? m[2].trim() : "";
}

// ---------- Chargement des catégories ----------
let _categoriesCache: Record<string, string> | null = null;

async function loadCategories(): Promise<Record<string, string>> {
  if (_categoriesCache) return _categoriesCache;
  try {
    const txt = await loadText("export/categories.json");
    _categoriesCache = JSON.parse(txt);
    return _categoriesCache!;
  } catch {
    return {}; // Fallback si le fichier n'existe pas
  }
}

// ---------- Chargement de la sélection JSON ----------
function selectionPath(meta: WeekMeta): string {
  return meta.week === "latest"
    ? "export/latest/ai_selection.json"
    : `export/${meta.week}/ai_selection.json`;
}

async function loadSelectionJson(meta: WeekMeta): Promise<Record<string, RawSelectionItem[]>> {
  try {
    const txt = await loadText(selectionPath(meta));
    return JSON.parse(txt);
  } catch {
    return {}; // Fallback si le fichier n'existe pas
  }
}

// ---------- Chargement du top3 JSON ----------
async function loadTop3Json(meta: WeekMeta): Promise<TopItem[]> {
  try {
    const path = meta.week === "latest"
      ? "export/latest/top3.json"
      : `export/${meta.week}/top3.json`;
    const txt = await loadText(path);
    const data = JSON.parse(txt) as RawSelectionItem[];
    return data.map((item) => ({
      title: item.title || "",
      url: item.url || "",
      source: item.source_name || "",
      score: item.score,
      tech_level: item.tech_level || "intermediate",
      marketing_score: item.marketing_score || 0,
    }));
  } catch {
    return []; // Fallback si le fichier n'existe pas
  }
}

// ---------- API principale ----------
export async function loadWeekSummary(meta: WeekMeta): Promise<{
  overview: string;
  top3: TopItem[];
  sections: SummarySection[];
}> {
  // Charger le markdown pour overview uniquement
  const md = await loadText(summaryPath(meta));

  // Charger le JSON pour top3 et sections
  const top3Data = await loadTop3Json(meta);
  const selectionData = await loadSelectionJson(meta);
  const categories = await loadCategories();

  // Transformer le JSON en sections
  const sections: SummarySection[] = [];

  // Parcourir dans l'ordre des catégories
  for (const [categoryKey, items] of Object.entries(selectionData)) {
    const categoryTitle = categories[categoryKey] || categoryKey;

    const sectionItems: SectionItem[] = items.map((item) => ({
      title: item.title || "",
      url: item.url || "",
      source: item.source_name || "",
      score: item.score,
      content_type: item.content_type || "technical",
      tech_level: item.tech_level || "intermediate",
      marketing_score: item.marketing_score || 0,
    }));

    if (sectionItems.length > 0) {
      sections.push({ title: categoryTitle, items: sectionItems });
    }
  }

  return {
    overview: parseOverview(md),
    top3: top3Data,
    sections,
  };
}
export async function loadLatestWeek(): Promise<WeekMeta> {
  const arr = await loadWeeksIndex();
  // Si weeks.json est vide ou absent, on retombe sur "latest"
  return arr[0] ?? { week: "latest", range: "" };
}

// ---------- Utils visuels (inchangés) ----------
export function getDomain(url?: string): string | null {
  if (!url) return null;
  try { return new URL(url).hostname.replace(/^www\./, ""); } catch { return null; }
}
export function faviconUrl(url?: string, size = 32): string {
  const dom = getDomain(url);
  return dom ? `https://www.google.com/s2/favicons?domain=${dom}&sz=${size}` : `https://via.placeholder.com/${size}`;
}