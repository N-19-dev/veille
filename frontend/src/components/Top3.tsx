import { faviconUrl, getDomain } from "../lib/parse";

type Item = {
  title: string;
  url: string;
  source: string;
  date?: string;
  score?: number;
};

export default function Top3({ items }: { items: Item[] }) {
  if (!items?.length) return null;
  return (
    <section>
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-lg font-semibold">🏆 Top 3 de la semaine</h2>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {items.map((it, i) => {
          const dom = getDomain(it.url);
          const displaySource = (it.source || dom || "Source").trim();

          return (
            <a
              key={i}
              href={it.url}
              target="_blank"
              rel="noreferrer"
              className="group block rounded-2xl border bg-white p-4 hover:shadow-sm transition"
            >
              <div className="mb-3 flex items-center gap-2">
                {/* Favicon avec fallback silencieux */}
                <img
                  src={faviconUrl(it.url, 64)}
                  alt=""
                  className="h-5 w-5 rounded-sm border object-contain"
                  loading="lazy"
                  onError={(e) => {
                    (e.currentTarget as HTMLImageElement).style.display = "none";
                  }}
                />
                <span className="text-[11px] font-semibold uppercase tracking-widest text-neutral-600">
                  {displaySource}
                </span>
                {it.date && <span className="text-[11px] text-neutral-400">· {it.date}</span>}
              </div>

              {/* Barre d'accent "magazine" */}
              <div className="mb-3 h-1 w-12 rounded-full bg-gradient-to-r from-neutral-300 to-neutral-200 group-hover:from-neutral-400 group-hover:to-neutral-200" />

              <h4 className="line-clamp-3 font-semibold leading-snug group-hover:underline">
                {it.title}
              </h4>
            </a>
          );
        })}
      </div>
    </section>
  );
}