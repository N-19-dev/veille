// src/lib/parse.ts
// Chargement depuis l’API FastAPI (DB) + types + utilitaires

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export type WeekMeta = {
  week: string;           // "2025w42" ou "latest"
  range?: string;         // "13 Oct 2025 → 19 Oct 2025"
};

export type TopItem = {
  title: string;
  url: string;
  source?: string;
  date?: string;
  score?: string | number;
};

export type SectionItem = {
  title: string;
  url: string;
  source?: string;
  score?: string | number;
};

export type SummarySection = {
  title: string;
  items: SectionItem[];
};

// --------------------
// API HTTP helpers
// --------------------

async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`API ${path} ${res.status} ${text}`);
  }
  return res.json() as Promise<T>;
}

// --------------------
// Chargement semaines
// --------------------

export async function loadWeeksIndex(): Promise<WeekMeta[]> {
  // Ex: [{week:"2025w45", range:"..."}, {week:"2025w44", ...}]
  const weeks = await apiGet<WeekMeta[]>("/api/weeks");
  // On s’assure que c’est trié décroissant (au cas où le backend change)
  return (weeks || []).sort((a, b) => (a.week < b.week ? 1 : -1));
}

export async function loadLatestWeek(): Promise<WeekMeta> {
  return apiGet<WeekMeta>("/api/week/latest");
}

// --------------------
// Chargement contenu
// --------------------

export async function loadWeekTop3(week: WeekMeta): Promise<TopItem[]> {
  if (!week?.week) return [];
  // Ex: [{title,url,source,date,score}]
  return apiGet<TopItem[]>(`/api/week/${encodeURIComponent(week.week)}/top3`);
}

export async function loadWeekSelection(
  week: WeekMeta
): Promise<SummarySection[]> {
  if (!week?.week) return [];
  // Ex: { sections: [{title, items:[{title,url,source,score}]}] }
  const data = await apiGet<{ sections: SummarySection[] }>(
    `/api/week/${encodeURIComponent(week.week)}/sections`
  );
  return data?.sections || [];
}

export async function loadWeekSummary(week: WeekMeta): Promise<{
  top3: TopItem[];
  sections: SummarySection[];
}> {
  const [top3, sections] = await Promise.all([
    loadWeekTop3(week),
    loadWeekSelection(week),
  ]);
  return { top3, sections };
}

// --------------------
// Utils visuels
// --------------------

export function getDomain(url?: string): string | null {
  if (!url) return null;
  try {
    const u = new URL(url);
    return u.hostname.replace(/^www\./, "");
  } catch {
    return null;
  }
}

export function faviconUrl(url?: string, size = 32): string {
  const dom = getDomain(url);
  if (!dom) return `https://via.placeholder.com/${size}`;
  return `https://www.google.com/s2/favicons?domain=${dom}&sz=${size}`;
}