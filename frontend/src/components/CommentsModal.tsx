import { useEffect, useState, useCallback, useMemo } from 'react';
import { collection, query, where, orderBy, onSnapshot } from 'firebase/firestore';
import { db } from '../lib/firebase';
import { useComments } from '../lib/CommentsContext';
import { useAuth } from '../lib/AuthContext';
import type { CommentData } from '../types/comments';
import Comment from './Comment';
import CommentInput from './CommentInput';

type SortOption = 'recent' | 'popular';

export default function CommentsModal() {
  const { isCommentsModalOpen, currentArticle, closeCommentsModal } = useComments();
  const { user } = useAuth();
  const [rawComments, setRawComments] = useState<CommentData[]>([]);
  const [sortBy, setSortBy] = useState<SortOption>('recent');
  const [replyToId, setReplyToId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // Fetch comments for the current article (real-time listener)
  useEffect(() => {
    if (!currentArticle) return;

    setLoading(true);
    const commentsRef = collection(db, 'comments');

    // Filter by article_id AND week_label, order by created_at ascending
    const q = query(
      commentsRef,
      where('article_id', '==', currentArticle.articleId),
      where('week_label', '==', currentArticle.weekLabel),
      orderBy('created_at', 'asc')
    );

    const unsubscribe = onSnapshot(
      q,
      (snapshot) => {
        const commentsData: CommentData[] = [];
        snapshot.forEach((doc) => {
          commentsData.push({ id: doc.id, ...doc.data() } as CommentData);
        });

        console.log(`[CommentsModal] Received ${commentsData.length} comments from Firestore`);
        setRawComments(commentsData);
        setLoading(false);
      },
      (error) => {
        console.error('Error fetching comments:', error);
        setLoading(false);
      }
    );

    return () => unsubscribe();
  }, [currentArticle]);

  // Sort comments based on sortBy option (in memory)
  const comments = useMemo(() => {
    const sorted = [...rawComments];

    if (sortBy === 'recent') {
      sorted.sort((a, b) => b.created_at.toMillis() - a.created_at.toMillis());
    } else if (sortBy === 'popular') {
      sorted.sort((a, b) => b.likes - a.likes);
    }

    return sorted;
  }, [rawComments, sortBy]);

  // Handle escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isCommentsModalOpen) {
        closeCommentsModal();
      }
    };

    if (isCommentsModalOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isCommentsModalOpen, closeCommentsModal]);

  const handleReply = useCallback((parentId: string) => {
    setReplyToId(parentId);
  }, []);

  const handleCommentAdded = useCallback(() => {
    setReplyToId(null);
  }, []);

  if (!isCommentsModalOpen || !currentArticle) return null;

  // Build threaded comment structure
  const topLevelComments = comments.filter((c) => !c.parent_id);
  const commentsByParent = comments.reduce((acc, comment) => {
    if (comment.parent_id) {
      if (!acc[comment.parent_id]) acc[comment.parent_id] = [];
      acc[comment.parent_id].push(comment);
    }
    return acc;
  }, {} as Record<string, CommentData[]>);

  return (
    <div
      className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/50 animate-fade-in"
      onClick={closeCommentsModal}
    >
      <div
        className="relative w-full sm:max-w-3xl max-h-[95vh] sm:max-h-[90vh] bg-white rounded-t-2xl sm:rounded-2xl shadow-2xl animate-scale-in flex flex-col sm:mx-4"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-start justify-between p-4 sm:p-6 border-b border-gray-200">
          <div className="flex-1 pr-4">
            <h2 className="text-lg sm:text-xl font-bold text-gray-900 mb-1 sm:mb-2">💬 Commentaires</h2>
            <p className="text-xs sm:text-sm text-gray-600 line-clamp-2">{currentArticle.articleTitle}</p>
            <div className="flex flex-wrap items-center gap-2 sm:gap-4 mt-2">
              <span className="text-xs text-gray-500">
                {comments.length} commentaire{comments.length !== 1 ? 's' : ''}
              </span>
              {/* Sort options */}
              <div className="flex items-center gap-1 sm:gap-2">
                <button
                  onClick={() => setSortBy('recent')}
                  className={`text-xs px-2 py-1 rounded ${
                    sortBy === 'recent'
                      ? 'bg-blue-100 text-blue-700 font-semibold'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  Récents
                </button>
                <button
                  onClick={() => setSortBy('popular')}
                  className={`text-xs px-2 py-1 rounded ${
                    sortBy === 'popular'
                      ? 'bg-blue-100 text-blue-700 font-semibold'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  Populaires
                </button>
              </div>
            </div>
          </div>
          <button
            onClick={closeCommentsModal}
            className="flex-shrink-0 text-gray-400 hover:text-gray-600 transition"
          >
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Comments List */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4 sm:space-y-6">
          {loading && (
            <div className="text-center py-8 text-gray-500">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
              <p className="mt-2">Chargement des commentaires...</p>
            </div>
          )}

          {!loading && comments.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              <p className="text-lg">Aucun commentaire pour le moment.</p>
              <p className="text-sm mt-2">Soyez le premier à commenter cet article !</p>
            </div>
          )}

          {!loading &&
            topLevelComments.map((comment) => (
              <Comment
                key={comment.id}
                comment={comment}
                replies={commentsByParent[comment.id] || []}
                onReply={handleReply}
                currentUserId={user?.uid}
                depth={0}
              />
            ))}
        </div>

        {/* Comment Input */}
        <div className="border-t border-gray-200 p-4 sm:p-6 bg-gray-50">
          {user ? (
            <CommentInput
              articleId={currentArticle.articleId}
              articleUrl={currentArticle.articleUrl}
              articleTitle={currentArticle.articleTitle}
              weekLabel={currentArticle.weekLabel}
              category={currentArticle.category}
              source={currentArticle.source}
              parentId={replyToId}
              placeholder={
                replyToId
                  ? 'Répondre au commentaire...'
                  : 'Écrire un commentaire...'
              }
              onCommentAdded={handleCommentAdded}
            />
          ) : (
            <div className="text-center text-gray-500">
              <p>Vous devez être connecté pour commenter.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
