type TechLevel = 'beginner' | 'intermediate' | 'advanced';
type Item = {
  title: string;
  url: string;
  source: string;
  date?: string;
  score?: number;
  tech_level?: TechLevel;
  marketing_score?: number;
};

// Badge de niveau technique (même style que ArticleCard)
const LevelBadge = ({ level }: { level: TechLevel }) => {
  if (level === 'beginner') {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium border bg-green-100 text-green-800 border-green-200">
        <span>🟢</span>
        <span>Débutant</span>
      </span>
    );
  }

  if (level === 'advanced') {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium border bg-red-100 text-red-800 border-red-200">
        <span>🔴</span>
        <span>Avancé</span>
      </span>
    );
  }

  // intermediate (default)
  return (
    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium border bg-yellow-100 text-yellow-800 border-yellow-200">
      <span>🟡</span>
      <span>Intermédiaire</span>
    </span>
  );
};

export default function Top3({ items }: { items: Item[] }) {
  if (!items?.length) return null;
  return (
    <section>
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-lg font-semibold">🏆 Top 3 de la semaine</h2>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {items.map((it, i) => (
          <a
            key={i}
            href={it.url}
            target="_blank"
            rel="noreferrer"
            className="group block rounded-2xl border bg-white p-4 hover:shadow-sm transition"
          >
            <div className="flex items-center gap-2 flex-wrap text-xs text-neutral-500 mb-1">
              <span>{it.source}{it.date ? ` · ${it.date}` : ""}</span>
              {it.tech_level && <LevelBadge level={it.tech_level} />}
            </div>
            <div className="mt-1 font-medium leading-snug group-hover:underline">{it.title}</div>
          </a>
        ))}
      </div>
    </section>
  );
}