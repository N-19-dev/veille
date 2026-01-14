import { faviconUrl, getDomain } from "../lib/parse";

type VideoItem = {
  title: string;
  url: string;
  source: string;
  date?: string;
  score?: number;
  source_type?: "youtube" | "podcast";
};

export default function TopVideos({ items }: { items: VideoItem[] }) {
  if (!items?.length) return null;

  return (
    <section>
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-lg font-semibold">🎥 Top 3 Vidéos / Podcasts</h2>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {items.map((it, i) => {
          const dom = getDomain(it.url);
          const displaySource = (it.source || dom || "Source").trim();
          const emoji = it.source_type === "youtube" ? "🎥" : "🎙️";

          return (
            <a
              key={i}
              href={it.url}
              target="_blank"
              rel="noreferrer"
              className="group block rounded-2xl border bg-white p-4 hover:shadow-sm transition"
            >
              <div className="mb-3 flex items-center gap-2">
                {/* Emoji pour le type de média */}
                <span className="text-lg" title={it.source_type === "youtube" ? "YouTube" : "Podcast"}>
                  {emoji}
                </span>
                <span className="text-[11px] font-semibold uppercase tracking-widest text-neutral-600">
                  {displaySource}
                </span>
                {it.date && <span className="text-[11px] text-neutral-400">· {it.date}</span>}
              </div>

              {/* Barre d'accent "magazine" avec couleur spécifique pour vidéo */}
              <div className="mb-3 h-1 w-12 rounded-full bg-gradient-to-r from-purple-300 to-blue-300 group-hover:from-purple-400 group-hover:to-blue-400" />

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
