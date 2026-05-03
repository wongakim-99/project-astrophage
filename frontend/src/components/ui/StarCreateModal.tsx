import { useState } from 'react';
import { X, Sparkles } from 'lucide-react';
import { useGalaxyStore } from '../../stores/galaxyStore';
import GalaxyCreateModal from './GalaxyCreateModal';

interface StarCreateModalProps {
  preselectedGalaxyId?: string;
  onClose: () => void;
}

export default function StarCreateModal({ preselectedGalaxyId, onClose }: StarCreateModalProps) {
  const galaxies = useGalaxyStore((s) => s.galaxies);

  const [form, setForm] = useState({
    title: '',
    slug: '',
    content: '',
    galaxyId: preselectedGalaxyId ?? galaxies[0]?.id ?? '',
  });
  const [showGalaxyCreate, setShowGalaxyCreate] = useState(false);

  const handleTitleChange = (title: string) => {
    const slug = title
      .toLowerCase()
      .replace(/\s+/g, '-')
      .replace(/[^a-z0-9ㄱ-ㅎ가-힣-]/g, '')
      .slice(0, 60);
    setForm((f) => ({ ...f, title, slug }));
  };

  const selectedGalaxy = galaxies.find((g) => g.id === form.galaxyId);
  const hasGalaxies = galaxies.length > 0;

  if (showGalaxyCreate) {
    return (
      <GalaxyCreateModal
        onClose={() => setShowGalaxyCreate(false)}
        onCreated={(id) => {
          setForm((f) => ({ ...f, galaxyId: id }));
          setShowGalaxyCreate(false);
        }}
      />
    );
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="relative w-full max-w-lg bg-[#0D0D20] border border-white/10 rounded-2xl shadow-2xl p-8">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-1.5 text-white/35 hover:text-white/70 hover:bg-white/[0.06] rounded transition-colors"
        >
          <X size={16} />
        </button>

        <h2 className="text-base font-mono font-medium text-white/90 mb-1 tracking-wider">새 지식 추가</h2>
        <p className="text-xs font-mono text-white/35 mb-6">
          새로운 항성을 우주에 배치합니다
        </p>

        {!hasGalaxies ? (
          /* 은하 없음 — 온보딩 유도 */
          <div className="flex flex-col items-center gap-4 py-8 text-center">
            <div className="w-12 h-12 rounded-full bg-white/[0.04] border border-white/[0.08] flex items-center justify-center">
              <Sparkles size={20} className="text-white/30" />
            </div>
            <div>
              <p className="text-sm font-mono text-white/65 mb-1">아직 은하가 없습니다</p>
              <p className="text-xs font-mono text-white/35">지식을 담을 은하를 먼저 만들어주세요</p>
            </div>
            <button
              onClick={() => setShowGalaxyCreate(true)}
              className="px-5 py-2.5 rounded-lg bg-[#A8D8FF] hover:bg-[#A8D8FF]/90 text-[#050510] font-bold text-sm transition-colors"
            >
              첫 번째 은하 만들기
            </button>
          </div>
        ) : (
          <div className="flex flex-col gap-4">
            {/* 은하 선택 */}
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-xs font-semibold text-white/65">은하 선택</label>
                <button
                  onClick={() => setShowGalaxyCreate(true)}
                  className="text-[11px] font-mono text-white/35 hover:text-white/60 transition-colors"
                >
                  + 새 은하
                </button>
              </div>
              <div className="flex flex-col gap-1.5 max-h-32 overflow-y-auto custom-scrollbar">
                {galaxies.map((galaxy) => (
                  <button
                    key={galaxy.id}
                    onClick={() => setForm((f) => ({ ...f, galaxyId: galaxy.id }))}
                    className={`flex items-center gap-2.5 px-3 py-2 rounded-lg text-left transition-colors border ${
                      form.galaxyId === galaxy.id
                        ? 'border-opacity-40 bg-opacity-10'
                        : 'border-white/[0.06] hover:bg-white/[0.04]'
                    }`}
                    style={
                      form.galaxyId === galaxy.id
                        ? { borderColor: `${galaxy.color}50`, background: `${galaxy.color}10` }
                        : {}
                    }
                  >
                    <span
                      className="w-2.5 h-2.5 rounded-full shrink-0"
                      style={{ backgroundColor: galaxy.color, boxShadow: `0 0 6px ${galaxy.color}` }}
                    />
                    <span className="text-sm font-mono" style={{ color: form.galaxyId === galaxy.id ? galaxy.color : 'rgba(255,255,255,0.65)' }}>
                      {galaxy.name}
                    </span>
                    {form.galaxyId === galaxy.id && (
                      <span className="ml-auto text-[10px] font-mono text-white/30">선택됨</span>
                    )}
                  </button>
                ))}
              </div>
              {/* API 연동 후 활성화될 임베딩 추천 안내 */}
              <p className="text-[10px] font-mono text-white/20 mt-1.5 flex items-center gap-1">
                <Sparkles size={9} />
                임베딩 기반 자동 추천은 API 연동 후 활성화됩니다
              </p>
            </div>

            {/* 제목 */}
            <div>
              <label className="block text-xs font-semibold text-white/65 mb-1.5">제목</label>
              <input
                type="text"
                placeholder={selectedGalaxy ? `${selectedGalaxy.name}의 새 개념` : '제목'}
                value={form.title}
                onChange={(e) => handleTitleChange(e.target.value)}
                autoFocus
                className="w-full bg-black/40 border border-white/10 rounded-lg px-4 py-2.5 text-white placeholder:text-white/25 focus:outline-none focus:border-[#A8D8FF]/60 transition-colors text-sm"
              />
            </div>

            {/* 슬러그 */}
            <div>
              <label className="block text-xs font-semibold text-white/65 mb-1.5">슬러그</label>
              <input
                type="text"
                value={form.slug}
                onChange={(e) => setForm((f) => ({ ...f, slug: e.target.value }))}
                className="w-full bg-black/40 border border-white/10 rounded-lg px-4 py-2.5 text-white/70 placeholder:text-white/25 focus:outline-none focus:border-[#A8D8FF]/60 transition-colors text-sm font-mono"
              />
            </div>

            {/* 내용 */}
            <div>
              <label className="block text-xs font-semibold text-white/65 mb-1.5">내용 (마크다운)</label>
              <textarea
                value={form.content}
                onChange={(e) => setForm((f) => ({ ...f, content: e.target.value }))}
                rows={5}
                className="w-full bg-black/40 border border-white/10 rounded-lg px-4 py-2.5 text-white placeholder:text-white/25 focus:outline-none focus:border-[#A8D8FF]/60 transition-colors text-sm resize-none custom-scrollbar"
              />
            </div>

            <div className="flex gap-3 mt-1">
              <button
                onClick={onClose}
                className="flex-1 py-2.5 rounded-lg border border-white/10 text-white/50 hover:text-white/75 hover:border-white/20 text-sm font-mono transition-colors"
              >
                취소
              </button>
              <button
                disabled={!form.title || !form.slug || !form.galaxyId}
                className="flex-1 py-2.5 rounded-lg bg-[#A8D8FF] hover:bg-[#A8D8FF]/90 text-[#050510] font-bold text-sm transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
              >
                생성
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
