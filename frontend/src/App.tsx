// src/App.tsx
import React from "react";
import Hero from "./components/Hero";
import Top3 from "./components/Top3";
import SectionCard from "./components/SectionCard";
import Overview from "./components/Overview";
import SearchBar from "./components/SearchBar";
import CategoryFilter from "./components/CategoryFilter";
import { loadWeeksIndex, loadLatestWeek, loadWeekSummary, type WeekMeta } from "./lib/parse";
import { createSearchIndex, searchArticles, type SearchableArticle } from "./lib/search";

export default function App() {
  const [weeks, setWeeks] = React.useState<WeekMeta[]>([]);
  const [currentWeek, setCurrentWeek] = React.useState<WeekMeta | null>(null);
  const [data, setData] = React.useState<{ overview: string; top3: any[]; sections: any[] } | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  // États pour la recherche et les filtres
  const [searchQuery, setSearchQuery] = React.useState("");
  const [selectedCategory, setSelectedCategory] = React.useState<string | null>(null);
  const [searchIndex, setSearchIndex] = React.useState<any>(null);

  React.useEffect(() => {
    (async () => {
      try {
        const ws = await loadWeeksIndex();
        setWeeks(ws);
        const latest = ws[0] || (await loadLatestWeek());
        setCurrentWeek(latest);
        const weekData = await loadWeekSummary(latest);
        setData(weekData);

        // Créer l'index de recherche
        const allArticles: SearchableArticle[] = [];
        weekData.sections.forEach((section: any) => {
          section.items?.forEach((item: any) => {
            allArticles.push({
              title: item.title,
              url: item.url,
              source: item.source,
              score: item.score,
              category: section.title,
            });
          });
        });
        setSearchIndex(createSearchIndex(allArticles));
      } catch (e: any) {
        setError(e.message ?? String(e));
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const onWeekChange = async (weekId: string) => {
    try {
      setLoading(true);
      setSearchQuery("");  // Reset search
      setSelectedCategory(null);  // Reset filter
      const w = weeks.find((x) => x.week === weekId);
      if (!w) throw new Error("Semaine inconnue");
      setCurrentWeek(w);
      const weekData = await loadWeekSummary(w);
      setData(weekData);

      // Recréer l'index de recherche
      const allArticles: SearchableArticle[] = [];
      weekData.sections.forEach((section: any) => {
        section.items?.forEach((item: any) => {
          allArticles.push({
            title: item.title,
            url: item.url,
            source: item.source,
            score: item.score,
            category: section.title,
          });
        });
      });
      setSearchIndex(createSearchIndex(allArticles));
    } catch (e: any) {
      setError(e.message ?? String(e));
    } finally {
      setLoading(false);
    }
  };

  // Filtrer les sections en fonction de la recherche et des filtres
  const filteredSections = React.useMemo(() => {
    if (!data) return [];

    let sections = data.sections;

    // Appliquer le filtre de catégorie
    if (selectedCategory) {
      sections = sections.filter((sec: any) => sec.title === selectedCategory);
    }

    // Appliquer la recherche
    if (searchQuery && searchIndex) {
      const searchResults = searchArticles(searchIndex, searchQuery);
      const searchUrls = new Set(searchResults.map((r) => r.url));

      sections = sections
        .map((sec: any) => ({
          ...sec,
          items: sec.items?.filter((item: any) => searchUrls.has(item.url)) || [],
        }))
        .filter((sec: any) => sec.items.length > 0);
    }

    return sections;
  }, [data, selectedCategory, searchQuery, searchIndex]);

  // Extraire les catégories uniques
  const categories = React.useMemo(() => {
    if (!data) return [];
    return data.sections.map((sec: any) => sec.title);
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
      <main className="max-w-6xl mx-auto px-4 py-8 space-y-8">
        <Overview content={data.overview} />

        {/* Barre de recherche et filtres */}
        <div className="space-y-4">
          <SearchBar
            searchQuery={searchQuery}
            onSearchChange={setSearchQuery}
          />
          <CategoryFilter
            categories={categories}
            selectedCategory={selectedCategory}
            onCategoryChange={setSelectedCategory}
          />
        </div>

        {/* Message si aucun résultat */}
        {(searchQuery || selectedCategory) && filteredSections.length === 0 && (
          <div className="text-center py-12">
            <p className="text-neutral-500 text-lg">
              Aucun article trouvé pour cette recherche ou filtre.
            </p>
          </div>
        )}

        <Top3 items={data.top3} />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {filteredSections.map((sec: any) =>
            sec.items?.length ? (
              <SectionCard
                key={sec.title}
                title={sec.title}
                bullets={sec.items.map((it: any) => ({
                  title: it.title,
                  url: it.url,
                  source: it.source,
                  score: it.score,
                }))}
              />
            ) : null
          )}
        </div>
      </main>
    </div>
  );
}