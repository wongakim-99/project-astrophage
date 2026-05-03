import { useCallback, useEffect, useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { MapControls } from '@react-three/drei';
import * as THREE from 'three';
import type { MapControls as MapControlsImpl } from 'three-stdlib';

const DEFAULT_PAN_LIMIT = 50;
const RECENTER_DURATION = 1;
const RECENTER_CUE_EDGE = 38;
const AUTO_CENTER_DISTANCE = 74;

interface NavigationState {
  vignetteIntensity: number;
  showRecenterCue: boolean;
}

interface BoundedMapControlsProps {
  minDistance: number;
  maxDistance: number;
  onNavigationStateChange?: (state: NavigationState) => void;
  panLimit?: number;
}

interface RecenterState {
  elapsed: number;
  startCamera: THREE.Vector3;
  startTarget: THREE.Vector3;
  endCamera: THREE.Vector3;
  endTarget: THREE.Vector3;
}

const targetOrigin = new THREE.Vector3(0, 0, 0);

function isEditableTarget(target: EventTarget | null) {
  if (!(target instanceof HTMLElement)) return false;
  return target.isContentEditable || ['INPUT', 'TEXTAREA', 'SELECT'].includes(target.tagName);
}

export default function BoundedMapControls({
  minDistance,
  maxDistance,
  onNavigationStateChange,
  panLimit = DEFAULT_PAN_LIMIT,
}: BoundedMapControlsProps) {
  const controlsRef = useRef<MapControlsImpl>(null);
  const recenterRef = useRef<RecenterState | null>(null);
  const lastNavigationStateRef = useRef<NavigationState>({
    vignetteIntensity: -1,
    showRecenterCue: false,
  });

  const clampTarget = useCallback((controls: MapControlsImpl) => {
    const { target, object } = controls;
    const nextX = THREE.MathUtils.clamp(target.x, -panLimit, panLimit);
    const nextY = THREE.MathUtils.clamp(target.y, -panLimit, panLimit);
    const dx = nextX - target.x;
    const dy = nextY - target.y;

    if (dx !== 0 || dy !== 0) {
      target.x = nextX;
      target.y = nextY;
      object.position.x += dx;
      object.position.y += dy;
    }
  }, [panLimit]);

  const reportNavigationState = useCallback((target: THREE.Vector3) => {
    if (!onNavigationStateChange) return;

    const radialDistance = Math.hypot(target.x, target.y);
    const edgeDistance = Math.max(Math.abs(target.x), Math.abs(target.y));
    const vignetteIntensity = THREE.MathUtils.clamp((radialDistance - 16) / (panLimit - 16), 0, 1);
    const showRecenterCue = edgeDistance >= RECENTER_CUE_EDGE;
    const last = lastNavigationStateRef.current;

    if (
      Math.abs(last.vignetteIntensity - vignetteIntensity) > 0.015 ||
      last.showRecenterCue !== showRecenterCue
    ) {
      lastNavigationStateRef.current = { vignetteIntensity, showRecenterCue };
      onNavigationStateChange({ vignetteIntensity, showRecenterCue });
    }
  }, [onNavigationStateChange, panLimit]);

  const startAutoCenter = useCallback(() => {
    const controls = controlsRef.current;
    if (!controls) return;

    clampTarget(controls);

    const offset = controls.object.position.clone().sub(controls.target);
    recenterRef.current = {
      elapsed: 0,
      startCamera: controls.object.position.clone(),
      startTarget: controls.target.clone(),
      endCamera: targetOrigin.clone().add(offset),
      endTarget: targetOrigin.clone(),
    };
  }, [clampTarget]);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.code !== 'Space' || isEditableTarget(event.target)) return;
      event.preventDefault();
      startAutoCenter();
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [startAutoCenter]);

  useFrame((_, delta) => {
    const controls = controlsRef.current;
    if (!controls) return;

    const targetDistance = Math.hypot(controls.target.x, controls.target.y);
    const cameraDistance = Math.hypot(controls.object.position.x, controls.object.position.y);
    if (!recenterRef.current && Math.max(targetDistance, cameraDistance) > AUTO_CENTER_DISTANCE) {
      startAutoCenter();
    }

    if (recenterRef.current) {
      const state = recenterRef.current;
      state.elapsed = Math.min(state.elapsed + delta, RECENTER_DURATION);
      const t = state.elapsed / RECENTER_DURATION;
      const eased = t * t * (3 - 2 * t);

      controls.target.copy(state.startTarget).lerp(state.endTarget, eased);
      controls.object.position.copy(state.startCamera).lerp(state.endCamera, eased);

      if (state.elapsed >= RECENTER_DURATION) {
        recenterRef.current = null;
      }
    } else {
      clampTarget(controls);
    }

    reportNavigationState(controls.target);
  });

  return (
    <MapControls
      ref={controlsRef}
      makeDefault
      enableRotate={false}
      enableDamping
      dampingFactor={0.04}
      zoomSpeed={0.6}
      maxDistance={maxDistance}
      minDistance={minDistance}
    />
  );
}
