// src/components/MySpace.tsx
import { useState, useEffect, useMemo } from "react";
import { useAuth } from "../lib/AuthContext";
import { useSavedArticles, type SavedArticle } from "../lib/SavedArticlesContext";
import { faviconUrl } from "../lib/parse";

type SearchArticle = {
  id: string;
  url: string;
  title: string;
  source_name: string;
  published_ts: number;
  category_key: string;
  week: string;
};

// Raw search index item (abbreviated keys to reduce file size)
type RawSearchItem = {
  id: string;
  t: string;   // title
  u: string;   // url
  s: string;   // source_name
  d: number;   // published_ts
  c: string;   // category_key
};

// Load search index
async function loadSearchIndex(): Promise<SearchArticle[]> {
  try {
    const base = typeof document !== "undefined" ? document.baseURI : "/";
    const url = new URL("export/search.json", base).toString();
    const res = await fetch(url, { cache: "no-store" });
    if (!res.ok) return [];
    const raw: RawSearchItem[] = await res.json();
    // Map abbreviated keys to full keys
    return raw.map((item) => ({
      id: item.id,
      title: item.t,
      url: item.u,
      source_name: item.s,
      published_ts: item.d,
      category_key: item.c,
      week: "",
    }));
  } catch {
    return [];
  }
}

// Format relative date
function formatDate(timestamp: number): string {
  const date = new Date(timestamp * 1000);
  return date.toLocaleDateString("fr-FR", { day: "numeric", month: "short", year: "numeric" });
}

export default function MySpace() {
  const { user } = useAuth();
  const { savedArticles, savedUrls, toggleSave, unsaveArticle } = useSavedArticles();
  const [searchQuery, setSearchQuery] = useState("");
  const [allArticles, setAllArticles] = useState<SearchArticle[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"search" | "saved">("search");

  // Load search index on mount
  useEffect(() => {
    loadSearchIndex().then((articles) => {
      // Sort by most recent first
      articles.sort((a, b) => b.published_ts - a.published_ts);
      setAllArticles(articles);
      setIsLoading(false);
    });
  }, []);

  // Filter articles based on search query
  const searchResults = useMemo(() => {
    if (!searchQuery.trim()) return [];
    const q = searchQuery.toLowerCase();
    return allArticles
      .filter((a) =>
        (a.title || "").toLowerCase().includes(q) ||
        (a.source_name || "").toLowerCase().includes(q)
      )
      .slice(0, 50); // Limit to 50 results
  }, [searchQuery, allArticles]);

  if (!user) {
    return (
      <div className="text-center py-12">
        <p className="text-neutral-500">Connecte-toi pour accéder à ton espace personnel.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-neutral-900">Mon espace</h1>
        <p className="text-sm text-neutral-500 mt-1">
          Recherche et sauvegarde des articles
        </p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-neutral-200">
        <button
          onClick={() => setActiveTab("search")}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition ${
            activeTab === "search"
              ? "border-blue-600 text-blue-600"
              : "border-transparent text-neutral-500 hover:text-neutral-900"
          }`}
        >
          Rechercher
        </button>
        <button
          onClick={() => setActiveTab("saved")}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition ${
            activeTab === "saved"
              ? "border-blue-600 text-blue-600"
              : "border-transparent text-neutral-500 hover:text-neutral-900"
          }`}
        >
          Sauvegardés ({savedArticles.length})
        </button>
      </div>

      {/* Search Tab */}
      {activeTab === "search" && (
        <div className="space-y-4">
          {/* Search input */}
          <div className="relative">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Rechercher un article..."
              className="w-full px-4 py-3 pl-10 border border-neutral-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-neutral-400">
              🔍
            </span>
          </div>

          {/* Results */}
          {isLoading ? (
            <p className="text-center text-neutral-500 py-8">Chargement...</p>
          ) : searchQuery.trim() === "" ? (
            <p className="text-center text-neutral-500 py-8">
              Tape un mot-clé pour rechercher dans {allArticles.length} articles
            </p>
          ) : searchResults.length === 0 ? (
            <p className="text-center text-neutral-500 py-8">Aucun résultat</p>
          ) : (
            <div className="space-y-2">
              {searchResults.map((article) => (
                <ArticleRow
                  key={article.id}
                  article={article}
                  isSaved={savedUrls.has(article.url)}
                  onToggle={() => toggleSave({ url: article.url, title: article.title, source_name: article.source_name })}
                />
              ))}
            </div>
          )}
        </div>
      )}

      {/* Saved Tab */}
      {activeTab === "saved" && (
        <div className="space-y-2">
          {savedArticles.length === 0 ? (
            <p className="text-center text-neutral-500 py-8">
              Aucun article sauvegardé
            </p>
          ) : (
            savedArticles.map((saved) => (
              <SavedArticleRow
                key={saved.id}
                article={saved}
                onUnsave={() => unsaveArticle(saved.url)}
              />
            ))
          )}
        </div>
      )}
    </div>
  );
}

// Article row for search results
function ArticleRow({
  article,
  isSaved,
  onToggle,
}: {
  article: SearchArticle;
  isSaved: boolean;
  onToggle: () => void;
}) {
  return (
    <div className="flex items-center gap-3 p-3 bg-white rounded-lg border border-neutral-200 hover:border-neutral-300 transition">
      <img
        src={faviconUrl(article.url, 24)}
        alt=""
        className="w-6 h-6 rounded flex-shrink-0"
      />
      <a
        href={article.url}
        target="_blank"
        rel="noopener noreferrer"
        className="flex-1 min-w-0"
      >
        <p className="text-sm font-medium text-neutral-900 truncate hover:underline">
          {article.title}
        </p>
        <p className="text-xs text-neutral-500">
          {article.source_name} · {formatDate(article.published_ts)}
        </p>
      </a>
      <button
        onClick={(e) => {
          e.preventDefault();
          onToggle();
        }}
        className={`flex-shrink-0 p-2 rounded transition ${
          isSaved
            ? "text-yellow-500 hover:text-yellow-600"
            : "text-neutral-300 hover:text-yellow-500"
        }`}
        title={isSaved ? "Retirer des favoris" : "Sauvegarder"}
      >
        {isSaved ? "★" : "☆"}
      </button>
    </div>
  );
}

// Saved article row
function SavedArticleRow({
  article,
  onUnsave,
}: {
  article: SavedArticle;
  onUnsave: () => void;
}) {
  return (
    <div className="flex items-center gap-3 p-3 bg-white rounded-lg border border-neutral-200 hover:border-neutral-300 transition">
      <img
        src={faviconUrl(article.url, 24)}
        alt=""
        className="w-6 h-6 rounded flex-shrink-0"
      />
      <a
        href={article.url}
        target="_blank"
        rel="noopener noreferrer"
        className="flex-1 min-w-0"
      >
        <p className="text-sm font-medium text-neutral-900 truncate hover:underline">
          {article.title}
        </p>
        <p className="text-xs text-neutral-500">{article.source_name}</p>
      </a>
      <button
        onClick={(e) => {
          e.preventDefault();
          onUnsave();
        }}
        className="flex-shrink-0 p-2 text-yellow-500 hover:text-yellow-600 rounded transition"
        title="Retirer des favoris"
      >
        ★
      </button>
    </div>
  );
}
