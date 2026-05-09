import { useState } from 'react';
import { useParams, useNavigate, Navigate } from 'react-router';
import { ArrowLeft, Orbit } from 'lucide-react';
import TiptapEditor from '../components/ui/TiptapEditor';
import { useGalaxies } from '../hooks/useGalaxies';
import { useGalaxyStars, useUpdateStar } from '../hooks/useStars';
import { useAuthStore } from '../stores/authStore';

export default function StarEditPage() {
  const { id: galaxyId, starId } = useParams<{ id: string; starId: string }>();
  const navigate = useNavigate();

  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const isInitialized = useAuthStore((s) => s.isInitialized);

  const { data: galaxies = [] } = useGalaxies();
  const { data: stars = [], isLoading: isLoadingStars } = useGalaxyStars(galaxyId);
  const { mutateAsync: updateStar, isPending } = useUpdateStar();

  const star = stars.find((s) => s.id === starId);

  const [title, setTitle] = useState<string | null>(null);
  const [content, setContent] = useState<string | null>(null);
  const [error, setError] = useState('');

  if (!isInitialized) return null;
  if (!isAuthenticated) return <Navigate to="/auth/login" replace />;
  if (isLoadingStars) return null;
  if (!star) return <Navigate to={`/galaxy/${galaxyId}`} replace />;

  // 첫 렌더에서 한 번만 초기화 (이후 사용자가 입력한 값은 보존)
  const currentTitle = title ?? star.title;
  const currentContent = content ?? star.content;
  const galaxy = galaxies.find((g) => g.id === star.galaxy_id);

  const handleSave = async () => {
    if (!currentTitle.trim()) return;
    setError('');
    try {
      await updateStar({
        id: String(star.id),
        title: currentTitle.trim(),
        content: currentContent,
      });
      navigate(`/galaxy/${galaxyId}`);
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(msg ?? '항성 수정에 실패했습니다.');
    }
  };

  const canSave = currentTitle.trim() && !isPending;

  return (
    <div className="h-full w-full bg-[#050510] flex flex-col text-white">

      {/* 상단 툴바 */}
      <div className="flex items-center justify-between px-6 py-3 border-b border-white/[0.07] shrink-0">
        <button
          onClick={() => navigate(`/galaxy/${galaxyId}`)}
          className="flex items-center gap-1.5 text-xs font-mono text-white/45 hover:text-white/80 transition-colors"
        >
          <ArrowLeft size={13} />
          <span>돌아가기</span>
        </button>

        <div className="flex items-center gap-3">
          {/* 은하 표시 (편집 시에는 변경 불가) */}
          {galaxy && (
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-white/[0.08] bg-white/[0.03] text-xs font-mono text-white/50">
              <span className="w-2 h-2 rounded-full" style={{ backgroundColor: galaxy.color }} />
              <Orbit size={12} />
              <span>{galaxy.name}</span>
            </div>
          )}

          {error && <p className="text-xs text-red-400/80 font-mono">{error}</p>}

          <button
            onClick={() => { void handleSave(); }}
            disabled={!canSave}
            className="px-4 py-1.5 rounded-lg bg-[#A8D8FF] hover:bg-[#A8D8FF]/90 text-[#050510] font-bold text-sm transition-colors disabled:opacity-35 disabled:cursor-not-allowed"
          >
            {isPending ? '저장 중...' : '저장'}
          </button>
        </div>
      </div>

      {/* 에디터 영역 */}
      <div className="flex-1 overflow-y-auto custom-scrollbar">
        <div className="mx-auto max-w-3xl px-8 py-10 flex flex-col gap-4">

          {/* 제목 */}
          <input
            value={currentTitle}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="제목"
            autoFocus
            className="w-full bg-transparent text-4xl font-bold text-white/90 placeholder:text-white/15 focus:outline-none"
            style={{ fontFamily: "'Noto Sans KR', sans-serif", letterSpacing: '-0.01em' }}
          />

          {/* 슬러그 — 편집 시에는 변경 불가 (URL 안정성) */}
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono text-white/20">/stars/</span>
            <span className="flex-1 text-xs font-mono text-white/35">{star.slug}</span>
          </div>

          <div className="border-t border-white/[0.06]" />

          {/* tiptap 에디터 — 기존 내용 prefill */}
          <TiptapEditor
            content={star.content}
            onChange={setContent}
            placeholder="내용을 입력하세요&#10;# 를 입력하면 제목이 됩니다"
            autofocus={false}
            className="min-h-[60vh]"
          />
        </div>
      </div>
    </div>
  );
}
