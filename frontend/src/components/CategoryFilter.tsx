// src/components/CategoryFilter.tsx
import React from "react";

interface CategoryFilterProps {
  categories: string[];
  selectedCategory: string | null;
  onCategoryChange: (category: string | null) => void;
}

export default function CategoryFilter({
  categories,
  selectedCategory,
  onCategoryChange,
}: CategoryFilterProps) {
  return (
    <div className="flex flex-wrap gap-2">
      <button
        onClick={() => onCategoryChange(null)}
        className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
          selectedCategory === null
            ? "bg-indigo-600 text-white"
            : "bg-neutral-100 text-neutral-700 hover:bg-neutral-200"
        }`}
      >
        Toutes
      </button>
      {categories.map((cat) => (
        <button
          key={cat}
          onClick={() => onCategoryChange(cat)}
          className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
            selectedCategory === cat
              ? "bg-indigo-600 text-white"
              : "bg-neutral-100 text-neutral-700 hover:bg-neutral-200"
          }`}
        >
          {cat}
        </button>
      ))}
    </div>
  );
}
