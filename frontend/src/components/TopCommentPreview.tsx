import { useEffect, useState } from 'react';
import { collection, query, where, orderBy, limit, onSnapshot } from 'firebase/firestore';
import { db } from '../lib/firebase';
import { useComments } from '../lib/CommentsContext';

interface TopCommentPreviewProps {
  articleId: string;
  articleUrl: string;
  articleTitle: string;
  weekLabel: string;
  category: string;
  source: string;
}

interface CommentPreview {
  id: string;
  content: string;
  user_name: string;
  likes: number;
}

export default function TopCommentPreview({
  articleId,
  articleUrl,
  articleTitle,
  weekLabel,
  category,
  source
}: TopCommentPreviewProps) {
  const [topComment, setTopComment] = useState<CommentPreview | null>(null);
  const [loading, setLoading] = useState(true);
  const { openCommentsModal } = useComments();

  useEffect(() => {
    const commentsRef = collection(db, 'comments');
    const q = query(
      commentsRef,
      where('article_id', '==', articleId),
      where('week_label', '==', weekLabel),
      where('parent_id', '==', null),
      orderBy('likes', 'desc'),
      limit(1)
    );

    const unsubscribe = onSnapshot(
      q,
      (snapshot) => {
        if (!snapshot.empty) {
          const doc = snapshot.docs[0];
          const data = doc.data();
          setTopComment({
            id: doc.id,
            content: data.content,
            user_name: data.user_name,
            likes: data.likes || 0
          });
        } else {
          setTopComment(null);
        }
        setLoading(false);
      },
      (error) => {
        console.error('Error fetching top comment:', error);
        setLoading(false);
      }
    );

    return () => unsubscribe();
  }, [articleId, weekLabel]);

  if (loading || !topComment) {
    return null;
  }

  // Truncate to ~80 chars
  const truncated = topComment.content.length > 80
    ? topComment.content.substring(0, 80).trim() + '…'
    : topComment.content;

  return (
    <button
      onClick={() => openCommentsModal(articleId, articleUrl, articleTitle, weekLabel, category, source)}
      className="text-left text-xs text-neutral-400 hover:text-neutral-600 transition-colors truncate"
    >
      <span className="font-medium">{topComment.user_name}:</span>{' '}
      <span className="italic">"{truncated}"</span>
    </button>
  );
}
