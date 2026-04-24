import React from 'react';
import { useParams } from 'react-router';
import { Canvas } from '@react-three/fiber';
import { MapControls, Stars } from '@react-three/drei';

export default function GalaxyPage() {
  const { id } = useParams();

  return (
    <div className="w-full h-full relative">
      <div className="absolute top-4 left-4 z-10 text-white pointer-events-none">
        <h1 className="text-2xl font-bold tracking-widest">GALAXY VIEW</h1>
        <p className="text-sm opacity-70">은하 ID: {id}</p>
      </div>

      <Canvas camera={{ position: [0, 0, 50], fov: 60 }}>
        <color attach="background" args={['#050510']} />
        <ambientLight intensity={0.5} />
        <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />

        {/* TODO: Render StarMeshes for this galaxy here */}
        
        <MapControls enableRotate={false} maxDistance={100} minDistance={5} />
      </Canvas>
    </div>
  );
}
