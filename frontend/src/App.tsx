// src/App.tsx
import React from "react";
import Hero from "./components/Hero";
import SectionCard from "./components/SectionCard";
import CategoryFilter from "./components/CategoryFilter";
import Top3 from "./components/Top3";
import { loadWeeksIndex, loadLatestWeek, loadWeekSummary, type WeekMeta, type TopItem, type SummarySection } from "./lib/parse";

// Type pour les données de la semaine
type WeekData = {
  overview: string;
  top3: TopItem[];
  sections: SummarySection[];
};

export default function App() {
  const [weeks, setWeeks] = React.useState<WeekMeta[]>([]);
  const [currentWeek, setCurrentWeek] = React.useState<WeekMeta | null>(null);
  const [data, setData] = React.useState<WeekData | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  // États pour les filtres
  const [selectedCategory, setSelectedCategory] = React.useState<string | null>(null);
  const [showFullSelection, setShowFullSelection] = React.useState(false);

  React.useEffect(() => {
    (async () => {
      try {
        const ws = await loadWeeksIndex();
        setWeeks(ws);
        const latest = ws[0] || (await loadLatestWeek());
        setCurrentWeek(latest);
        const weekData = await loadWeekSummary(latest);
        setData(weekData);
      } catch (e) {
        setError(e instanceof Error ? e.message : String(e));
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const onWeekChange = async (weekId: string) => {
    try {
      setLoading(true);
      setSelectedCategory(null);  // Reset filter
      setShowFullSelection(false);  // Reset to Top 3 view
      const w = weeks.find((x) => x.week === weekId);
      if (!w) throw new Error("Semaine inconnue");
      setCurrentWeek(w);
      const weekData = await loadWeekSummary(w);
      setData(weekData);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  };

  // Filtrer les sections en fonction des filtres
  const filteredSections = React.useMemo(() => {
    if (!data) return [];

    let sections = data.sections;

    // Appliquer le filtre de catégorie
    if (selectedCategory) {
      sections = sections.filter((sec) => sec.title === selectedCategory);
    }

    return sections;
  }, [data, selectedCategory]);

  // Extraire les catégories uniques
  const categories = React.useMemo(() => {
    if (!data) return [];
    return data.sections.map((sec) => sec.title);
  }, [data]);

  // Compter le nombre total d'articles
  const totalArticles = React.useMemo(() => {
    if (!data) return 0;
    return data.sections.reduce((acc, sec) => acc + (sec.items?.length || 0), 0);
  }, [data]);

  if (error) return <div className="p-6 text-red-600">{error}</div>;
  if (loading || !currentWeek || !data) return <div className="p-6">Chargement…</div>;

  return (
    <div className="min-h-screen bg-neutral-50">
      <Hero
        weekLabel={currentWeek.week}
        dateRange={currentWeek.range}
        weeks={weeks.map(w => w.week)}
        onWeekChange={onWeekChange}
      />
      <main className="max-w-6xl mx-auto px-4 py-4 sm:py-6 md:py-8 space-y-4 sm:space-y-6 md:space-y-8">
        {/* Top 3 - Toujours visible */}
        <Top3 items={data.top3} />

        {/* Bouton toggle pour voir toute la sélection */}
        <div className="text-center">
          <button
            onClick={() => setShowFullSelection(!showFullSelection)}
            className="inline-flex items-center gap-2 px-6 py-3 rounded-full border border-neutral-300 bg-white hover:bg-neutral-50 hover:border-neutral-400 transition-colors text-sm font-medium"
          >
            {showFullSelection ? (
              <>
                <span>Masquer la sélection complète</span>
                <span>▲</span>
              </>
            ) : (
              <>
                <span>Voir toute la sélection ({totalArticles} articles)</span>
                <span>▼</span>
              </>
            )}
          </button>
        </div>

        {/* Sélection complète - Affichée uniquement si toggle activé */}
        {showFullSelection && (
          <>
            {/* Filtres */}
            <CategoryFilter
              categories={categories}
              selectedCategory={selectedCategory}
              onCategoryChange={setSelectedCategory}
            />

            {/* Message si aucun résultat */}
            {selectedCategory && filteredSections.length === 0 && (
              <div className="text-center py-8 sm:py-12">
                <p className="text-neutral-500 text-base sm:text-lg">
                  Aucun article trouvé pour ce filtre.
                </p>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
              {filteredSections.map((sec) =>
                sec.items?.length ? (
                  <SectionCard
                    key={sec.title}
                    title={sec.title}
                    bullets={sec.items.map((it) => ({
                      title: it.title,
                      url: it.url,
                      source: it.source,
                      score: it.score,
                      tech_level: it.tech_level,
                      marketing_score: it.marketing_score,
                    }))}
                  />
                ) : null
              )}
            </div>
          </>
        )}
      </main>
    </div>
  );
}