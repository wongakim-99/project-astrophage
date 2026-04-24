
import { X, ExternalLink } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Link } from 'react-router';
import { useStarStore } from '../../stores/starStore';

export default function StarPanel() {
  const { stars, selectedStarSlug, isPanelOpen, setPanelOpen, selectStar } = useStarStore();
  
  const star = stars.find((s) => s.slug === selectedStarSlug);

  const handleClose = () => {
    setPanelOpen(false);
    // Optional: wait for animation to finish before clearing selected star
    setTimeout(() => selectStar(null), 300);
  };

  return (
    <div
      className={`fixed top-16 right-0 w-96 h-[calc(100vh-4rem)] bg-[#0A0A15]/90 backdrop-blur-xl border-l border-white/10 shadow-2xl transition-transform duration-300 ease-in-out z-30 flex flex-col ${
        isPanelOpen && star ? 'translate-x-0' : 'translate-x-full'
      }`}
    >
      {star && (
        <>
          <div className="flex items-center justify-between p-6 border-b border-white/10">
            <div>
              <h2 className="text-2xl font-bold" style={{ color: star.color }}>
                {star.name}
              </h2>
              <p className="text-xs text-foreground/50 mt-1 tracking-wider">
                {star.isPublic ? 'PUBLIC STAR' : 'PRIVATE STAR'}
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Link
                to={`/user/stars/${star.slug}`} // Assuming 'user' for dummy, should be real username later
                className="p-2 hover:bg-white/10 rounded-full transition-colors text-foreground/70 hover:text-white"
                title="Open full page"
              >
                <ExternalLink size={20} />
              </Link>
              <button
                onClick={handleClose}
                className="p-2 hover:bg-white/10 rounded-full transition-colors text-foreground/70 hover:text-white"
              >
                <X size={20} />
              </button>
            </div>
          </div>
          
          <div className="flex-1 overflow-y-auto p-6 custom-scrollbar">
            <div className="prose prose-invert prose-sm max-w-none">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {star.content || '*No content available.*'}
              </ReactMarkdown>
            </div>
          </div>
          
          <div className="p-4 border-t border-white/10 bg-black/20 text-xs text-foreground/40 text-center">
            View Time: Recording...
          </div>
        </>
      )}
    </div>
  );
}
