import { useState } from 'react';
import { db } from '../lib/firebase';
import { collection, addDoc, serverTimestamp } from 'firebase/firestore';
import { useAuth } from '../lib/AuthContext';

const TECH_KEYWORDS = [
  'api', 'sdk', 'cli', 'sql', 'nosql', 'graphql', 'rest', 'grpc',
  'devops', 'mlops', 'dataops', 'devsecops', 'gitops', 'ci/cd', 'cicd',
  'docker', 'kubernetes', 'k8s', 'terraform', 'ansible', 'helm',
  'python', 'javascript', 'typescript', 'rust', 'golang', 'java', 'scala', 'kotlin',
  'react', 'vue', 'angular', 'svelte', 'nextjs', 'nuxt', 'node', 'deno', 'bun',
  'aws', 'azure', 'gcp', 'cloud', 'serverless', 'lambda', 'saas', 'paas', 'iaas',
  'data', 'database', 'postgres', 'mysql', 'mongo', 'redis', 'elastic', 'kafka',
  'spark', 'flink', 'airflow', 'dbt', 'dagster', 'prefect', 'snowflake', 'bigquery', 'redshift',
  'machine learning', 'deep learning', 'llm', 'gpt', 'transformer', 'neural', 'ai',
  'nlp', 'rag', 'embedding', 'fine-tuning', 'finetune', 'prompt',
  'git', 'github', 'gitlab', 'bitbucket', 'open source', 'opensource',
  'backend', 'frontend', 'fullstack', 'full-stack', 'microservice', 'monorepo',
  'algorithm', 'architecture', 'framework', 'library', 'package', 'module',
  'deploy', 'pipeline', 'orchestration', 'etl', 'elt', 'streaming',
  'security', 'auth', 'oauth', 'jwt', 'encryption', 'vulnerability', 'cve',
  'linux', 'unix', 'bash', 'shell', 'terminal', 'wasm', 'webassembly',
  'blockchain', 'web3', 'smart contract',
  'agile', 'scrum', 'kanban', 'sprint',
  'monitoring', 'observability', 'logging', 'tracing', 'prometheus', 'grafana',
  'testing', 'tdd', 'unittest', 'pytest', 'jest', 'cypress',
  'startup', 'saas', 'tech', 'engineering', 'developer', 'software', 'code', 'coding',
  'infra', 'infrastructure', 'network', 'dns', 'cdn', 'load balancer',
  'lakehouse', 'data lake', 'data warehouse', 'iceberg', 'delta', 'hudi',
  'governance', 'lineage', 'catalog', 'metadata',
  'tutorial', 'benchmark', 'migration', 'refactor', 'debug',
];

function looksLikeTech(url: string): { ok: boolean; reason?: string } {
  const text = url.toLowerCase();
  const found = TECH_KEYWORDS.some(kw => text.includes(kw));
  if (!found) {
    return { ok: false, reason: 'Cet article ne correspond pas à la thématique du site.' };
  }
  return { ok: true };
}

export default function SubmitArticle() {
  const { user, openLoginModal } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [url, setUrl] = useState('');
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

    // Tech moderation check
    const check = looksLikeTech(url);
    if (!check.ok) {
      setError(check.reason!);
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      await addDoc(collection(db, 'submissions'), {
        url: url.trim(),
        title: null,
        submitted_by: user.uid,
        submitted_by_name: user.displayName || 'Anonymous',
        submitted_at: serverTimestamp(),
        upvotes: 0,
        downvotes: 0,
      });

      setSuccess(true);
      setUrl('');

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
