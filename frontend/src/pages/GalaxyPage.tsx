import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router';
import { Canvas } from '@react-three/fiber';
import { Stars } from '@react-three/drei';
import { EffectComposer, Bloom } from '@react-three/postprocessing';
import { ArrowLeft, Plus, X } from 'lucide-react';
import BoundedMapControls from '../components/three/BoundedMapControls';
import StarMesh from '../components/three/StarMesh';
import StarPanel from '../components/ui/StarPanel';
import { useStarStore } from '../stores/starStore';
import { useGalaxyStore } from '../stores/galaxyStore';

export default function GalaxyPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [navigationState, setNavigationState] = useState({
    vignetteIntensity: 0,
    showRecenterCue: false,
  });
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [form, setForm] = useState({ title: '', slug: '', content: '' });

  const galaxies = useGalaxyStore((state) => state.galaxies);
  const galaxy = galaxies.find(g => g.id === id);

  const stars = useStarStore((state) => state.stars);
  const selectStar = useStarStore((state) => state.selectStar);

  const galaxyStars = stars.filter(s => s.galaxyId === id);

  useEffect(() => {
    return () => selectStar(null);
  }, [selectStar]);

  const handleTitleChange = (title: string) => {
    const slug = title
      .toLowerCase()
      .replace(/\s+/g, '-')
      .replace(/[^a-z0-9ㄱ-ㅎ가-힣-]/g, '')
      .slice(0, 60);
    setForm(f => ({ ...f, title, slug }));
  };

  const vignetteEdge = 0.48 + navigationState.vignetteIntensity * 0.28;

  return (
    <div className="w-full h-full relative overflow-hidden">
      <div className="absolute top-4 left-4 z-20 flex flex-col gap-2">
        <button
          onClick={() => navigate('/universe')}
          className="flex items-center gap-1.5 text-xs font-mono text-white/50 hover:text-white/80 transition-colors bg-white/[0.04] hover:bg-white/[0.08] px-3 py-1.5 rounded border border-white/[0.08] hover:border-white/[0.18] w-fit"
        >
          <ArrowLeft size={12} />
          <span>universe</span>
        </button>
        <div className="pointer-events-none mt-1">
          <h1 className="text-lg font-mono font-medium tracking-wider" style={{ color: galaxy?.color || '#fff' }}>
            {galaxy?.name || 'unknown galaxy'}
          </h1>
          <p className="text-xs font-mono text-white/40 mt-0.5">{galaxyStars.length} stars</p>
        </div>
      </div>

      {/* 새 지식 추가 버튼 */}
      <button
        onClick={() => { setIsCreateOpen(true); setForm({ title: '', slug: '', content: '' }); }}
        className="absolute bottom-8 right-8 z-20 flex items-center gap-2 bg-[#A8D8FF]/90 hover:bg-[#A8D8FF] text-[#050510] font-mono font-bold text-sm px-4 py-2.5 rounded-full shadow-lg shadow-[#A8D8FF]/20 hover:shadow-[#A8D8FF]/40 transition-all duration-200 hover:scale-105"
      >
        <Plus size={16} />
        새 지식
      </button>

      <Canvas camera={{ position: [0, 0, 40], fov: 60 }}>
        <color attach="background" args={['#050510']} />
        <ambientLight intensity={0.5} />
        <Stars radius={100} depth={50} count={3000} factor={4} saturation={0} fade speed={1} />

        {galaxyStars.map((star) => (
          <StarMesh
            key={star.id}
            position={star.position}
            color={star.color}
            size={star.size}
            name={star.name}
            onClick={() => selectStar(star.slug)}
          />
        ))}

        <BoundedMapControls
          minDistance={8}
          maxDistance={130}
          onNavigationStateChange={setNavigationState}
        />

        <EffectComposer>
          <Bloom
            luminanceThreshold={0.15}
            luminanceSmoothing={0.9}
            intensity={1.2}
            mipmapBlur
          />
        </EffectComposer>
      </Canvas>

      <div
        className="pointer-events-none absolute inset-0 z-10 transition-opacity duration-150"
        style={{
          opacity: navigationState.vignetteIntensity,
          background: `radial-gradient(circle at center, rgba(0,0,0,0) 38%, rgba(0,0,0,0.22) 68%, rgba(0,0,0,${vignetteEdge}) 100%)`,
        }}
      />

      <div
        className={`pointer-events-none absolute bottom-6 left-1/2 z-20 -translate-x-1/2 rounded border border-white/[0.08] bg-black/25 px-3 py-1.5 font-mono text-[10px] tracking-[0.24em] text-white/35 backdrop-blur-sm transition-all duration-200 ${
          navigationState.showRecenterCue ? 'translate-y-0 opacity-100' : 'translate-y-1 opacity-0'
        }`}
      >
        [ SPACE : RECENTER ]
      </div>

      <StarPanel />

      {/* 새 지식 추가 모달 */}
      {isCreateOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
          <div className="relative w-full max-w-lg bg-[#0D0D20] border border-white/10 rounded-2xl shadow-2xl p-8">
            <button
              onClick={() => setIsCreateOpen(false)}
              className="absolute top-4 right-4 p-1.5 text-white/35 hover:text-white/70 hover:bg-white/[0.06] rounded transition-colors"
            >
              <X size={16} />
            </button>

            <h2 className="text-base font-mono font-medium text-white/90 mb-1 tracking-wider">새 지식 추가</h2>
            <p className="text-xs font-mono text-white/35 mb-6">
              {galaxy?.name || '이 은하'}에 새로운 항성을 생성합니다
            </p>

            <div className="flex flex-col gap-4">
              <div>
                <label className="block text-xs font-semibold text-white/65 mb-1.5">제목</label>
                <input
                  type="text"
                  placeholder="React Hooks"
                  value={form.title}
                  onChange={e => handleTitleChange(e.target.value)}
                  className="w-full bg-black/40 border border-white/10 rounded-lg px-4 py-2.5 text-white placeholder:text-white/25 focus:outline-none focus:border-[#A8D8FF]/60 transition-colors text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-white/65 mb-1.5">슬러그</label>
                <input
                  type="text"
                  placeholder="react-hooks"
                  value={form.slug}
                  onChange={e => setForm(f => ({ ...f, slug: e.target.value }))}
                  className="w-full bg-black/40 border border-white/10 rounded-lg px-4 py-2.5 text-white/70 placeholder:text-white/25 focus:outline-none focus:border-[#A8D8FF]/60 transition-colors text-sm font-mono"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-white/65 mb-1.5">내용 (마크다운)</label>
                <textarea
                  placeholder="# React Hooks&#10;&#10;훅은 함수 컴포넌트에서 상태와 사이드이펙트를 다루는 방법이다..."
                  value={form.content}
                  onChange={e => setForm(f => ({ ...f, content: e.target.value }))}
                  rows={6}
                  className="w-full bg-black/40 border border-white/10 rounded-lg px-4 py-2.5 text-white placeholder:text-white/25 focus:outline-none focus:border-[#A8D8FF]/60 transition-colors text-sm resize-none custom-scrollbar"
                />
              </div>

              <div className="flex gap-3 mt-2">
                <button
                  type="button"
                  onClick={() => setIsCreateOpen(false)}
                  className="flex-1 py-2.5 rounded-lg border border-white/10 text-white/50 hover:text-white/75 hover:border-white/20 text-sm font-mono transition-colors"
                >
                  취소
                </button>
                <button
                  type="button"
                  disabled={!form.title || !form.slug}
                  className="flex-1 py-2.5 rounded-lg bg-[#A8D8FF] hover:bg-[#A8D8FF]/90 text-[#050510] font-bold text-sm transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  생성
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
