import { useRef, useState, useMemo, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { Html } from '@react-three/drei';

const PARTICLE_COUNT = 14;
const STAR_SCALE = 0.7;
const PURPLE_SCATTER = new THREE.Color('#9d7cff');
const WHITE_CORE = new THREE.Color('#fff8e8');

const starVertexShader = `
  varying vec2 vUv;
  varying vec3 vNormal;
  varying vec3 vWorldPosition;

  void main() {
    vUv = uv;
    vNormal = normalize(normalMatrix * normal);

    vec4 worldPosition = modelMatrix * vec4(position, 1.0);
    vWorldPosition = worldPosition.xyz;

    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }
`;

const starFragmentShader = `
  uniform float uTime;
  uniform float uHoverIntensity;
  uniform vec3 uBaseColor;
  uniform vec3 uCoreColor;
  uniform vec3 uScatterColor;

  varying vec2 vUv;
  varying vec3 vNormal;
  varying vec3 vWorldPosition;

  float hash(vec3 p) {
    p = fract(p * 0.3183099 + vec3(0.1, 0.2, 0.3));
    p *= 17.0;
    return fract(p.x * p.y * p.z * (p.x + p.y + p.z));
  }

  float noise(vec3 x) {
    vec3 i = floor(x);
    vec3 f = fract(x);
    f = f * f * (3.0 - 2.0 * f);

    return mix(
      mix(
        mix(hash(i + vec3(0.0, 0.0, 0.0)), hash(i + vec3(1.0, 0.0, 0.0)), f.x),
        mix(hash(i + vec3(0.0, 1.0, 0.0)), hash(i + vec3(1.0, 1.0, 0.0)), f.x),
        f.y
      ),
      mix(
        mix(hash(i + vec3(0.0, 0.0, 1.0)), hash(i + vec3(1.0, 0.0, 1.0)), f.x),
        mix(hash(i + vec3(0.0, 1.0, 1.0)), hash(i + vec3(1.0, 1.0, 1.0)), f.x),
        f.y
      ),
      f.z
    );
  }

  float fbm(vec3 p) {
    float value = 0.0;
    float amplitude = 0.55;

    for (int i = 0; i < 5; i++) {
      value += amplitude * noise(p);
      p *= 2.02;
      amplitude *= 0.52;
    }

    return value;
  }

  void main() {
    vec3 viewDirection = normalize(cameraPosition - vWorldPosition);
    float fresnel = pow(1.0 - max(dot(normalize(vNormal), viewDirection), 0.0), 2.35);

    vec3 flow = vec3(vUv * 4.0, 0.0);
    float slowTime = uTime * 0.08;
    float plasma = fbm(flow + vec3(slowTime, -slowTime * 0.7, slowTime * 1.4));
    float ember = fbm(flow * 1.9 + vec3(-slowTime * 1.8, slowTime, slowTime * 0.4));

    float hotCore = smoothstep(0.48, 0.92, plasma + ember * 0.45);
    vec3 surface = mix(uScatterColor, uBaseColor, 0.68 + ember * 0.24);
    surface = mix(surface, uCoreColor, hotCore * 0.72);
    surface += uScatterColor * fresnel * 1.55;
    surface += uCoreColor * pow(fresnel, 4.0) * 0.85;

    float pulse = 1.0 + sin(uTime * 0.9 + plasma * 5.0) * 0.045;
    float energy = 1.12 + uHoverIntensity * 0.32 + hotCore * 0.34 + fresnel * 0.65;

    gl_FragColor = vec4(surface * energy * pulse, 1.0);
  }
`;

const coronaVertexShader = `
  varying vec3 vNormal;
  varying vec3 vWorldPosition;

  void main() {
    vNormal = normalize(normalMatrix * normal);

    vec4 worldPosition = modelMatrix * vec4(position, 1.0);
    vWorldPosition = worldPosition.xyz;

    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }
`;

const coronaFragmentShader = `
  uniform float uTime;
  uniform float uHoverIntensity;
  uniform vec3 uBaseColor;
  uniform vec3 uScatterColor;

  varying vec3 vNormal;
  varying vec3 vWorldPosition;

  void main() {
    vec3 viewDirection = normalize(cameraPosition - vWorldPosition);
    float fresnel = pow(1.0 - max(dot(normalize(vNormal), viewDirection), 0.0), 2.0);
    float pulse = 0.72 + sin(uTime * 0.65) * 0.08 + uHoverIntensity * 0.08;

    vec3 corona = mix(uBaseColor, uScatterColor, 0.58) * (0.8 + fresnel * 1.7);
    float alpha = smoothstep(0.05, 1.0, fresnel) * pulse * 0.34;

    gl_FragColor = vec4(corona, alpha);
  }
`;

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
  const meshRef = useRef<THREE.Mesh>(null);
  const leaderRef = useRef<THREE.Line>(null);
  const surfaceMatRef = useRef<THREE.ShaderMaterial>(null);
  const coronaMatRef = useRef<THREE.ShaderMaterial>(null);
  const [isHovered, setIsHovered] = useState(false);
  const flickerRef = useRef({ intensity: 0, t: 0 });
  const visualSize = size * STAR_SCALE;
  const labelPosition = useMemo(
    () => new THREE.Vector3(visualSize * 2.2, visualSize * 1.42, 0),
    [visualSize]
  );
  const leaderLine = useMemo(() => {
    const start = new THREE.Vector3(visualSize * 0.72, visualSize * 0.5, 0);
    const end = new THREE.Vector3(labelPosition.x - visualSize * 0.18, labelPosition.y - visualSize * 0.1, 0);
    const geometry = new THREE.BufferGeometry().setFromPoints([start, end]);
    const material = new THREE.LineDashedMaterial({
      color,
      transparent: true,
      opacity: 0.26,
      dashSize: 0.06,
      gapSize: 0.06,
      depthWrite: false,
    });
    const line = new THREE.Line(geometry, material);
    line.computeLineDistances();
    return line;
  }, [color, labelPosition, visualSize]);
  const baseColor = useMemo(() => new THREE.Color(color), [color]);
  const starUniforms = useMemo(() => ({
    uTime: { value: 0 },
    uHoverIntensity: { value: 0 },
    uBaseColor: { value: baseColor },
    uCoreColor: { value: WHITE_CORE },
    uScatterColor: { value: PURPLE_SCATTER },
  }), [baseColor]);
  const coronaUniforms = useMemo(() => ({
    uTime: { value: 0 },
    uHoverIntensity: { value: 0 },
    uBaseColor: { value: baseColor },
    uScatterColor: { value: PURPLE_SCATTER },
  }), [baseColor]);

  useEffect(() => {
    return () => {
      leaderLine.geometry.dispose();
      if (Array.isArray(leaderLine.material)) {
        leaderLine.material.forEach((material) => material.dispose());
      } else {
        leaderLine.material.dispose();
      }
    };
  }, [leaderLine]);

  useFrame((_, delta) => {
    const f = flickerRef.current;
    f.t += delta;

    if (meshRef.current) {
      meshRef.current.rotation.y += delta * 0.2;
    }

    const target = isHovered ? 1 : 0;
    f.intensity = THREE.MathUtils.lerp(f.intensity, target, isHovered ? 0.18 : 0.08);

    if (surfaceMatRef.current) {
      surfaceMatRef.current.uniforms.uTime.value = f.t;
      surfaceMatRef.current.uniforms.uHoverIntensity.value = f.intensity;
    }

    if (coronaMatRef.current) {
      coronaMatRef.current.uniforms.uTime.value = f.t;
      coronaMatRef.current.uniforms.uHoverIntensity.value = f.intensity;
    }

    if (leaderRef.current) {
      const material = leaderRef.current.material;
      if (!Array.isArray(material)) {
        material.opacity = THREE.MathUtils.lerp(material.opacity, isHovered ? 0.5 : 0.26, 0.18);
      }
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
        <sphereGeometry args={[visualSize, 64, 64]} />
        <shaderMaterial
          ref={surfaceMatRef}
          uniforms={starUniforms}
          vertexShader={starVertexShader}
          fragmentShader={starFragmentShader}
        />
      </mesh>

      <mesh scale={1.9}>
        <sphereGeometry args={[visualSize, 48, 48]} />
        <shaderMaterial
          ref={coronaMatRef}
          uniforms={coronaUniforms}
          vertexShader={coronaVertexShader}
          fragmentShader={coronaFragmentShader}
          transparent
          depthWrite={false}
          blending={THREE.AdditiveBlending}
          side={THREE.BackSide}
        />
      </mesh>

      <primitive ref={leaderRef} object={leaderLine} />

      <Html distanceFactor={15} center position={labelPosition}>
        <div
          className="pointer-events-none select-none whitespace-nowrap"
          style={{
            fontSize: '8px',
            fontFamily: "'IBM Plex Mono', ui-monospace, monospace",
            color: isHovered ? 'rgba(235, 235, 255, 0.92)' : 'rgba(210, 210, 230, 0.58)',
            textShadow: isHovered
              ? `0 0 10px ${color}, 0 1px 4px rgba(0,0,0,1)`
              : '0 1px 4px rgba(0,0,0,1)',
            letterSpacing: '0.16em',
            lineHeight: 1,
            padding: '3px 5px',
            borderLeft: `1px solid ${isHovered ? color : 'rgba(220,220,245,0.24)'}`,
            background: 'rgba(5, 5, 16, 0.24)',
            transition: 'color 0.15s, text-shadow 0.15s, border-color 0.15s',
          }}
        >
          {name.toLowerCase()}
        </div>
      </Html>

      <StarParticles active={isHovered} color={color} size={visualSize} />
    </group>
  );
}
