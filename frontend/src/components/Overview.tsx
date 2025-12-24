// src/components/Overview.tsx
import React from "react";
import { marked } from "marked";

export default function Overview({ content }: { content?: string }) {
  const html = React.useMemo(() => {
    if (!content) return "";

    // Configuration du parser Markdown
    marked.setOptions({
      breaks: true,
      gfm: true,
    });
    return marked.parse(content);
  }, [content]);

  if (!content) return null;

  return (
    <section className="bg-white border rounded-2xl p-4 sm:p-6 md:p-8 shadow-sm">
      <div className="mb-4 sm:mb-5">
        <div className="text-xs font-semibold tracking-widest uppercase text-neutral-500">
          Aperçu
        </div>
        <h2 className="text-xl sm:text-2xl md:text-3xl font-bold mt-1 flex items-center gap-2">
          <span className="text-blue-600">🟦</span>
          <span>Aperçu général de la semaine</span>
        </h2>
        <div className="h-1 bg-accent w-16 sm:w-24 mt-2 sm:mt-3 rounded-full" />
      </div>

      <article
        className="prose prose-sm sm:prose-base prose-neutral max-w-none prose-p:leading-relaxed prose-a:text-blue-600 hover:prose-a:text-blue-500 prose-strong:text-neutral-900 prose-li:my-0.5"
        dangerouslySetInnerHTML={{ __html: html }}
      />
    </section>
  );
}