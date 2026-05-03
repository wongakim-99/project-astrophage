import * as THREE from 'three';

export const PURPLE_SCATTER = new THREE.Color('#9d7cff');
export const WHITE_CORE = new THREE.Color('#fff8e8');

export const starVertexShader = `
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

export const starFragmentShader = `
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

export const coronaVertexShader = `
  varying vec3 vNormal;
  varying vec3 vWorldPosition;

  void main() {
    vNormal = normalize(normalMatrix * normal);

    vec4 worldPosition = modelMatrix * vec4(position, 1.0);
    vWorldPosition = worldPosition.xyz;

    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }
`;

export const coronaFragmentShader = `
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
