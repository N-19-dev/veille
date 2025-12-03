// src/lib/search.ts
import Fuse from "fuse.js";

export interface SearchableArticle {
  title: string;
  url: string;
  source: string;
  score?: number;
  category?: string;
}

/**
 * Crée une instance Fuse.js pour la recherche floue d'articles.
 */
export function createSearchIndex(articles: SearchableArticle[]) {
  const options = {
    keys: [
      { name: "title", weight: 0.7 },
      { name: "source", weight: 0.3 },
    ],
    threshold: 0.3, // 0 = exact match, 1 = match anything
    includeScore: true,
    minMatchCharLength: 2,
  };

  return new Fuse(articles, options);
}

/**
 * Recherche des articles avec Fuse.js.
 */
export function searchArticles(
  searchIndex: Fuse<SearchableArticle>,
  query: string
): SearchableArticle[] {
  if (!query || query.trim().length < 2) {
    return [];
  }

  const results = searchIndex.search(query);
  return results.map((result) => result.item);
}

/**
 * Filtre les articles par catégorie.
 */
export function filterByCategory(
  articles: SearchableArticle[],
  category: string | null
): SearchableArticle[] {
  if (!category) {
    return articles;
  }

  return articles.filter((article) => article.category === category);
}
