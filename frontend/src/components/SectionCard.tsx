// src/components/SectionCard.tsx
// Rubrique magazine : un lead + secondaires (max 6) avec accent visuel.

import ArticleCard from "./ArticleCard";

type Article = {
  title: string;
  url?: string;
  source?: string;
  date?: string;
  score?: number | string;
  description?: string;
};

export default function SectionCard({
  title,
  bullets,
}: {
  title: string;
  bullets: Article[];
}) {
  if (!bullets?.length) return null;

  const [lead, ...rest] = bullets;

  return (
    <section className="bg-white border rounded-2xl p-5 hover:shadow-sm transition">
      <div className="mb-4">
        <h3 className="text-xl font-bold leading-tight">{title}</h3>
        {/* accent line — utilise bg-accent si défini, sinon un gradient neutre */}
        <div className="h-1 w-20 mt-2 rounded-full bg-gradient-to-r from-neutral-300 to-neutral-200" />
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {/* Lead plus mis en avant */}
        <div className="md:col-span-2">
          <ArticleCard {...lead} className="border-2 border-neutral-100" />
        </div>

        {/* Secondaires */}
        {rest.slice(0, 6).map((b, i) => (
          <ArticleCard key={i} {...b} />
        ))}
      </div>
    </section>
  );
}