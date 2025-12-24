// src/App.tsx
import React from "react";
import Hero from "./components/Hero";
import SectionCard from "./components/SectionCard";
import Overview from "./components/Overview";
import SearchBar from "./components/SearchBar";
import CategoryFilter from "./components/CategoryFilter";
import ContentTypeTabs, { type ContentType } from "./components/ContentTypeTabs";
import { loadWeeksIndex, loadLatestWeek, loadWeekSummary, type WeekMeta, type TopItem, type SummarySection } from "./lib/parse";
import { createSearchIndex, searchArticles, type SearchableArticle } from "./lib/search";
import type Fuse from "fuse.js";

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

  // États pour la recherche et les filtres
  const [searchQuery, setSearchQuery] = React.useState("");
  const [selectedCategory, setSelectedCategory] = React.useState<string | null>(null);
  const [searchIndex, setSearchIndex] = React.useState<Fuse<SearchableArticle> | null>(null);
  const [activeContentType, setActiveContentType] = React.useState<ContentType>("all");

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
        weekData.sections.forEach((section) => {
          section.items?.forEach((item) => {
            allArticles.push({
              title: item.title,
              url: item.url,
              source: item.source || "",
              score: typeof item.score === "number" ? item.score : 0,
              category: section.title,
            });
          });
        });
        setSearchIndex(createSearchIndex(allArticles));
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
      setSearchQuery("");  // Reset search
      setSelectedCategory(null);  // Reset filter
      setActiveContentType("all");  // Reset content type
      const w = weeks.find((x) => x.week === weekId);
      if (!w) throw new Error("Semaine inconnue");
      setCurrentWeek(w);
      const weekData = await loadWeekSummary(w);
      setData(weekData);

      // Recréer l'index de recherche
      const allArticles: SearchableArticle[] = [];
      weekData.sections.forEach((section) => {
        section.items?.forEach((item) => {
          allArticles.push({
            title: item.title,
            url: item.url,
            source: item.source || "",
            score: typeof item.score === "number" ? item.score : 0,
            category: section.title,
          });
        });
      });
      setSearchIndex(createSearchIndex(allArticles));
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  };

  // Filtrer les sections en fonction de la recherche, des filtres et du type de contenu
  const filteredSections = React.useMemo(() => {
    if (!data) return [];

    let sections = data.sections;

    // Appliquer le filtre de type de contenu (technical vs rex)
    if (activeContentType !== "all") {
      sections = sections
        .map((sec) => ({
          ...sec,
          items: sec.items?.filter((item) =>
            (item.content_type || "technical") === activeContentType
          ) || [],
        }))
        .filter((sec) => sec.items.length > 0);
    }

    // Appliquer le filtre de catégorie
    if (selectedCategory) {
      sections = sections.filter((sec) => sec.title === selectedCategory);
    }

    // Appliquer la recherche
    if (searchQuery && searchIndex) {
      const searchResults = searchArticles(searchIndex, searchQuery);
      const searchUrls = new Set(searchResults.map((r) => r.url));

      sections = sections
        .map((sec) => ({
          ...sec,
          items: sec.items?.filter((item) => searchUrls.has(item.url)) || [],
        }))
        .filter((sec) => sec.items.length > 0);
    }

    return sections;
  }, [data, selectedCategory, searchQuery, searchIndex, activeContentType]);

  // Extraire les catégories uniques
  const categories = React.useMemo(() => {
    if (!data) return [];
    return data.sections.map((sec) => sec.title);
  }, [data]);

  // Compter les articles par type de contenu
  const contentTypeCounts = React.useMemo(() => {
    if (!data) return { technical: 0, rex: 0 };

    let technicalCount = 0;
    let rexCount = 0;

    data.sections.forEach((sec) => {
      sec.items?.forEach((item) => {
        const contentType = item.content_type || "technical";
        if (contentType === "rex") {
          rexCount++;
        } else {
          technicalCount++;
        }
      });
    });

    return { technical: technicalCount, rex: rexCount };
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
        <Overview content={data.overview} />

        {/* Onglets de type de contenu */}
        <ContentTypeTabs
          activeTab={activeContentType}
          onTabChange={setActiveContentType}
          technicalCount={contentTypeCounts.technical}
          rexCount={contentTypeCounts.rex}
        />

        {/* Barre de recherche et filtres */}
        <div className="space-y-3 sm:space-y-4">
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
          <div className="text-center py-8 sm:py-12">
            <p className="text-neutral-500 text-base sm:text-lg">
              Aucun article trouvé pour cette recherche ou filtre.
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
      </main>
    </div>
  );
}