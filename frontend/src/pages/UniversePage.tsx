import { useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { Stars } from '@react-three/drei';
import { EffectComposer, Bloom } from '@react-three/postprocessing';
import { useNavigate } from 'react-router';
import { Compass, LogIn, Plus } from 'lucide-react';
import BoundedMapControls from '../components/three/BoundedMapControls';
import GalaxyCluster from '../components/three/GalaxyCluster';
import GalaxyCreateModal from '../components/ui/GalaxyCreateModal';
import { useGalaxies } from '../hooks/useGalaxies';
import { useAuthStore } from '../stores/authStore';
import { galaxyPosition } from '../stores/galaxyStore';

export default function UniversePage() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const isInitialized = useAuthStore((s) => s.isInitialized);
  const { data: galaxies = [], isLoading } = useGalaxies();
  const navigate = useNavigate();
  const [showGalaxyCreate, setShowGalaxyCreate] = useState(false);
  const [navigationState, setNavigationState] = useState({
    vignetteIntensity: 0,
    showRecenterCue: false,
  });

  const vignetteEdge = 0.48 + navigationState.vignetteIntensity * 0.28;
  const showGuestState = isInitialized && !isAuthenticated;
  const showEmptyState = isInitialized && isAuthenticated && !isLoading && galaxies.length === 0;

  return (
    <div className="w-full h-full relative">
      <div className="absolute top-4 left-4 z-20 pointer-events-none">
        <p className="text-[11px] font-mono text-white/20 tracking-[0.25em] uppercase">universe</p>
        {(!isInitialized || isLoading) && (
          <p className="text-[10px] font-mono text-white/20 mt-1">loading...</p>
        )}
      </div>

      <Canvas camera={{ position: [0, 0, 80], fov: 60 }}>
        <color attach="background" args={['#050510']} />
        <ambientLight intensity={0.5} />
        <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />

        {galaxies.map((galaxy, index) => (
          <GalaxyCluster
            key={galaxy.id}
            position={galaxyPosition(index, galaxies.length)}
            color={galaxy.color}
            name={galaxy.name}
            onClick={() => navigate(`/galaxy/${galaxy.id}`)}
          />
        ))}

        <BoundedMapControls
          minDistance={18}
          maxDistance={260}
          onNavigationStateChange={setNavigationState}
        />

        <EffectComposer>
          <Bloom luminanceThreshold={0.15} luminanceSmoothing={0.9} intensity={1.5} mipmapBlur />
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

      {showGuestState && (
        <div className="absolute inset-0 z-20 flex items-center justify-center px-6">
          <div className="w-full max-w-md rounded-lg border border-white/[0.1] bg-[#050510]/75 p-6 text-center shadow-2xl backdrop-blur-md">
            <p className="mb-3 text-[10px] font-mono uppercase tracking-[0.24em] text-white/30">guest universe</p>
            <h1 className="text-xl font-mono font-semibold tracking-wide text-white/90">내 우주는 로그인 후 생성됩니다</h1>
            <p className="mt-3 text-sm leading-6 text-white/50">
              공개로 열린 다른 사용자의 우주를 먼저 둘러보거나, 로그인해서 내 은하와 지식을 만들 수 있습니다.
            </p>
            <div className="mt-6 flex flex-col gap-2 sm:flex-row">
              <button
                onClick={() => navigate('/universes')}
                className="flex flex-1 items-center justify-center gap-2 rounded-lg bg-[#A8D8FF] px-4 py-2.5 text-sm font-bold text-[#050510] transition-colors hover:bg-[#A8D8FF]/90"
              >
                <Compass size={15} />
                우주 탐색
              </button>
              <button
                onClick={() => navigate('/auth/login')}
                className="flex flex-1 items-center justify-center gap-2 rounded-lg border border-white/[0.14] px-4 py-2.5 text-sm font-mono text-white/70 transition-colors hover:border-white/[0.28] hover:text-white"
              >
                <LogIn size={15} />
                로그인
              </button>
            </div>
          </div>
        </div>
      )}

      {showEmptyState && (
        <div className="absolute inset-0 z-20 flex items-center justify-center px-6">
          <div className="w-full max-w-md rounded-lg border border-white/[0.1] bg-[#050510]/75 p-6 text-center shadow-2xl backdrop-blur-md">
            <p className="mb-3 text-[10px] font-mono uppercase tracking-[0.24em] text-white/30">empty universe</p>
            <h1 className="text-xl font-mono font-semibold tracking-wide text-white/90">아직 생성된 은하가 없습니다</h1>
            <p className="mt-3 text-sm leading-6 text-white/50">
              첫 은하를 만들고, 그 안에 지식을 항성처럼 배치해보세요.
            </p>
            <button
              onClick={() => setShowGalaxyCreate(true)}
              className="mt-6 inline-flex items-center justify-center gap-2 rounded-lg bg-[#A8D8FF] px-5 py-2.5 text-sm font-bold text-[#050510] transition-colors hover:bg-[#A8D8FF]/90"
            >
              <Plus size={15} />
              새 은하 만들기
            </button>
          </div>
        </div>
      )}

      {showGalaxyCreate && (
        <GalaxyCreateModal onClose={() => setShowGalaxyCreate(false)} />
      )}
    </div>
  );
}
