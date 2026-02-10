import { useState, useEffect } from "react";
import { db } from "../lib/firebase";
import { collection, query, orderBy, onSnapshot, Timestamp } from "firebase/firestore";
import { faviconUrl } from "../lib/parse";
import { useAuth } from "../lib/AuthContext";
import SubmitArticle from "./SubmitArticle";

type Submission = {
  id: string;
  url: string;
  title: string | null;
  submitted_by: string;
  submitted_by_name: string;
  submitted_at: Timestamp;
  upvotes: number;
  downvotes: number;
};

const ADMIN_EMAIL = "natsornet@gmail.com";

export default function CommunityPage() {
  const { user } = useAuth();
  const [submissions, setSubmissions] = useState<Submission[]>([]);

  useEffect(() => {
    const q = query(
      collection(db, "submissions"),
      orderBy("submitted_at", "desc")
    );

    const unsubscribe = onSnapshot(
      q,
      (snapshot) => {
        const subs: Submission[] = [];
        snapshot.forEach((doc) => {
          subs.push({ id: doc.id, ...doc.data() } as Submission);
        });
        setSubmissions(subs);
      },
      (error) => {
        console.error("Error fetching submissions:", error);
      }
    );

    return () => unsubscribe();
  }, []);

  // Sort by score (upvotes - downvotes), then by date
  const sorted = [...submissions].sort((a, b) => {
    const scoreA = (a.upvotes || 0) - (a.downvotes || 0);
    const scoreB = (b.upvotes || 0) - (b.downvotes || 0);
    if (scoreB !== scoreA) return scoreB - scoreA;
    const dateA = a.submitted_at?.toDate?.()?.getTime() || 0;
    const dateB = b.submitted_at?.toDate?.()?.getTime() || 0;
    return dateB - dateA;
  });

  const handleDelete = async (id: string) => {
    if (!confirm("Supprimer cette soumission ?")) return;
    try {
      const { doc, deleteDoc } = await import("firebase/firestore");
      await deleteDoc(doc(db, "submissions", id));
    } catch (err) {
      console.error("Error deleting submission:", err);
    }
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-lg font-semibold text-neutral-900">
          Must Have ({submissions.length})
        </h2>
        <p className="text-sm text-neutral-500 mt-1">
          Les articles recommandés par la communauté
        </p>
      </div>

      {sorted.length === 0 ? (
        <p className="text-neutral-500 text-sm py-8 text-center">
          Aucun article proposé pour le moment.
        </p>
      ) : (
        <div className="space-y-3">
          {sorted.map((sub) => {
            let domain = "";
            try {
              domain = new URL(sub.url).hostname.replace(/^www\./, "");
            } catch {
              domain = "unknown";
            }

            const submittedAt = sub.submitted_at?.toDate?.() || new Date();
            const ageMs = Date.now() - submittedAt.getTime();
            const ageHours = Math.floor(ageMs / 3600000);
            const ageText =
              ageHours < 1
                ? "à l'instant"
                : ageHours < 24
                  ? `il y a ${ageHours}h`
                  : `il y a ${Math.floor(ageHours / 24)}j`;

            const score = (sub.upvotes || 0) - (sub.downvotes || 0);
            const canDelete =
              user?.email === ADMIN_EMAIL || user?.uid === sub.submitted_by;

            return (
              <div
                key={sub.id}
                className="bg-white rounded-xl border border-neutral-200 p-3 sm:p-4 hover:border-neutral-300 hover:shadow-sm transition-all"
              >
                <div className="flex gap-2.5 sm:gap-3">
                  <a
                    href={sub.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex gap-2.5 sm:gap-3 flex-1 min-w-0"
                  >
                    <img
                      src={faviconUrl(sub.url, 32)}
                      alt=""
                      className="w-7 h-7 sm:w-8 sm:h-8 rounded-md flex-shrink-0 mt-0.5"
                      loading="lazy"
                    />
                    <div className="flex-1 min-w-0">
                      <h3 className="font-medium text-neutral-900 leading-snug line-clamp-2 text-sm sm:text-base">
                        {sub.title || domain}
                      </h3>
                      <div className="flex items-center gap-1.5 sm:gap-2 mt-1 sm:mt-1.5 text-xs sm:text-sm text-neutral-500">
                        <span className="truncate">{domain}</span>
                        <span>·</span>
                        <span className="text-blue-600 font-medium truncate">
                          {sub.submitted_by_name}
                        </span>
                        <span>·</span>
                        <span className="flex-shrink-0">{ageText}</span>
                      </div>
                    </div>
                  </a>

                  <div className="flex items-center gap-2 flex-shrink-0">
                    {score !== 0 && (
                      <span
                        className={`text-xs font-medium px-1.5 py-0.5 rounded ${
                          score > 0
                            ? "text-green-700 bg-green-50"
                            : "text-red-700 bg-red-50"
                        }`}
                      >
                        {score > 0 ? `+${score}` : score}
                      </span>
                    )}
                    {canDelete && (
                      <button
                        onClick={() => handleDelete(sub.id)}
                        className="text-neutral-400 hover:text-red-500 transition p-1"
                        title="Supprimer"
                      >
                        ✕
                      </button>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      <SubmitArticle />
    </div>
  );
}
