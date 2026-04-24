
import { Canvas } from '@react-three/fiber';
import { MapControls, Stars } from '@react-three/drei';
import { useNavigate } from 'react-router';
import GalaxyCluster from '../components/three/GalaxyCluster';
import { useGalaxyStore } from '../stores/galaxyStore';

export default function UniversePage() {
  const galaxies = useGalaxyStore((state) => state.galaxies);
  const navigate = useNavigate();

  return (
    <div className="w-full h-full relative">
      <div className="absolute top-4 left-4 z-10 text-white pointer-events-none">
        <h1 className="text-2xl font-bold tracking-widest text-brand-active drop-shadow-[0_0_10px_rgba(168,216,255,0.5)]">UNIVERSE VIEW</h1>
        <p className="text-sm opacity-70">모든 지식의 은하단</p>
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
        
        <MapControls enableRotate={false} maxDistance={200} minDistance={20} />
      </Canvas>
    </div>
  );
}
