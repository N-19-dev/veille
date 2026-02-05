// src/App.tsx
import React from "react";
import SectionCard from "./components/SectionCard";
import CategoryFilter from "./components/CategoryFilter";
import Top3 from "./components/Top3";
import TopVideos from "./components/TopVideos";
import FeedView from "./components/FeedView";
import MySpace from "./components/MySpace";
import AuthButton from "./components/AuthButton";
import LoginModal from "./components/LoginModal";
import CommentsModal from "./components/CommentsModal";
import { useAuth } from "./lib/AuthContext";
import {
  loadWeeksIndex,
  loadLatestWeek,
  loadWeekSummary,
  loadFeed,
  type WeekMeta,
  type TopItem,
  type VideoItem,
  type SummarySection,
  type Feed,
} from "./lib/parse";

// Type pour les données de la semaine
type WeekData = {
  overview: string;
  top3: TopItem[];
  topVideos: VideoItem[];
  sections: SummarySection[];
};

type ViewMode = "feed" | "videos" | "week" | "myspace";

export default function App() {
  const { user, isLoginModalOpen, closeLoginModal } = useAuth();

  // Mode de vue: feed continu ou semaine
  const [viewMode, setViewMode] = React.useState<ViewMode>("feed");

  // États pour le mode semaine
  const [weeks, setWeeks] = React.useState<WeekMeta[]>([]);
  const [currentWeek, setCurrentWeek] = React.useState<WeekMeta | null>(null);
  const [weekData, setWeekData] = React.useState<WeekData | null>(null);

  // États pour le mode feed
  const [feedData, setFeedData] = React.useState<Feed | null>(null);

  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  // États pour les filtres (mode semaine)
  const [selectedCategory, setSelectedCategory] = React.useState<string | null>(null);
  const [showFullSelection, setShowFullSelection] = React.useState(false);

  // Chargement initial
  React.useEffect(() => {
    (async () => {
      try {
        // Charger le feed
        const feed = await loadFeed();
        setFeedData(feed);

        // Charger les semaines pour le mode archive
        const ws = await loadWeeksIndex();
        setWeeks(ws);
        const latest = ws[0] || (await loadLatestWeek());
        setCurrentWeek(latest);

        // Pre-load week data
        const wData = await loadWeekSummary(latest);
        setWeekData(wData);
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
      setSelectedCategory(null);
      setShowFullSelection(false);
      const w = weeks.find((x) => x.week === weekId);
      if (!w) throw new Error("Semaine inconnue");
      setCurrentWeek(w);
      const wData = await loadWeekSummary(w);
      setWeekData(wData);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  };

  // Filtrer les sections en fonction des filtres
  const filteredSections = React.useMemo(() => {
    if (!weekData) return [];
    let sections = weekData.sections;
    if (selectedCategory) {
      sections = sections.filter((sec) => sec.title === selectedCategory);
    }
    return sections;
  }, [weekData, selectedCategory]);

  // Extraire les catégories uniques
  const categories = React.useMemo(() => {
    if (!weekData) return [];
    return weekData.sections.map((sec) => sec.title);
  }, [weekData]);

  // Compter le nombre total d'articles
  const totalArticles = React.useMemo(() => {
    if (!weekData) return 0;
    return weekData.sections.reduce((acc, sec) => acc + (sec.items?.length || 0), 0);
  }, [weekData]);

  if (error) return <div className="p-6 text-red-600">{error}</div>;
  if (loading) return <div className="p-6">Chargement…</div>;

  return (
    <div className="min-h-screen bg-neutral-50">
      {/* Header simplifié */}
      <header className="bg-white border-b border-neutral-200">
        <div className="max-w-6xl mx-auto px-3 sm:px-4 py-3 sm:py-4">
          {/* Mobile: stacked layout, Desktop: horizontal */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            {/* Top row: Logo + Auth */}
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-lg sm:text-xl font-bold text-neutral-900">Veille Tech</h1>
                <p className="text-xs sm:text-sm text-neutral-500">Data Engineering</p>
              </div>
              {/* Auth button visible on mobile in top row */}
              <div className="sm:hidden">
                <AuthButton />
              </div>
            </div>

            {/* Mode toggle + Auth (desktop) */}
            <div className="flex items-center justify-center sm:justify-end gap-3 sm:gap-4">
              <div className="flex bg-neutral-100 rounded-lg p-1 w-full sm:w-auto">
                <button
                  onClick={() => setViewMode("feed")}
                  className={`flex-1 sm:flex-none px-3 sm:px-4 py-2 text-xs sm:text-sm font-medium rounded-md transition-colors ${
                    viewMode === "feed"
                      ? "bg-white text-neutral-900 shadow-sm"
                      : "text-neutral-600 hover:text-neutral-900"
                  }`}
                >
                  Feed
                </button>
                <button
                  onClick={() => setViewMode("videos")}
                  className={`flex-1 sm:flex-none px-3 sm:px-4 py-2 text-xs sm:text-sm font-medium rounded-md transition-colors ${
                    viewMode === "videos"
                      ? "bg-white text-neutral-900 shadow-sm"
                      : "text-neutral-600 hover:text-neutral-900"
                  }`}
                >
                  Vidéos
                </button>
                <button
                  onClick={() => setViewMode("week")}
                  className={`flex-1 sm:flex-none px-3 sm:px-4 py-2 text-xs sm:text-sm font-medium rounded-md transition-colors ${
                    viewMode === "week"
                      ? "bg-white text-neutral-900 shadow-sm"
                      : "text-neutral-600 hover:text-neutral-900"
                  }`}
                >
                  Archives
                </button>
                {user && (
                  <button
                    onClick={() => setViewMode("myspace")}
                    className={`flex-1 sm:flex-none px-3 sm:px-4 py-2 text-xs sm:text-sm font-medium rounded-md transition-colors ${
                      viewMode === "myspace"
                        ? "bg-white text-neutral-900 shadow-sm"
                        : "text-neutral-600 hover:text-neutral-900"
                    }`}
                  >
                    ⭐
                  </button>
                )}
              </div>

              {/* Auth button hidden on mobile (shown in top row instead) */}
              <div className="hidden sm:block">
                <AuthButton />
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-3 sm:px-4 py-4 sm:py-8">
        {/* Mode Feed (articles uniquement) */}
        {viewMode === "feed" && feedData && (
          <FeedView
            articles={feedData.articles}
            videos={[]}
            generatedAt={feedData.generated_at}
          />
        )}

        {/* Mode Vidéos */}
        {viewMode === "videos" && feedData && (
          <div className="space-y-6">
            <div className="text-center text-sm text-neutral-500">
              Vidéos & Podcasts récents
            </div>
            <FeedView
              articles={[]}
              videos={feedData.videos}
              generatedAt={feedData.generated_at}
            />
          </div>
        )}

        {/* Mode Mon espace */}
        {viewMode === "myspace" && (
          <MySpace />
        )}

        {/* Mode Semaine (Archives) */}
        {viewMode === "week" && currentWeek && weekData && (
          <div className="space-y-6">
            {/* Week selector */}
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-neutral-900">
                Semaine {currentWeek.week}
              </h2>
              <select
                value={currentWeek.week}
                onChange={(e) => onWeekChange(e.target.value)}
                className="px-3 py-2 border border-neutral-300 rounded-lg text-sm"
              >
                {weeks.map((w) => (
                  <option key={w.week} value={w.week}>
                    {w.week} {w.range ? `(${w.range})` : ""}
                  </option>
                ))}
              </select>
            </div>

            {/* Top 3 */}
            <Top3 items={weekData.top3} weekLabel={currentWeek.week} />

            {/* Top Vidéos */}
            <TopVideos items={weekData.topVideos} />

            {/* Toggle sélection complète */}
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

            {/* Sélection complète */}
            {showFullSelection && (
              <>
                <CategoryFilter
                  categories={categories}
                  selectedCategory={selectedCategory}
                  onCategoryChange={setSelectedCategory}
                />

                {selectedCategory && filteredSections.length === 0 && (
                  <div className="text-center py-8">
                    <p className="text-neutral-500">Aucun article trouvé pour ce filtre.</p>
                  </div>
                )}

                <div className="grid grid-cols-1 gap-4">
                  {filteredSections.map((sec) =>
                    sec.items?.length ? (
                      <SectionCard
                        key={sec.title}
                        title={sec.title}
                        weekLabel={currentWeek.week}
                        category={sec.title}
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
          </div>
        )}
      </main>

      {/* Modals */}
      <LoginModal isOpen={isLoginModalOpen} onClose={closeLoginModal} />
      <CommentsModal />
    </div>
  );
}
