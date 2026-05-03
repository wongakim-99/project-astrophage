import { useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { Stars } from '@react-three/drei';
import { EffectComposer, Bloom } from '@react-three/postprocessing';
import { useNavigate } from 'react-router';
import BoundedMapControls from '../components/three/BoundedMapControls';
import GalaxyCluster from '../components/three/GalaxyCluster';
import { useGalaxies } from '../hooks/useGalaxies';
import { galaxyPosition } from '../stores/galaxyStore';

export default function UniversePage() {
  const { data: galaxies = [], isLoading } = useGalaxies();
  const navigate = useNavigate();
  const [navigationState, setNavigationState] = useState({
    vignetteIntensity: 0,
    showRecenterCue: false,
  });

  const vignetteEdge = 0.48 + navigationState.vignetteIntensity * 0.28;

  return (
    <div className="w-full h-full relative">
      <div className="absolute top-4 left-4 z-20 pointer-events-none">
        <p className="text-[11px] font-mono text-white/20 tracking-[0.25em] uppercase">universe</p>
        {isLoading && (
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
    </div>
  );
}
