import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router';
import { Canvas } from '@react-three/fiber';
import { Stars } from '@react-three/drei';
import { EffectComposer, Bloom } from '@react-three/postprocessing';
import { ArrowLeft, Plus } from 'lucide-react';
import BoundedMapControls from '../components/three/BoundedMapControls';
import StarMesh from '../components/three/StarMesh';
import StarPanel from '../components/ui/StarPanel';
import StarCreateModal from '../components/ui/StarCreateModal';
import { useStarStore } from '../stores/starStore';
import { useGalaxies } from '../hooks/useGalaxies';
import { useGalaxyStars } from '../hooks/useStars';
import { LIFECYCLE_STYLE } from '../types/api';

export default function GalaxyPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [navigationState, setNavigationState] = useState({ vignetteIntensity: 0, showRecenterCue: false });
  const [isCreateOpen, setIsCreateOpen] = useState(false);

  const { data: galaxies = [] } = useGalaxies();
  const { data: stars = [], isLoading } = useGalaxyStars(id);
  const { selectStar, selectedStarSlug } = useStarStore();

  const galaxy = galaxies.find((g) => g.id === id);

  useEffect(() => {
    return () => selectStar(null);
  }, [selectStar]);

  const selectedStar = stars.find((s) => s.slug === selectedStarSlug) ?? null;
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
          <p className="text-xs font-mono text-white/40 mt-0.5">
            {isLoading ? 'loading...' : `${stars.length} stars`}
          </p>
        </div>
      </div>

      <button
        onClick={() => setIsCreateOpen(true)}
        className="absolute bottom-8 right-8 z-20 flex items-center gap-2 bg-[#A8D8FF]/90 hover:bg-[#A8D8FF] text-[#050510] font-mono font-bold text-sm px-4 py-2.5 rounded-full shadow-lg shadow-[#A8D8FF]/20 hover:shadow-[#A8D8FF]/40 transition-all duration-200 hover:scale-105"
      >
        <Plus size={16} />
        새 지식
      </button>

      <Canvas camera={{ position: [0, 0, 40], fov: 60 }}>
        <color attach="background" args={['#050510']} />
        <ambientLight intensity={0.5} />
        <Stars radius={100} depth={50} count={3000} factor={4} saturation={0} fade speed={1} />

        {stars.map((star) => {
          const style = LIFECYCLE_STYLE[star.lifecycle_state];
          return (
            <StarMesh
              key={star.id}
              position={[star.pos_x, star.pos_y, 0]}
              color={style.color}
              size={style.size}
              name={star.title}
              onClick={() => selectStar(star.slug)}
            />
          );
        })}

        <BoundedMapControls
          minDistance={8}
          maxDistance={130}
          onNavigationStateChange={setNavigationState}
        />

        <EffectComposer>
          <Bloom luminanceThreshold={0.15} luminanceSmoothing={0.9} intensity={1.2} mipmapBlur />
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

      <StarPanel star={selectedStar} galaxyColor={galaxy?.color} />

      {isCreateOpen && (
        <StarCreateModal
          preselectedGalaxyId={id}
          onClose={() => setIsCreateOpen(false)}
        />
      )}
    </div>
  );
}
