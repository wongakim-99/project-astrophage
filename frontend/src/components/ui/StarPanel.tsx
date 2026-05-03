
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
      className={`fixed top-16 right-0 w-80 h-[calc(100vh-4rem)] transition-transform duration-300 ease-in-out z-30 flex flex-col ${
        isPanelOpen && star ? 'translate-x-0' : 'translate-x-full'
      }`}
      style={{
        background: 'rgba(8, 8, 28, 0.97)',
        borderLeft: '1px solid rgba(139, 92, 246, 0.2)',
        boxShadow: '-12px 0 28px rgba(139, 92, 246, 0.08), inset 0 0 60px rgba(80, 40, 160, 0.04)',
      }}
    >
      {star && (
        <>
          {/* Header */}
          <div className="flex items-start justify-between px-5 pt-5 pb-4 border-b border-white/[0.08]">
            <div className="flex-1 min-w-0 pr-3">
              <h2 className="text-sm font-mono font-medium leading-tight" style={{ color: star.color }}>
                {star.name}
              </h2>
              <p className="text-[11px] font-mono text-white/50 mt-1 tracking-wider">{star.slug}</p>
            </div>
            <div className="flex items-center gap-0.5 shrink-0">
              <Link
                to={`/user/stars/${star.slug}`}
                className="p-1.5 hover:bg-white/[0.08] rounded transition-colors text-white/40 hover:text-white/70"
                title="Open full page"
              >
                <ExternalLink size={14} />
              </Link>
              <button
                onClick={handleClose}
                className="p-1.5 hover:bg-white/[0.08] rounded transition-colors text-white/40 hover:text-white/70"
              >
                <X size={14} />
              </button>
            </div>
          </div>

          {/* Properties */}
          <div className="px-5 py-3 border-b border-white/[0.06]">
            <div
              className="text-[9px] font-mono mb-3 tracking-[0.25em] uppercase"
              style={{ color: 'rgba(139,92,246,0.75)' }}
            >
              — properties
            </div>
            <div className="space-y-2.5">
              <div className="flex items-center gap-3">
                <span className="text-[10px] font-mono text-white/45 w-16 shrink-0 tracking-wider">vis</span>
                <span
                  className={`text-[10px] font-mono px-1.5 py-0.5 rounded tracking-wider ${
                    star.isPublic
                      ? 'text-brand-active bg-brand-active/15'
                      : 'text-white/60 bg-white/[0.06]'
                  }`}
                >
                  {star.isPublic ? 'public' : 'private'}
                </span>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-[10px] font-mono text-white/45 w-16 shrink-0 tracking-wider">size</span>
                <span className="text-[10px] font-mono text-white/70 tracking-wider">{star.size.toFixed(1)} au</span>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-[10px] font-mono text-white/45 w-16 shrink-0 tracking-wider">coords</span>
                <span className="text-[10px] font-mono text-white/60 tracking-wider">
                  {star.position[0].toFixed(1)}, {star.position[1].toFixed(1)}
                </span>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-[10px] font-mono text-white/45 w-16 shrink-0 tracking-wider">energy</span>
                <span className="text-[10px] font-mono tracking-wider" style={{ color: 'rgba(139,92,246,0.65)' }}>—</span>
              </div>
            </div>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto px-5 py-4 custom-scrollbar">
            <div className="prose prose-invert prose-sm max-w-none prose-p:text-white/80 prose-headings:text-white/90 prose-headings:font-mono prose-headings:font-medium prose-code:text-brand-active/90 prose-code:bg-white/[0.06]">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {star.content || '*No content available.*'}
              </ReactMarkdown>
            </div>
          </div>

          {/* Footer */}
          <div className="px-5 py-2.5 border-t border-white/[0.06] text-[9px] font-mono text-white/40 tracking-widest">
            ✦ view time: recording
          </div>
        </>
      )}
    </div>
  );
}
