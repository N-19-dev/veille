// src/components/FeedView.tsx
import { type FeedItem, faviconUrl, formatRelativeDate } from "../lib/parse";
import VoteButton from "./VoteButton";
import CommentsCount from "./CommentsCount";
import TopCommentPreview from "./TopCommentPreview";
import { useComments } from "../lib/CommentsContext";

type FeedViewProps = {
  articles: FeedItem[];
  videos: FeedItem[];
  generatedAt: string;
};

// Helper function to generate article ID (matches backend hash)
function generateArticleId(url: string, title: string): string {
  const str = `${url}${title}`;
  return btoa(unescape(encodeURIComponent(str))).slice(0, 40);
}

// Get current week label (format: 2026w05)
function getCurrentWeekLabel(): string {
  const now = new Date();
  const startOfYear = new Date(now.getFullYear(), 0, 1);
  const days = Math.floor((now.getTime() - startOfYear.getTime()) / 86400000);
  const weekNumber = Math.ceil((days + startOfYear.getDay() + 1) / 7);
  return `${now.getFullYear()}w${weekNumber.toString().padStart(2, '0')}`;
}

function FeedCard({ item }: { item: FeedItem }) {
  const { openCommentsModal } = useComments();
  const icon = item.source_type === "youtube" ? "▶️" : item.source_type === "podcast" ? "🎙️" : null;
  const articleId = generateArticleId(item.url, item.title);
  const weekLabel = getCurrentWeekLabel();

  return (
    <div className="bg-white rounded-xl border border-neutral-200 p-4 hover:border-neutral-300 hover:shadow-sm transition-all">
      {/* Main content - clickable */}
      <a
        href={item.url}
        target="_blank"
        rel="noopener noreferrer"
        className="block"
      >
        <div className="flex gap-3">
          {/* Favicon */}
          <img
            src={faviconUrl(item.url, 32)}
            alt=""
            className="w-8 h-8 rounded-md flex-shrink-0 mt-0.5"
            loading="lazy"
          />

          <div className="flex-1 min-w-0">
            {/* Title */}
            <h3 className="font-medium text-neutral-900 leading-snug line-clamp-2 group-hover:underline">
              {icon && <span className="mr-1">{icon}</span>}
              {item.title}
            </h3>

            {/* Meta */}
            <div className="flex items-center gap-2 mt-1.5 text-sm text-neutral-500">
              <span className="truncate">{item.source_name}</span>
              <span>·</span>
              <span className="flex-shrink-0">{formatRelativeDate(item.published_ts)}</span>
            </div>

            {/* Summary (if exists) */}
            {item.summary && (
              <p className="mt-2 text-sm text-neutral-600 line-clamp-2">
                {item.summary}
              </p>
            )}
          </div>
        </div>
      </a>

      {/* Vote and Comments */}
      <div className="mt-3 pt-3 border-t flex items-center justify-between gap-4">
        {/* Votes - left */}
        <div className="flex-shrink-0">
          <VoteButton
            articleId={articleId}
            articleUrl={item.url}
            weekLabel={weekLabel}
            source={item.source_name}
            category={item.category_key}
          />
        </div>

        {/* Comments section - right */}
        <div className="flex items-center gap-3 overflow-hidden">
          {/* Top comment preview - hidden on small screens */}
          <div className="hidden md:block truncate max-w-[180px]">
            <TopCommentPreview
              articleId={articleId}
              articleUrl={item.url}
              articleTitle={item.title}
              weekLabel={weekLabel}
              category={item.category_key || 'unknown'}
              source={item.source_name}
            />
          </div>

          <button
            onClick={() => {
              openCommentsModal(
                articleId,
                item.url,
                item.title,
                weekLabel,
                item.category_key || 'unknown',
                item.source_name
              );
            }}
            className="flex-shrink-0 flex items-center gap-1.5 text-sm text-gray-400 hover:text-gray-600 transition"
          >
            <CommentsCount articleId={articleId} weekLabel={weekLabel} />
            <span>comments</span>
          </button>
        </div>
      </div>
    </div>
  );
}

function FeedSection({
  title,
  items,
  emptyMessage
}: {
  title: string;
  items: FeedItem[];
  emptyMessage: string;
}) {
  return (
    <section>
      <h2 className="text-lg font-semibold text-neutral-900 mb-4">{title}</h2>
      {items.length > 0 ? (
        <div className="space-y-3">
          {items.map((item) => (
            <FeedCard key={item.id} item={item} />
          ))}
        </div>
      ) : (
        <p className="text-neutral-500 text-sm py-8 text-center">{emptyMessage}</p>
      )}
    </section>
  );
}

export default function FeedView({ articles, videos, generatedAt }: FeedViewProps) {
  const generatedDate = new Date(generatedAt);
  const formattedDate = generatedDate.toLocaleDateString("fr-FR", {
    day: "numeric",
    month: "long",
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <div className="space-y-8">
      {/* Header info */}
      <div className="text-center text-sm text-neutral-500">
        Mis à jour : {formattedDate}
      </div>

      {/* Articles feed */}
      <FeedSection
        title={`📰 Articles (${articles.length})`}
        items={articles}
        emptyMessage="Aucun article pour le moment"
      />

      {/* Videos/Podcasts feed */}
      <FeedSection
        title={`🎬 Vidéos & Podcasts (${videos.length})`}
        items={videos}
        emptyMessage="Aucune vidéo ou podcast pour le moment"
      />
    </div>
  );
}
