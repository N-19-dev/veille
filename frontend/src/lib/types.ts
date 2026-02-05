// src/lib/types.ts
// Shared types across the application

export type SavedArticle = {
  id: string;
  url: string;
  title: string;
  source_name: string;
  saved_at: Date;
};
