
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
    setTimeout(() => selectStar(null), 300);
  };

  return (
    <div
      className={`fixed top-16 right-0 w-80 h-[calc(100vh-4rem)] bg-[#07071a] border-l border-white/[0.05] shadow-2xl transition-transform duration-300 ease-in-out z-30 flex flex-col ${
        isPanelOpen && star ? 'translate-x-0' : 'translate-x-full'
      }`}
    >
      {star && (
        <>
          {/* Header */}
          <div className="flex items-start justify-between px-5 pt-5 pb-4 border-b border-white/[0.05]">
            <div className="flex-1 min-w-0 pr-3">
              <h2 className="text-sm font-mono font-medium leading-tight" style={{ color: star.color }}>
                {star.name}
              </h2>
              <p className="text-[10px] font-mono text-white/20 mt-1 tracking-wider">{star.slug}</p>
            </div>
            <div className="flex items-center gap-0.5 shrink-0">
              <Link
                to={`/user/stars/${star.slug}`}
                className="p-1.5 hover:bg-white/[0.06] rounded transition-colors text-white/20 hover:text-white/50"
                title="Open full page"
              >
                <ExternalLink size={14} />
              </Link>
              <button
                onClick={handleClose}
                className="p-1.5 hover:bg-white/[0.06] rounded transition-colors text-white/20 hover:text-white/50"
              >
                <X size={14} />
              </button>
            </div>
          </div>

          {/* Properties — Obsidian frontmatter style */}
          <div className="px-5 py-3 border-b border-white/[0.05]">
            <div className="text-[9px] font-mono text-white/20 mb-3 tracking-[0.2em] uppercase">
              Properties
            </div>
            <div className="space-y-2">
              <div className="flex items-center gap-3">
                <span className="text-[10px] font-mono text-white/25 w-16 shrink-0">visibility</span>
                <span
                  className={`text-[10px] font-mono px-1.5 py-0.5 rounded ${
                    star.isPublic
                      ? 'text-brand-active bg-brand-active/10'
                      : 'text-white/35 bg-white/[0.04]'
                  }`}
                >
                  {star.isPublic ? 'public' : 'private'}
                </span>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-[10px] font-mono text-white/25 w-16 shrink-0">size</span>
                <span className="text-[10px] font-mono text-white/40">{star.size.toFixed(1)} au</span>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-[10px] font-mono text-white/25 w-16 shrink-0">energy</span>
                <span className="text-[10px] font-mono text-white/25">—</span>
              </div>
            </div>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto px-5 py-4 custom-scrollbar">
            <div className="prose prose-invert prose-sm max-w-none prose-p:text-white/55 prose-headings:text-white/75 prose-headings:font-mono prose-headings:font-medium prose-code:text-brand-active/80 prose-code:bg-white/[0.04]">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {star.content || '*No content available.*'}
              </ReactMarkdown>
            </div>
          </div>

          {/* Footer */}
          <div className="px-5 py-2.5 border-t border-white/[0.04] text-[9px] font-mono text-white/15 tracking-widest">
            ✦ view time: recording
          </div>
        </>
      )}
    </div>
  );
}
