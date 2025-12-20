// src/components/ArticleCard.tsx
// Carte article compacte : favicon, source, titre clamp, barre d'accent.
// Compatible top3/sections: {title,url,source,date,score,tech_level,marketing_score}

import React from "react";
import { faviconUrl, getDomain } from "../lib/parse";

type TechLevel = 'beginner' | 'intermediate' | 'advanced';

type Props = {
  title: string;
  url?: string;
  source?: string;
  date?: string;
  score?: number | string;
  tech_level?: TechLevel;
  marketing_score?: number;
  className?: string;
};

export default function ArticleCard({
  title,
  url,
  source,
  date,
  className = "",
}: Props) {
  const dom = getDomain(url ?? "");
  const displaySource = (source || dom || "Source").trim();

  // Si pas d'URL, on rend un <div> non cliquable
  const Clickable: React.ElementType = url ? "a" : "div";
  const clickableProps = url
    ? {
        href: url,
        target: "_blank",
        rel: "noreferrer",
      }
    : {};

  return (
    <Clickable
      {...clickableProps}
      className={[
        "group block rounded-2xl border bg-white p-4 transition-all",
        url
          ? "hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-neutral-300"
          : "opacity-90",
        className,
      ].join(" ")}
      aria-label={title}
    >
      <div className="mb-3 flex items-center gap-2">
        {/* Favicon avec fallback silencieux */}
        <img
          src={faviconUrl(url ?? "", 64)}
          alt=""
          className="h-5 w-5 rounded-sm border object-contain"
          loading="lazy"
          onError={(e) => {
            (e.currentTarget as HTMLImageElement).style.display = "none";
          }}
        />
        <span className="text-[11px] font-semibold uppercase tracking-widest text-neutral-600">
          {displaySource}
        </span>
        {date && <span className="text-[11px] text-neutral-400">· {date}</span>}
      </div>

      {/* Barre d’accent “magazine” (remplace bg-accent par un gradient par défaut) */}
      <div className="mb-3 h-1 w-12 rounded-full bg-gradient-to-r from-neutral-300 to-neutral-200 group-hover:from-neutral-400 group-hover:to-neutral-200" />

      <h4 className="line-clamp-3 font-semibold leading-snug group-hover:underline">
        {title}
      </h4>
    </Clickable>
  );
}