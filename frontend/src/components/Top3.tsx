type Item = { title: string; url: string; source: string; date?: string; score?: number };

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
            <div className="text-xs text-neutral-500">
              {it.source}{it.date ? ` · ${it.date}` : ""}
            </div>
            <div className="mt-1 font-medium leading-snug group-hover:underline">{it.title}</div>
            {typeof it.score === "number" && (
              <div className="mt-2 text-xs text-neutral-500">Score: {it.score}</div>
            )}
          </a>
        ))}
      </div>
    </section>
  );
}