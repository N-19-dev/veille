// src/lib/SavedArticlesContext.tsx
/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { db } from "./firebase";
import { collection, query, where, onSnapshot, addDoc, deleteDoc, doc, serverTimestamp } from "firebase/firestore";
import { useAuth } from "./AuthContext";
import type { SavedArticle } from "./types";

type SavedArticlesContextType = {
  savedArticles: SavedArticle[];
  savedUrls: Set<string>;
  isSaved: (url: string) => boolean;
  saveArticle: (article: { url: string; title: string; source_name: string }) => Promise<void>;
  unsaveArticle: (url: string) => Promise<void>;
  toggleSave: (article: { url: string; title: string; source_name: string }) => Promise<void>;
};

const SavedArticlesContext = createContext<SavedArticlesContextType | null>(null);

export function SavedArticlesProvider({ children }: { children: ReactNode }) {
  const { user } = useAuth();
  const [savedArticles, setSavedArticles] = useState<SavedArticle[]>([]);
  const [savedUrls, setSavedUrls] = useState<Set<string>>(new Set());

  // Load saved articles from Firebase
  useEffect(() => {
    if (!user) {
      setSavedArticles([]);
      setSavedUrls(new Set());
      return;
    }

    const q = query(
      collection(db, "saved_articles"),
      where("user_id", "==", user.uid)
    );

    const unsubscribe = onSnapshot(q, (snapshot) => {
      const saved: SavedArticle[] = [];
      const urls = new Set<string>();
      snapshot.forEach((docSnap) => {
        const data = docSnap.data();
        saved.push({
          id: docSnap.id,
          url: data.url,
          title: data.title,
          source_name: data.source_name,
          saved_at: data.saved_at?.toDate() || new Date(),
        });
        urls.add(data.url);
      });
      // Sort by most recently saved
      saved.sort((a, b) => b.saved_at.getTime() - a.saved_at.getTime());
      setSavedArticles(saved);
      setSavedUrls(urls);
    });

    return () => unsubscribe();
  }, [user]);

  const isSaved = (url: string) => savedUrls.has(url);

  const saveArticle = async (article: { url: string; title: string; source_name: string }) => {
    if (!user) return;
    try {
      await addDoc(collection(db, "saved_articles"), {
        user_id: user.uid,
        url: article.url,
        title: article.title,
        source_name: article.source_name,
        saved_at: serverTimestamp(),
      });
    } catch (err) {
      console.error("Error saving article:", err);
    }
  };

  const unsaveArticle = async (url: string) => {
    if (!user) return;
    const saved = savedArticles.find((a) => a.url === url);
    if (!saved) return;
    try {
      await deleteDoc(doc(db, "saved_articles", saved.id));
    } catch (err) {
      console.error("Error unsaving article:", err);
    }
  };

  const toggleSave = async (article: { url: string; title: string; source_name: string }) => {
    if (isSaved(article.url)) {
      await unsaveArticle(article.url);
    } else {
      await saveArticle(article);
    }
  };

  return (
    <SavedArticlesContext.Provider value={{ savedArticles, savedUrls, isSaved, saveArticle, unsaveArticle, toggleSave }}>
      {children}
    </SavedArticlesContext.Provider>
  );
}

export function useSavedArticles() {
  const context = useContext(SavedArticlesContext);
  if (!context) {
    throw new Error("useSavedArticles must be used within a SavedArticlesProvider");
  }
  return context;
}
