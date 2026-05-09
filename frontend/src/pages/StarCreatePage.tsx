import { useState } from 'react';
import { useParams, useNavigate, Navigate } from 'react-router';
import { ArrowLeft, Orbit } from 'lucide-react';
import TiptapEditor from '../components/ui/TiptapEditor';
import { useGalaxies } from '../hooks/useGalaxies';
import { useCreateStar } from '../hooks/useStars';
import { useAuthStore } from '../stores/authStore';

function slugify(title: string): string {
  return title
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, '')
    .trim()
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .slice(0, 60);
}

export default function StarCreatePage() {
  const { id: galaxyId } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const isInitialized = useAuthStore((s) => s.isInitialized);

  const { data: galaxies = [] } = useGalaxies();
  const { mutateAsync: createStar, isPending } = useCreateStar();

  const [title, setTitle] = useState('');
  const [slug, setSlug] = useState('');
  const [content, setContent] = useState('');
  const [selectedGalaxyId, setSelectedGalaxyId] = useState(galaxyId ?? '');
  const [isSlugEdited, setIsSlugEdited] = useState(false);
  const [showGalaxyPicker, setShowGalaxyPicker] = useState(false);
  const [error, setError] = useState('');

  if (!isInitialized) return null;
  if (!isAuthenticated) return <Navigate to="/auth/login" replace />;

  const selectedGalaxy = galaxies.find((g) => g.id === selectedGalaxyId);

  const handleTitleChange = (value: string) => {
    setTitle(value);
    if (!isSlugEdited) setSlug(slugify(value));
  };

  const handleCreate = async () => {
    if (!title.trim() || !slug || !selectedGalaxyId) return;
    setError('');
    try {
      await createStar({
        title: title.trim(),
        slug,
        content,
        galaxy_id: selectedGalaxyId,
      });
      navigate(`/galaxy/${selectedGalaxyId}`);
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(msg ?? '항성 생성에 실패했습니다.');
    }
  };

  const canCreate = title.trim() && slug && selectedGalaxyId && !isPending;

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
          {/* 은하 선택 */}
          <div className="relative">
            <button
              onClick={() => setShowGalaxyPicker((v) => !v)}
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-white/[0.1] bg-white/[0.04] text-xs font-mono text-white/60 hover:text-white/85 hover:border-white/[0.2] transition-colors"
            >
              {selectedGalaxy && (
                <span className="w-2 h-2 rounded-full" style={{ backgroundColor: selectedGalaxy.color }} />
              )}
              <Orbit size={12} />
              <span>{selectedGalaxy?.name ?? '은하 선택'}</span>
            </button>

            {showGalaxyPicker && (
              <div className="absolute right-0 top-full mt-1 w-52 bg-[#0D0D20] border border-white/[0.1] rounded-xl shadow-2xl z-50 overflow-hidden">
                {galaxies.map((galaxy) => (
                  <button
                    key={galaxy.id}
                    onClick={() => { setSelectedGalaxyId(galaxy.id); setShowGalaxyPicker(false); }}
                    className="flex items-center gap-2.5 w-full px-4 py-2.5 text-sm font-mono text-left transition-colors hover:bg-white/[0.05]"
                    style={{ color: galaxy.id === selectedGalaxyId ? galaxy.color : 'rgba(255,255,255,0.65)' }}
                  >
                    <span className="w-2 h-2 rounded-full shrink-0" style={{ backgroundColor: galaxy.color }} />
                    {galaxy.name}
                  </button>
                ))}
              </div>
            )}
          </div>

          {error && <p className="text-xs text-red-400/80 font-mono">{error}</p>}

          <button
            onClick={() => { void handleCreate(); }}
            disabled={!canCreate}
            className="px-4 py-1.5 rounded-lg bg-[#A8D8FF] hover:bg-[#A8D8FF]/90 text-[#050510] font-bold text-sm transition-colors disabled:opacity-35 disabled:cursor-not-allowed"
          >
            {isPending ? '생성 중...' : '생성'}
          </button>
        </div>
      </div>

      {/* 에디터 영역 */}
      <div className="flex-1 overflow-y-auto custom-scrollbar">
        <div className="mx-auto max-w-3xl px-8 py-10 flex flex-col gap-4">

          {/* 제목 */}
          <input
            value={title}
            onChange={(e) => handleTitleChange(e.target.value)}
            placeholder="제목"
            autoFocus
            className="w-full bg-transparent text-4xl font-bold text-white/90 placeholder:text-white/15 focus:outline-none"
            style={{ fontFamily: "'Noto Sans KR', sans-serif", letterSpacing: '-0.01em' }}
          />

          {/* 슬러그 */}
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono text-white/20">/stars/</span>
            <input
              value={slug}
              onChange={(e) => {
                setSlug(e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, ''));
                setIsSlugEdited(true);
              }}
              placeholder="slug"
              className="flex-1 bg-transparent text-xs font-mono text-white/35 placeholder:text-white/15 focus:outline-none focus:text-white/55 transition-colors"
            />
          </div>

          <div className="border-t border-white/[0.06]" />

          {/* tiptap 에디터 */}
          <TiptapEditor
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
