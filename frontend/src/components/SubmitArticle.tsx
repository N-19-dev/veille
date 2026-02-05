import { useState } from 'react';
import { db } from '../lib/firebase';
import { collection, addDoc, serverTimestamp } from 'firebase/firestore';
import { useAuth } from '../lib/AuthContext';

const CATEGORIES = [
  { key: 'warehouses_engines', label: '🏛️ Warehouses & Query Engines' },
  { key: 'orchestration', label: '⚙️ Orchestration' },
  { key: 'data_governance', label: '📋 Data Governance' },
  { key: 'lakes_formats', label: '🌊 Data Lakes & Formats' },
  { key: 'cloud_infra', label: '☁️ Cloud & Infrastructure' },
  { key: 'python_dev', label: '🐍 Python & Dev Tools' },
  { key: 'ai_data_engineering', label: '🤖 AI & Data Engineering' },
  { key: 'news_trends', label: '📰 News & Trends' },
];

export default function SubmitArticle() {
  const { user, openLoginModal } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [url, setUrl] = useState('');
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!user) {
      openLoginModal();
      return;
    }

    if (!url.trim()) {
      setError('URL requise');
      return;
    }

    // Basic URL validation
    try {
      new URL(url);
    } catch {
      setError('URL invalide');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      await addDoc(collection(db, 'submissions'), {
        url: url.trim(),
        title: title.trim() || null,
        category_key: category || null,
        submitted_by: user.uid,
        submitted_by_name: user.displayName || 'Anonymous',
        submitted_at: serverTimestamp(),
        status: 'pending', // For future moderation
        upvotes: 0,
        downvotes: 0,
      });

      setSuccess(true);
      setUrl('');
      setTitle('');
      setCategory('');

      // Reset success message after 3s
      setTimeout(() => {
        setSuccess(false);
        setIsOpen(false);
      }, 3000);
    } catch (err) {
      console.error('Error submitting article:', err);
      setError('Erreur lors de la soumission. Réessayez.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) {
    return (
      <div className="text-center py-6">
        <button
          onClick={() => user ? setIsOpen(true) : openLoginModal()}
          className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-neutral-600 hover:text-neutral-900 hover:bg-neutral-100 rounded-lg transition"
        >
          <span>+</span>
          <span>Proposer un article</span>
        </button>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl border border-neutral-200 p-4 sm:p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-neutral-900">Proposer un article</h3>
        <button
          onClick={() => setIsOpen(false)}
          className="text-neutral-400 hover:text-neutral-600"
        >
          ✕
        </button>
      </div>

      {success ? (
        <div className="text-center py-4">
          <p className="text-green-600 font-medium">✓ Article soumis !</p>
          <p className="text-sm text-neutral-500 mt-1">Il apparaîtra dans le feed.</p>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="url" className="block text-sm font-medium text-neutral-700 mb-1">
              URL de l'article *
            </label>
            <input
              type="url"
              id="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://..."
              className="w-full px-3 py-2 border border-neutral-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          </div>

          <div>
            <label htmlFor="title" className="block text-sm font-medium text-neutral-700 mb-1">
              Titre (optionnel)
            </label>
            <input
              type="text"
              id="title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Sera extrait automatiquement si vide"
              className="w-full px-3 py-2 border border-neutral-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label htmlFor="category" className="block text-sm font-medium text-neutral-700 mb-1">
              Catégorie (optionnel)
            </label>
            <select
              id="category"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full px-3 py-2 border border-neutral-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">-- Sélectionner --</option>
              {CATEGORIES.map((cat) => (
                <option key={cat.key} value={cat.key}>
                  {cat.label}
                </option>
              ))}
            </select>
          </div>

          {error && (
            <p className="text-sm text-red-600">{error}</p>
          )}

          <button
            type="submit"
            disabled={isSubmitting}
            className={`w-full py-2 px-4 rounded-lg font-medium text-white transition ${
              isSubmitting
                ? 'bg-neutral-400 cursor-wait'
                : 'bg-blue-600 hover:bg-blue-700'
            }`}
          >
            {isSubmitting ? 'Envoi...' : 'Soumettre'}
          </button>
        </form>
      )}
    </div>
  );
}
