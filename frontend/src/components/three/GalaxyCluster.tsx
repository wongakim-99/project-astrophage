import { useMemo, useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { Html } from '@react-three/drei';
import * as THREE from 'three';

interface GalaxyClusterProps {
  position: [number, number, number];
  color: string;
  name: string;
  onClick?: () => void;
}

function gaussianRandom(mean = 0, std = 1): number {
  const u = 1 - Math.random();
  const v = Math.random();
  return mean + std * Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
}

export default function GalaxyCluster({ position, color, name, onClick }: GalaxyClusterProps) {
  const discRef = useRef<THREE.Group>(null);

  const { armPos, armCol, corePos, coreCol } = useMemo(() => {
    const ARM_N    = 1600;
    const CORE_N   = 350;
    const N_ARMS   = 2;
    const MAX_R    = 9;
    const WIND     = 4.0; // 나선팔이 감기는 각도 (라디안)

    const armPos  = new Float32Array(ARM_N  * 3);
    const armCol  = new Float32Array(ARM_N  * 3);
    const corePos = new Float32Array(CORE_N * 3);
    const coreCol = new Float32Array(CORE_N * 3);

    const themeCol = new THREE.Color(color);
    const warmWhite = new THREE.Color('#fff6e0');  // 핵부 따뜻한 흰빛

    // ── 나선팔 파티클 ──────────────────────────────────
    for (let i = 0; i < ARM_N; i++) {
      const arm = i % N_ARMS;
      const t   = Math.random();                        // 0=핵 ~ 1=외곽

      const r           = Math.pow(t, 0.55) * MAX_R;   // 내부가 더 밀집
      const baseAngle   = (arm / N_ARMS) * Math.PI * 2;
      const spiralAngle = baseAngle + t * WIND;

      // 팔 폭 — 외곽으로 갈수록 넓어짐
      const angleNoise  = gaussianRandom(0, 0.18 + t * 0.35);
      const radialNoise = gaussianRandom(0, 0.3 + t * 0.5);
      const finalAngle  = spiralAngle + angleNoise;
      const finalR      = r + radialNoise;

      armPos[i * 3]     = Math.cos(finalAngle) * finalR;
      armPos[i * 3 + 1] = Math.sin(finalAngle) * finalR;
      armPos[i * 3 + 2] = gaussianRandom(0, 0.10 + t * 0.08);

      // 색상: 핵 근처=따뜻한 흰빛 → 팔=테마 색상
      const distNorm = Math.min(finalR / MAX_R, 1);
      const fc       = warmWhite.clone().lerp(themeCol, Math.min(distNorm * 1.8, 1));
      const bright   = 0.35 + (1 - distNorm) * 0.65;

      armCol[i * 3]     = fc.r * bright;
      armCol[i * 3 + 1] = fc.g * bright;
      armCol[i * 3 + 2] = fc.b * bright;
    }

    // ── 중심핵 파티클 (밀집·밝음) ─────────────────────
    for (let i = 0; i < CORE_N; i++) {
      const r     = Math.abs(gaussianRandom(0, 1.4));
      const angle = Math.random() * Math.PI * 2;

      corePos[i * 3]     = Math.cos(angle) * r;
      corePos[i * 3 + 1] = Math.sin(angle) * r;
      corePos[i * 3 + 2] = gaussianRandom(0, 0.05);

      const bright       = 0.85 + Math.random() * 0.15;
      coreCol[i * 3]     = warmWhite.r * bright;
      coreCol[i * 3 + 1] = warmWhite.g * bright;
      coreCol[i * 3 + 2] = warmWhite.b * bright;
    }

    return { armPos, armCol, corePos, coreCol };
  }, [color]);

  // 아주 느린 자전 — 실제 은하 자전 느낌
  useFrame((_, delta) => {
    if (discRef.current) discRef.current.rotation.z += delta * 0.007;
  });

  return (
    <group position={position}>
      {/* 기울어진 은하 원반: x축 틸트 + y 스케일 압축으로 타원형 원근감 */}
      <group ref={discRef} rotation={[0.45, 0.08, 0]} scale={[1, 0.52, 1]}>
        {/* 나선팔 */}
        <points>
          <bufferGeometry>
            <bufferAttribute attach="attributes-position" array={armPos}  count={armPos.length  / 3} itemSize={3} />
            <bufferAttribute attach="attributes-color"    array={armCol}  count={armCol.length  / 3} itemSize={3} />
          </bufferGeometry>
          <pointsMaterial size={0.16} vertexColors transparent opacity={0.88} sizeAttenuation depthWrite={false} />
        </points>

        {/* 핵 — 더 크고 밝은 파티클 */}
        <points>
          <bufferGeometry>
            <bufferAttribute attach="attributes-position" array={corePos} count={corePos.length / 3} itemSize={3} />
            <bufferAttribute attach="attributes-color"    array={coreCol} count={coreCol.length / 3} itemSize={3} />
          </bufferGeometry>
          <pointsMaterial size={0.32} vertexColors transparent opacity={0.95} sizeAttenuation depthWrite={false} />
        </points>
      </group>

      {/* 발광 핵 구체 — Bloom 글로우의 광원 */}
      <mesh>
        <sphereGeometry args={[0.75, 16, 16]} />
        <meshBasicMaterial color="#fff6e0" />
      </mesh>

      {/* 투명 클릭 히트박스 */}
      <mesh onClick={onClick}>
        <sphereGeometry args={[10, 8, 8]} />
        <meshBasicMaterial transparent opacity={0} depthWrite={false} />
      </mesh>

      {/* 은하 이름 */}
      <Html distanceFactor={55} center position={[0, -10, 0]}>
        <div
          className="text-xs font-mono tracking-widest pointer-events-none whitespace-nowrap"
          style={{ color, textShadow: `0 0 8px ${color}` }}
        >
          {name}
        </div>
      </Html>
    </group>
  );
}
