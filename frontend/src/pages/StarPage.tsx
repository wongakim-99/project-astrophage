
import { useParams } from 'react-router';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useStarStore } from '../stores/starStore';

export default function StarPage() {
  const { username, slug } = useParams();
  const stars = useStarStore((state) => state.stars);
  const star = stars.find(s => s.slug === slug);

  if (!star) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-background text-foreground">
        <p className="text-xl opacity-50">Star not found.</p>
      </div>
    );
  }

  return (
    <div className="w-full h-full overflow-y-auto bg-background text-foreground custom-scrollbar">
      <div className="max-w-3xl mx-auto w-full p-8 my-12 bg-[#0A0A15]/80 backdrop-blur-xl rounded-2xl border border-white/10 shadow-2xl">
        <div className="mb-10 pb-6 border-b border-white/10">
          <div className="flex items-center gap-3 mb-4">
            <div 
              className="w-4 h-4 rounded-full shadow-[0_0_10px_rgba(255,255,255,0.5)]" 
              style={{ backgroundColor: star.color, boxShadow: `0 0 15px ${star.color}` }}
            />
            <h1 className="text-4xl font-bold tracking-tight" style={{ color: star.color }}>
              {star.name}
            </h1>
          </div>
          <div className="flex items-center gap-4 text-sm opacity-70">
            <span>@{username}</span>
            <span>•</span>
            <span>{star.isPublic ? 'Public' : 'Private'}</span>
          </div>
        </div>

        <div className="prose prose-invert max-w-none prose-headings:font-bold prose-a:text-brand-active hover:prose-a:text-brand-normal transition-colors">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {star.content || '*No content available.*'}
          </ReactMarkdown>
        </div>
      </div>
    </div>
  );
}
