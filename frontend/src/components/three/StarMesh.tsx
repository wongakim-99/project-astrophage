import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { Mesh } from 'three';
import { Html } from '@react-three/drei';

interface StarMeshProps {
  position: [number, number, number];
  color: string;
  size: number;
  name: string;
  onClick?: () => void;
}

export default function StarMesh({ position, color, size, name, onClick }: StarMeshProps) {
  const meshRef = useRef<Mesh>(null);

  // Simple idle animation (rotation)
  useFrame((state, delta) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += delta * 0.2;
    }
  });

  return (
    <mesh position={position} ref={meshRef} onClick={onClick}>
      <sphereGeometry args={[size, 32, 32]} />
      <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.5} />
      
      {/* Label that shows up next to star */}
      <Html distanceFactor={15} center>
        <div className="bg-black/50 backdrop-blur-sm px-2 py-1 rounded text-xs text-white pointer-events-none transform translate-y-4 shadow-lg border border-white/10 whitespace-nowrap">
          {name}
        </div>
      </Html>
    </mesh>
  );
}
