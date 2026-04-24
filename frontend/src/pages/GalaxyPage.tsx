import { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router';
import { Canvas } from '@react-three/fiber';
import { MapControls, Stars } from '@react-three/drei';
import { ArrowLeft } from 'lucide-react';
import StarMesh from '../components/three/StarMesh';
import StarPanel from '../components/ui/StarPanel';
import { useStarStore } from '../stores/starStore';
import { useGalaxyStore } from '../stores/galaxyStore';

export default function GalaxyPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const galaxies = useGalaxyStore((state) => state.galaxies);
  const galaxy = galaxies.find(g => g.id === id);
  
  const stars = useStarStore((state) => state.stars);
  const selectStar = useStarStore((state) => state.selectStar);
  
  const galaxyStars = stars.filter(s => s.galaxyId === id);

  // Clear selected star when unmounting
  useEffect(() => {
    return () => selectStar(null);
  }, [selectStar]);

  return (
    <div className="w-full h-full relative overflow-hidden">
      {/* Header UI */}
      <div className="absolute top-4 left-4 z-10 text-white flex flex-col gap-2">
        <button 
          onClick={() => navigate('/universe')}
          className="flex items-center gap-2 text-sm text-foreground/70 hover:text-white transition-colors bg-white/5 hover:bg-white/10 px-3 py-1.5 rounded-full backdrop-blur-md w-fit border border-white/10"
        >
          <ArrowLeft size={16} />
          <span>Back to Universe</span>
        </button>
        <div className="pointer-events-none mt-2">
          <h1 className="text-3xl font-bold tracking-widest drop-shadow-lg" style={{ color: galaxy?.color || '#fff' }}>
            {galaxy?.name || 'UNKNOWN GALAXY'}
          </h1>
          <p className="text-sm opacity-70">{galaxyStars.length} stars discovered</p>
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
        
        <MapControls enableRotate={false} maxDistance={100} minDistance={5} />
      </Canvas>

      {/* Side Panel */}
      <StarPanel />
    </div>
  );
}
