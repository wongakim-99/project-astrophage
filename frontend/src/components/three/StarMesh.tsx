import { useRef, useState, useMemo, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { Html } from '@react-three/drei';

const PARTICLE_COUNT = 14;

interface StarMeshProps {
  position: [number, number, number];
  color: string;
  size: number;
  name: string;
  onClick?: () => void;
}

function StarParticles({
  active,
  color,
  size,
}: {
  active: boolean;
  color: string;
  size: number;
}) {
  const geo = useMemo(() => {
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(PARTICLE_COUNT * 3), 3));
    return g;
  }, []);

  const velRef = useRef(
    Array.from({ length: PARTICLE_COUNT }, () => ({
      vx: (Math.random() - 0.5) * 0.06,
      vy: (Math.random() - 0.5) * 0.06,
      vz: (Math.random() - 0.5) * 0.02,
      life: Math.random(),
    }))
  );

  // 비활성화 시 파티클 위치 초기화
  useEffect(() => {
    if (!active) {
      const pos = geo.attributes.position as THREE.BufferAttribute;
      (pos.array as Float32Array).fill(0);
      pos.needsUpdate = true;
      velRef.current.forEach((v) => { v.life = Math.random(); });
    }
  }, [active, geo]);

  useFrame((_, delta) => {
    if (!active) return;
    const pos = geo.attributes.position as THREE.BufferAttribute;
    const arr = pos.array as Float32Array;

    velRef.current.forEach((v, i) => {
      v.life += delta * 1.5;
      if (v.life > 1) {
        // 수명 만료 → 원점에서 재발사
        v.life = 0;
        v.vx = (Math.random() - 0.5) * 0.06;
        v.vy = (Math.random() - 0.5) * 0.06;
        v.vz = (Math.random() - 0.5) * 0.02;
        arr[i * 3]     = 0;
        arr[i * 3 + 1] = 0;
        arr[i * 3 + 2] = 0;
      } else {
        arr[i * 3]     += v.vx * delta * 35;
        arr[i * 3 + 1] += v.vy * delta * 35;
        arr[i * 3 + 2] += v.vz * delta * 35;
      }
    });
    pos.needsUpdate = true;
  });

  return (
    <points geometry={geo} visible={active}>
      <pointsMaterial
        size={0.04 + size * 0.015}
        color={color}
        transparent
        opacity={0.8}
        sizeAttenuation
        depthWrite={false}
        blending={THREE.AdditiveBlending}
      />
    </points>
  );
}

export default function StarMesh({ position, color, size, name, onClick }: StarMeshProps) {
  const meshRef   = useRef<THREE.Mesh>(null);
  const matRef    = useRef<THREE.MeshStandardMaterial>(null);
  const [isHovered, setIsHovered] = useState(false);
  const flickerRef = useRef({ intensity: 0.5, t: 0 });

  useFrame((_, delta) => {
    const f = flickerRef.current;
    f.t += delta;

    if (meshRef.current) {
      meshRef.current.rotation.y += delta * 0.2;
    }

    if (matRef.current) {
      let target: number;
      if (isHovered) {
        // 비고조파 다중 주파수 → 불규칙 깜빡임
        const noise =
          0.5 * Math.sin(f.t * 17.3) +
          0.3 * Math.sin(f.t *  6.7 + 1.2) +
          0.2 * Math.sin(f.t * 38.1 + 2.4);
        target = 1.3 + noise * 0.65;
      } else {
        target = 0.5;
      }
      f.intensity = THREE.MathUtils.lerp(f.intensity, target, isHovered ? 0.25 : 0.08);
      matRef.current.emissiveIntensity = f.intensity;
    }
  });

  return (
    // group으로 감싸야 파티클이 mesh 회전과 독립적으로 world space에서 방출됨
    <group position={position}>
      <mesh
        ref={meshRef}
        onClick={onClick}
        onPointerOver={(e) => {
          e.stopPropagation();
          setIsHovered(true);
          document.body.style.cursor = 'pointer';
        }}
        onPointerOut={() => {
          setIsHovered(false);
          document.body.style.cursor = 'auto';
        }}
      >
        <sphereGeometry args={[size, 32, 32]} />
        <meshStandardMaterial
          ref={matRef}
          color={color}
          emissive={color}
          emissiveIntensity={0.5}
        />

        <Html distanceFactor={15} center>
          <div
            className="pointer-events-none select-none whitespace-nowrap"
            style={{
              fontSize: '9px',
              fontFamily: "'IBM Plex Mono', ui-monospace, monospace",
              color: isHovered ? 'rgba(220, 220, 245, 0.9)' : 'rgba(200, 200, 220, 0.55)',
              textShadow: isHovered
                ? '0 0 8px rgba(200, 200, 255, 0.5), 0 1px 4px rgba(0,0,0,1)'
                : '0 1px 4px rgba(0,0,0,1)',
              transform: 'translateY(14px)',
              letterSpacing: '0.14em',
              transition: 'color 0.15s, text-shadow 0.15s',
            }}
          >
            {name.toLowerCase()}
          </div>
        </Html>
      </mesh>

      <StarParticles active={isHovered} color={color} size={size} />
    </group>
  );
}
