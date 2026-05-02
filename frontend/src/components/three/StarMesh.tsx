import { useRef } from 'react';
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
  useFrame((_, delta) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += delta * 0.2;
    }
  });

  return (
    <mesh position={position} ref={meshRef} onClick={onClick}>
      <sphereGeometry args={[size, 32, 32]} />
      <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.5} />
      
      <Html distanceFactor={15} center>
        <div
          className="pointer-events-none select-none whitespace-nowrap"
          style={{
            fontSize: '9px',
            fontFamily: 'ui-monospace, "Cascadia Code", Consolas, monospace',
            color: 'rgba(200, 200, 220, 0.6)',
            textShadow: '0 1px 4px rgba(0,0,0,1), 0 0 12px rgba(0,0,0,0.9)',
            transform: 'translateY(14px)',
            letterSpacing: '0.04em',
          }}
        >
          {name}
        </div>
      </Html>
    </mesh>
  );
}
