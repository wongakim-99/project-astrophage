import { useRef, useEffect } from 'react';
import { Canvas } from '@react-three/fiber';
import { MapControls, Stars } from '@react-three/drei';
import { EffectComposer, Bloom } from '@react-three/postprocessing';
import { useNavigate } from 'react-router';
import GalaxyCluster from '../components/three/GalaxyCluster';
import { useGalaxyStore } from '../stores/galaxyStore';

const PAN_LIMIT = 45;

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
        // enableRotate:false 환경에서 camera.xy == target.xy 불변식 유지
        // += dx 방식은 부동소수점 누적 오차가 spherical offset을 오염시켜 zoom에 간섭함
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
      maxDistance={260}
      minDistance={15}
    />
  );
}

export default function UniversePage() {
  const galaxies = useGalaxyStore((state) => state.galaxies);
  const navigate = useNavigate();

  return (
    <div className="w-full h-full relative">
      <div className="absolute top-4 left-4 z-10 pointer-events-none">
        <p className="text-[11px] font-mono text-white/20 tracking-[0.25em] uppercase">universe</p>
      </div>

      <Canvas camera={{ position: [0, 0, 80], fov: 60 }}>
        <color attach="background" args={['#050510']} />
        <ambientLight intensity={0.5} />
        <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />

        {galaxies.map((galaxy) => (
          <GalaxyCluster
            key={galaxy.id}
            position={galaxy.position}
            color={galaxy.color}
            name={galaxy.name}
            onClick={() => navigate(`/galaxy/${galaxy.id}`)}
          />
        ))}

        <CameraControls />

        <EffectComposer>
          <Bloom
            luminanceThreshold={0.15}
            luminanceSmoothing={0.9}
            intensity={1.5}
            mipmapBlur
          />
        </EffectComposer>
      </Canvas>
    </div>
  );
}
