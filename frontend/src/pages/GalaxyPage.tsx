import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router';
import { Canvas } from '@react-three/fiber';
import { Stars } from '@react-three/drei';
import { EffectComposer, Bloom } from '@react-three/postprocessing';
import { ArrowLeft } from 'lucide-react';
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

  const galaxies = useGalaxyStore((state) => state.galaxies);
  const galaxy = galaxies.find(g => g.id === id);

  const stars = useStarStore((state) => state.stars);
  const selectStar = useStarStore((state) => state.selectStar);

  const galaxyStars = stars.filter(s => s.galaxyId === id);

  useEffect(() => {
    return () => selectStar(null);
  }, [selectStar]);

  const vignetteEdge = 0.48 + navigationState.vignetteIntensity * 0.28;

  return (
    <div className="w-full h-full relative overflow-hidden">
      <div className="absolute top-4 left-4 z-20 flex flex-col gap-2">
        <button
          onClick={() => navigate('/universe')}
          className="flex items-center gap-1.5 text-[11px] font-mono text-white/30 hover:text-white/60 transition-colors bg-white/[0.03] hover:bg-white/[0.06] px-3 py-1.5 rounded border border-white/[0.06] hover:border-white/[0.12] w-fit"
        >
          <ArrowLeft size={12} />
          <span>universe</span>
        </button>
        <div className="pointer-events-none mt-1">
          <h1 className="text-lg font-mono font-medium tracking-wider" style={{ color: galaxy?.color || '#fff' }}>
            {galaxy?.name || 'unknown galaxy'}
          </h1>
          <p className="text-[11px] font-mono text-white/25 mt-0.5">{galaxyStars.length} stars</p>
        </div>
      </div>

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
    </div>
  );
}
