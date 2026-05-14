import { useState } from 'react';
import { X, ExternalLink, Pencil, Trash2 } from 'lucide-react';
import { Link, useNavigate } from 'react-router';
import { useAuthStore } from '../../stores/authStore';
import { useStarStore } from '../../stores/starStore';
import { useDeleteStar, useToggleStarVisibility } from '../../hooks/useStars';
import type { StarResponse } from '../../types/api';
import { LIFECYCLE_STYLE } from '../../types/api';

interface StarPanelProps {
  star: StarResponse | null;
  galaxyColor?: string;
}

export default function StarPanel({ star, galaxyColor }: StarPanelProps) {
  const navigate = useNavigate();
  const { isPanelOpen, setPanelOpen, selectStar } = useStarStore();
  const user = useAuthStore((s) => s.user);
  const { mutateAsync: deleteStar, isPending: isDeleting } = useDeleteStar();
  const { mutateAsync: toggleVisibility, isPending: isTogglingVisibility } = useToggleStarVisibility();

  const [isConfirmingDelete, setIsConfirmingDelete] = useState(false);

  const handleClose = () => {
    setIsConfirmingDelete(false);
    setPanelOpen(false);
    setTimeout(() => selectStar(null), 300);
  };

  const handleDelete = async () => {
    if (!star) return;
    await deleteStar({ id: String(star.id), galaxy_id: String(star.galaxy_id) });
    handleClose();
  };

  const handleEdit = () => {
    if (!star) return;
    navigate(`/galaxy/${star.galaxy_id}/edit/${star.id}`);
  };

  const style = star ? LIFECYCLE_STYLE[star.lifecycle_state] : null;
  const publicUrl = star && user && star.is_public && user.is_universe_public
    ? `/${user.username}/stars/${star.slug}`
    : null;

  return (
    <div
      className={`fixed top-16 right-0 h-[calc(100vh-4rem)] w-[660px] transition-transform duration-300 ease-in-out z-30 flex flex-col ${
        isPanelOpen && star ? 'translate-x-0' : 'translate-x-full'
      }`}
      style={{
        background: 'rgba(8, 8, 28, 0.97)',
        borderLeft: `1px solid ${galaxyColor ? `${galaxyColor}22` : 'rgba(139, 92, 246, 0.2)'}`,
        boxShadow: '-12px 0 28px rgba(139, 92, 246, 0.08)',
      }}
    >
      {isConfirmingDelete && (
        <div
          className="absolute inset-0 z-40 flex flex-col items-center justify-center gap-3"
          style={{ background: 'rgba(8, 8, 28, 0.93)' }}
        >
          <Trash2 size={28} className="text-red-400/50 mb-1" />
          <p className="text-sm font-mono text-white/80">항성을 삭제할까요?</p>
          <p className="text-[11px] font-mono text-white/40 mb-2">이 작업은 되돌릴 수 없습니다.</p>
          <div className="flex gap-2">
            <button
              onClick={() => setIsConfirmingDelete(false)}
              className="px-4 py-1.5 text-xs font-mono rounded border border-white/10 text-white/50 hover:text-white/80 hover:bg-white/[0.06] transition-colors"
            >
              취소
            </button>
            <button
              onClick={() => { void handleDelete(); }}
              disabled={isDeleting}
              className="px-4 py-1.5 text-xs font-mono rounded bg-red-500/20 border border-red-500/30 text-red-400 hover:bg-red-500/30 transition-colors disabled:opacity-40"
            >
              {isDeleting ? '삭제 중...' : '삭제'}
            </button>
          </div>
        </div>
      )}

      {star && style && (
        <>
          {/* 헤더 */}
          <div className="flex items-start justify-between px-8 pt-6 pb-5 border-b border-white/[0.08]">
            <div className="flex-1 min-w-0 pr-4">
              <h2 className="text-2xl font-bold leading-tight" style={{ color: style.color, fontFamily: "'Noto Sans KR', sans-serif", letterSpacing: '-0.01em' }}>
                {star.title}
              </h2>
              <p className="text-[11px] font-mono text-white/40 mt-2 tracking-wider">/stars/{star.slug}</p>
            </div>

            <div className="flex items-center gap-1 shrink-0">
              {publicUrl && (
                <Link
                  to={publicUrl}
                  title="공개 페이지"
                  className="p-2 hover:bg-white/[0.08] rounded transition-colors text-white/40 hover:text-white/70"
                >
                  <ExternalLink size={16} />
                </Link>
              )}
              <button
                onClick={handleEdit}
                title="편집"
                className="p-2 hover:bg-white/[0.08] rounded transition-colors text-white/40 hover:text-white/70"
              >
                <Pencil size={16} />
              </button>
              <button
                onClick={() => setIsConfirmingDelete(true)}
                title="삭제"
                className="p-2 hover:bg-red-500/10 rounded transition-colors text-white/40 hover:text-red-400/80"
              >
                <Trash2 size={16} />
              </button>
              <button
                onClick={handleClose}
                title="닫기"
                className="p-2 hover:bg-white/[0.08] rounded transition-colors text-white/40 hover:text-white/70"
              >
                <X size={16} />
              </button>
            </div>
          </div>

          {/* 속성 */}
          <div className="px-8 py-3 border-b border-white/[0.06]">
            <div className="flex items-center gap-6 text-[10px] font-mono tracking-wider">
              <div className="flex items-center gap-2">
                <span className="text-white/35">vis</span>
                <button
                  onClick={() => {
                    void toggleVisibility({
                      id: String(star.id),
                      galaxy_id: String(star.galaxy_id),
                      is_public: !star.is_public,
                    });
                  }}
                  disabled={isTogglingVisibility}
                  className={`px-1.5 py-0.5 rounded transition-colors disabled:opacity-50 ${
                    star.is_public
                      ? 'text-brand-active bg-brand-active/15 hover:bg-brand-active/25'
                      : 'text-white/60 bg-white/[0.06] hover:bg-white/[0.12]'
                  }`}
                >
                  {star.is_public ? 'public' : 'private'}
                </button>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-white/35">energy</span>
                <span className="text-white/70">{star.energy_score.toFixed(1)}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-white/35">coords</span>
                <span className="text-white/60">{star.pos_x.toFixed(1)}, {star.pos_y.toFixed(1)}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-white/35">state</span>
                <span style={{ color: style.color }}>{star.lifecycle_state.replace('_', ' ')}</span>
              </div>
            </div>
          </div>

          {/* 본문 — Tiptap이 HTML로 저장하므로 prose 스타일로 직접 렌더 */}
          <div className="flex-1 overflow-y-auto px-8 py-6 custom-scrollbar">
            {star.content ? (
              <div
                className="prose prose-invert prose-sm max-w-none prose-p:text-white/80 prose-headings:text-white/90 prose-headings:font-bold prose-strong:text-white/95 prose-code:text-brand-active/90 prose-code:bg-white/[0.06] prose-code:px-1 prose-code:py-0.5 prose-code:rounded prose-li:text-white/80 prose-a:text-brand-active prose-blockquote:border-l-brand-active/40 prose-blockquote:text-white/60"
                dangerouslySetInnerHTML={{ __html: star.content }}
              />
            ) : (
              <p className="text-sm font-mono text-white/30 italic">No content available.</p>
            )}
          </div>

          <div className="px-8 py-3 border-t border-white/[0.06] text-[9px] font-mono text-white/40 tracking-widest">
            ✦ view time: recording
          </div>
        </>
      )}
    </div>
  );
}
