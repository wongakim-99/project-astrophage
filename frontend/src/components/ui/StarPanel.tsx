import { useState } from 'react';
import { X, ExternalLink, Pencil, Check, RotateCcw, Trash2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import TiptapEditor from './TiptapEditor';
import { Link } from 'react-router';
import { useAuthStore } from '../../stores/authStore';
import { useStarStore } from '../../stores/starStore';
import { useDeleteStar, useUpdateStar } from '../../hooks/useStars';
import type { StarResponse } from '../../types/api';
import { LIFECYCLE_STYLE } from '../../types/api';

interface StarPanelProps {
  star: StarResponse | null;
  galaxyColor?: string;
}

export default function StarPanel({ star, galaxyColor }: StarPanelProps) {
  const { isPanelOpen, setPanelOpen, selectStar } = useStarStore();
  const user = useAuthStore((s) => s.user);
  const { mutateAsync: updateStar, isPending: isSaving } = useUpdateStar();
  const { mutateAsync: deleteStar, isPending: isDeleting } = useDeleteStar();

  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState('');
  const [editContent, setEditContent] = useState('');
  const [isConfirmingDelete, setIsConfirmingDelete] = useState(false);

  const handleClose = () => {
    setIsEditing(false);
    setIsConfirmingDelete(false);
    setPanelOpen(false);
    setTimeout(() => selectStar(null), 300);
  };

  const handleDelete = async () => {
    if (!star) return;
    await deleteStar({ id: String(star.id), galaxy_id: String(star.galaxy_id) });
    handleClose();
  };

  const handleStartEdit = () => {
    setEditTitle(star?.title ?? '');
    setEditContent(star?.content ?? '');
    setIsEditing(true);
  };

  const handleCancel = () => {
    setIsEditing(false);
  };

  const handleSave = async () => {
    if (!star) return;
    await updateStar({ id: String(star.id), title: editTitle, content: editContent });
    setIsEditing(false);
  };

  const style = star ? LIFECYCLE_STYLE[star.lifecycle_state] : null;
  const publicUrl = star && user && star.is_public && user.is_universe_public
    ? `/${user.username}/stars/${star.slug}`
    : null;

  return (
    <div
      className={`fixed top-16 right-0 h-[calc(100vh-4rem)] transition-all duration-300 ease-in-out z-30 flex flex-col ${
        isPanelOpen && star
          ? `translate-x-0 ${isEditing ? 'w-[660px]' : 'w-80'}`
          : `translate-x-full ${isEditing ? 'w-[660px]' : 'w-80'}`
      }`}
      style={{
        background: 'rgba(8, 8, 28, 0.97)',
        borderLeft: `1px solid ${galaxyColor ? `${galaxyColor}22` : 'rgba(139, 92, 246, 0.2)'}`,
        boxShadow: '-12px 0 28px rgba(139, 92, 246, 0.08)',
      }}
    >
      {star && style && (
        <>
          {/* 헤더 */}
          <div className="flex items-start justify-between px-5 pt-5 pb-4 border-b border-white/[0.08]">
            <div className="flex-1 min-w-0 pr-3">
              {isEditing ? (
                <input
                  value={editTitle}
                  onChange={(e) => setEditTitle(e.target.value)}
                  className="w-full bg-transparent text-sm font-mono font-medium border-b border-white/20 pb-1 focus:outline-none focus:border-[#A8D8FF]/60 transition-colors"
                  style={{ color: style.color }}
                />
              ) : (
                <h2 className="text-sm font-mono font-medium leading-tight" style={{ color: style.color }}>
                  {star.title}
                </h2>
              )}
              <p className="text-[11px] font-mono text-white/50 mt-1 tracking-wider">{star.slug}</p>
            </div>

            <div className="flex items-center gap-0.5 shrink-0">
              {isEditing ? (
                <>
                  <button
                    onClick={handleCancel}
                    title="취소"
                    className="p-1.5 hover:bg-white/[0.08] rounded transition-colors text-white/40 hover:text-white/70"
                  >
                    <RotateCcw size={14} />
                  </button>
                  <button
                    onClick={() => { void handleSave(); }}
                    disabled={isSaving}
                    title="저장"
                    className="p-1.5 hover:bg-[#A8D8FF]/10 rounded transition-colors text-[#A8D8FF]/70 hover:text-[#A8D8FF] disabled:opacity-40"
                  >
                    <Check size={14} />
                  </button>
                </>
              ) : isConfirmingDelete ? (
                <>
                  <span className="text-[10px] font-mono text-red-400/80 tracking-wider mr-1">삭제?</span>
                  <button
                    onClick={() => setIsConfirmingDelete(false)}
                    title="취소"
                    className="p-1.5 hover:bg-white/[0.08] rounded transition-colors text-white/40 hover:text-white/70"
                  >
                    <RotateCcw size={14} />
                  </button>
                  <button
                    onClick={() => { void handleDelete(); }}
                    disabled={isDeleting}
                    title="삭제 확인"
                    className="p-1.5 hover:bg-red-500/20 rounded transition-colors text-red-400/70 hover:text-red-400 disabled:opacity-40"
                  >
                    <Check size={14} />
                  </button>
                </>
              ) : (
                <>
                  {publicUrl && (
                    <Link
                      to={publicUrl}
                      className="p-1.5 hover:bg-white/[0.08] rounded transition-colors text-white/40 hover:text-white/70"
                    >
                      <ExternalLink size={14} />
                    </Link>
                  )}
                  <button
                    onClick={handleStartEdit}
                    title="편집"
                    className="p-1.5 hover:bg-white/[0.08] rounded transition-colors text-white/40 hover:text-white/70"
                  >
                    <Pencil size={14} />
                  </button>
                  <button
                    onClick={() => setIsConfirmingDelete(true)}
                    title="삭제"
                    className="p-1.5 hover:bg-red-500/10 rounded transition-colors text-white/40 hover:text-red-400/80"
                  >
                    <Trash2 size={14} />
                  </button>
                  <button
                    onClick={handleClose}
                    title="닫기"
                    className="p-1.5 hover:bg-white/[0.08] rounded transition-colors text-white/40 hover:text-white/70"
                  >
                    <X size={14} />
                  </button>
                </>
              )}
            </div>
          </div>

          {/* 속성 — 편집 모드에선 숨겨서 에디터 공간 확보 */}
          {!isEditing && (
            <div className="px-5 py-3 border-b border-white/[0.06]">
              <div className="text-[9px] font-mono mb-3 tracking-[0.25em] uppercase" style={{ color: 'rgba(139,92,246,0.75)' }}>
                — properties
              </div>
              <div className="space-y-2.5">
                <div className="flex items-center gap-3">
                  <span className="text-[10px] font-mono text-white/45 w-16 shrink-0 tracking-wider">vis</span>
                  <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded tracking-wider ${
                    star.is_public ? 'text-brand-active bg-brand-active/15' : 'text-white/60 bg-white/[0.06]'
                  }`}>
                    {star.is_public ? 'public' : 'private'}
                  </span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-[10px] font-mono text-white/45 w-16 shrink-0 tracking-wider">energy</span>
                  <span className="text-[10px] font-mono text-white/70 tracking-wider">{star.energy_score.toFixed(1)}</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-[10px] font-mono text-white/45 w-16 shrink-0 tracking-wider">coords</span>
                  <span className="text-[10px] font-mono text-white/60 tracking-wider">
                    {star.pos_x.toFixed(1)}, {star.pos_y.toFixed(1)}
                  </span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-[10px] font-mono text-white/45 w-16 shrink-0 tracking-wider">state</span>
                  <span className="text-[10px] font-mono tracking-wider" style={{ color: style.color }}>
                    {star.lifecycle_state.replace('_', ' ')}
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* 본문 */}
          {isEditing ? (
            <div className="flex-1 overflow-y-auto px-5 py-4 custom-scrollbar">
              <TiptapEditor
                content={editContent}
                onChange={setEditContent}
                placeholder="내용을 입력하세요..."
                autofocus
                className="min-h-full"
              />
            </div>
          ) : (
            <div className="flex-1 overflow-y-auto px-5 py-4 custom-scrollbar">
              <div className="prose prose-invert prose-sm max-w-none prose-p:text-white/80 prose-headings:text-white/90 prose-headings:font-mono prose-headings:font-medium prose-code:text-brand-active/90 prose-code:bg-white/[0.06]">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {star.content || '*No content available.*'}
                </ReactMarkdown>
              </div>
            </div>
          )}

          {!isEditing && (
            <div className="px-5 py-2.5 border-t border-white/[0.06] text-[9px] font-mono text-white/40 tracking-widest">
              ✦ view time: recording
            </div>
          )}
        </>
      )}
    </div>
  );
}
