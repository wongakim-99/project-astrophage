import { useRef, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router';
import { Canvas } from '@react-three/fiber';
import { MapControls, Stars } from '@react-three/drei';
import { EffectComposer, Bloom } from '@react-three/postprocessing';
import { ArrowLeft } from 'lucide-react';
import StarMesh from '../components/three/StarMesh';
import StarPanel from '../components/ui/StarPanel';
import { useStarStore } from '../stores/starStore';
import { useGalaxyStore } from '../stores/galaxyStore';

const PAN_LIMIT = 25;

function CameraControls() {
  const ref = useRef<any>(null);

  useEffect(() => {
    const c = ref.current;
    if (!c) return;

    const clamp = () => {
      const nx = Math.max(-PAN_LIMIT, Math.min(PAN_LIMIT, c.target.x));
      const ny = Math.max(-PAN_LIMIT, Math.min(PAN_LIMIT, c.target.y));
      if (nx !== c.target.x || ny !== c.target.y) {
        c.target.x = nx;
        c.target.y = ny;
        c.object.position.x = nx;
        c.object.position.y = ny;
      }
    };

    c.addEventListener('change', clamp);
    return () => c.removeEventListener('change', clamp);
  }, []);

  return (
    <MapControls
      ref={ref}
      makeDefault
      enableRotate={false}
      enableDamping
      dampingFactor={0.04}
      zoomSpeed={0.6}
      maxDistance={130}
      minDistance={3}
    />
  );
}

export default function GalaxyPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const galaxies = useGalaxyStore((state) => state.galaxies);
  const galaxy = galaxies.find(g => g.id === id);

  const stars = useStarStore((state) => state.stars);
  const selectStar = useStarStore((state) => state.selectStar);

  const galaxyStars = stars.filter(s => s.galaxyId === id);

  useEffect(() => {
    return () => selectStar(null);
  }, [selectStar]);

  return (
    <div className="w-full h-full relative overflow-hidden">
      <div className="absolute top-4 left-4 z-10 flex flex-col gap-2">
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

        <CameraControls />

        <EffectComposer>
          <Bloom
            luminanceThreshold={0.15}
            luminanceSmoothing={0.9}
            intensity={1.2}
            mipmapBlur
          />
        </EffectComposer>
      </Canvas>

      <StarPanel />
    </div>
  );
}
