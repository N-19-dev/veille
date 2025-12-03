// src/lib/parse.ts

export type WeekMeta = { week: string; range?: string };
export type TopItem = { title: string; url: string; source?: string; date?: string; score?: string | number };
export type SectionItem = { title: string; url: string; source?: string; score?: string | number; description?: string };
export type SummarySection = { title: string; items: SectionItem[] };

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
function parseTop3(md: string): TopItem[] {
  const out: TopItem[] = [];
  const topHeader = /(^|\n)##\s*🏆?\s*Top\s*3[^\n]*\n([\s\S]*?)(\n##\s|$)/i;
  const m = md.match(topHeader);
  if (!m) return out;
  const block = m[2];
  const itemRe =
    /^\s*[-–•]\s*(?:\*\*\d+\.\*\*\s*)?\[(.+?)\]\((https?:\/\/[^\s)]+)\)\s*—\s*([^·\n]+)?(?:\s*·\s*([\d-]{8,10}))?(?:\s*·\s*\*\*(\d+)\s*\/\s*100\*\*)?/gim;
  let mm: RegExpExecArray | null;
  while ((mm = itemRe.exec(block)) && out.length < 3) {
    out.push({ title: mm[1]?.trim(), url: mm[2]?.trim(), source: mm[3]?.trim(), date: mm[4]?.trim(), score: mm[5]?.trim() });
  }
  return out;
}

// 👉 NOUVEAU : extrait le bloc “Aperçu général de la semaine” ou “Tendances de la semaine”
function parseOverview(md: string): string {
  const rx = /(^|\n)##\s*(?:🟦\s*)?(?:Aperçu général|Tendances) de la semaine\s*\n([\s\S]*?)(\n##\s|$)/i;
  const m = md.match(rx);
  return m ? m[2].trim() : "";
}

function parseSections(md: string): SummarySection[] {
  const sections: SummarySection[] = [];
  const h2Re = /(^|\n)##\s+([^\n]+)\n/gm;
  const indices: Array<{ title: string; start: number; end: number }> = [];
  let match: RegExpExecArray | null;
  while ((match = h2Re.exec(md))) {
    const title = match[2].trim();
    const start = match.index + match[0].length;
    indices.push({ title, start, end: md.length });
    if (indices.length > 1) indices[indices.length - 2].end = match.index;
  }
  for (const seg of indices) {
    const title = seg.title;
    if (/(aperçu général|tendances) de la semaine/i.test(title)) continue; // on évite le bloc overview ici
    const block = md.slice(seg.start, seg.end).trim();

    // Nouvelle regex pour le format multi-lignes
    // ### Titre
    // *Source : ...*
    // * **Pourquoi c'est important :** ...
    // *Lien :* url
    const items: SectionItem[] = [];

    // Regex plus souple pour capturer le bloc entier d'un item
    // On cherche un titre (### ou **) suivi de lignes jusqu'au prochain titre ou fin de bloc

    // On va itérer sur les blocs commençant par ### ou **
    // const itemSplitRe = /(?:^|\n)(?:###|\*\*)\s*(.+?)(?:\*\*|(?:\n|$))/g;

    // Cette approche par split est compliquée car on veut capturer le contenu après.
    // Essayons une regex qui capture chaque item complet.

    // Format observé :
    // ### Title
    // *Source : Source (Date)*
    // * **Pourquoi c'est important :** Desc
    // *Lien :* url

    const itemRe = /(?:^|\n)(?:###|\*\*)\s*([^\n*]+)(?:\*\*)?\s*\n\s*\*Source\s*:\s*([^(]+)\s*(?:\(([^)]+)\))?\*\s*\n\s*\*\s*\*\*Pourquoi c'est important\s*:\*\*\s*([^\n]+)\s*\n\s*\*(?:Lien|Link)[^:]*:\*\s*(?:\[([^\]]+)\]\(([^)]+)\)|(https?:\/\/[^\s]+))/gim;

    let lm: RegExpExecArray | null;
    let foundNewFormat = false;

    while ((lm = itemRe.exec(block))) {
      foundNewFormat = true;
      const rawUrl = lm[7];
      const mdUrl = lm[6];
      // const mdText = lm[5]; // unused

      items.push({
        title: lm[1]?.trim(),
        source: lm[2]?.trim(),
        // date: lm[3]?.trim(),
        description: lm[4]?.trim(),
        url: (mdUrl || rawUrl || "").trim(),
        score: 0
      });
    }

    if (!foundNewFormat) {
      // Fallback ancien format
      const lineRe =
        /^\s*[-–•]\s*\[(.+?)\]\((https?:\/\/[^\s)]+)\)\s*(?:—\s*([^·\n]+))?(?:\s*·\s*([\d-]{8,10}))?(?:\s*·\s*\*\*(\d+)\s*\/\s*100\*\*)?/gim;
      while ((lm = lineRe.exec(block))) {
        items.push({ title: lm[1]?.trim(), url: lm[2]?.trim(), source: lm[3]?.trim(), score: lm[5]?.trim() });
      }
    }

    if (items.length) sections.push({ title, items });
  }
  return sections;
}

// ---------- API principale ----------
export async function loadWeekSummary(meta: WeekMeta): Promise<{
  overview: string;          // <- nouveau
  top3: TopItem[];
  sections: SummarySection[];
}> {
  const md = await loadText(summaryPath(meta));
  return {
    overview: parseOverview(md),
    top3: parseTop3(md),
    sections: parseSections(md),
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