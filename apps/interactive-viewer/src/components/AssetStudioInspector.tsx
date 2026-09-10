import { Component, Suspense, useMemo, useEffect, useState, useRef, useCallback, type ReactNode } from 'react';
import * as THREE from 'three';
import { useFrame } from '@react-three/fiber';
import { Text, useGLTF } from '@react-three/drei';
import type { AssetRegistryItem } from '../data/assetRegistry';

export interface ModelBounds {
  center: [number, number, number];
  size: [number, number, number];
  radius: number;
}

export interface AssetStudioInspectorProps {
  asset: AssetRegistryItem;
  stateIndex: number;
  showSockets: boolean;
  showWireframe: boolean;
  showDimensions: boolean;
  lightingMode?: 'daylight' | 'studio' | 'darkroom';
  onModelBoundsMeasured?: (bounds: ModelBounds) => void;
}

interface ErrorBoundaryProps {
  fallback?: ReactNode;
  children: ReactNode;
}
interface ErrorBoundaryState {
  hasError: boolean;
}

class GLBErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = { hasError: false };
  static getDerivedStateFromError() {
    return { hasError: true };
  }
  componentDidCatch(error: any) {
    console.warn('GLB load error:', error);
  }
  render() {
    if (this.state.hasError) {
      return this.props.fallback || null;
    }
    return this.props.children;
  }
}

// 7 Rainbow Spectral Colors for Prism Dispersion (VIBGYOR)
const SPECTRUM_RAYS = [
  { name: 'Red', hex: '#ef4444', devDeg: 37.8, lambda: '700nm' },
  { name: 'Orange', hex: '#f97316', devDeg: 38.6, lambda: '620nm' },
  { name: 'Yellow', hex: '#eab308', devDeg: 39.4, lambda: '580nm' },
  { name: 'Green', hex: '#22c55e', devDeg: 40.3, lambda: '530nm' },
  { name: 'Blue', hex: '#3b82f6', devDeg: 41.2, lambda: '480nm' },
  { name: 'Indigo', hex: '#6366f1', devDeg: 42.0, lambda: '440nm' },
  { name: 'Violet', hex: '#a855f7', devDeg: 42.6, lambda: '400nm' },
];

/**
 * GLB Asset Renderer
 * Loads the actual Blender-exported GLB model, centers it at (0,0) horizontally,
 * grounds its lowest geometry point at Y = 0 on the studio floor, and computes
 * the live bounding dimensions.
 */
function GLBAssetRenderer({
  asset,
  stateIndex,
  showWireframe,
  onModelBoundsMeasured,
}: {
  asset: AssetRegistryItem;
  stateIndex: number;
  showWireframe: boolean;
  onModelBoundsMeasured?: (bounds: ModelBounds) => void;
}) {
  const { scene } = useGLTF(`/assets/${asset.id}.glb`);
  const flameRef = useRef<THREE.Group>(null);

  // Animate flame flicker in interactive states
  useFrame(({ clock }) => {
    const t = clock.getElapsedTime();
    if (flameRef.current) {
      const flicker = 1.0 + Math.sin(t * 18.0) * 0.08 + Math.cos(t * 26.0) * 0.05;
      flameRef.current.scale.set(flicker, flicker * 1.1, flicker);
    }
  });

  const { clonedScene, bounds } = useMemo(() => {
    const cloned = scene.clone(true);

    // Apply wireframe toggle and shadows
    cloned.traverse((child) => {
      if ((child as THREE.Mesh).isMesh) {
        const mesh = child as THREE.Mesh;
        mesh.castShadow = true;
        mesh.receiveShadow = true;
        if (mesh.material) {
          if (Array.isArray(mesh.material)) {
            mesh.material = mesh.material.map((m) => {
              const cloneMat = m.clone() as any;
              if ('wireframe' in cloneMat) cloneMat.wireframe = showWireframe;
              return cloneMat;
            });
          } else {
            const cloneMat = (mesh.material as THREE.Material).clone() as any;
            if ('wireframe' in cloneMat) cloneMat.wireframe = showWireframe;
            mesh.material = cloneMat;
          }
        }
      }
    });

    // Compute bounding box before offset
    const box = new THREE.Box3().setFromObject(cloned);
    const size = new THREE.Vector3();
    box.getSize(size);
    const center = new THREE.Vector3();
    box.getCenter(center);

    // Center on X and Z, and place base at Y = 0
    const offsetX = -center.x;
    const offsetY = -box.min.y;
    const offsetZ = -center.z;
    cloned.position.set(offsetX, offsetY, offsetZ);

    const radius = Math.max(size.x, size.y, size.z) / 2;

    const b: ModelBounds = {
      center: [0, size.y / 2, 0],
      size: [size.x, size.y, size.z],
      radius: Math.max(radius, 0.02),
    };

    console.log('[GLB RENDERER]', asset.id, 'computed bounds:', JSON.stringify(b));
    return { clonedScene: cloned, bounds: b };
  }, [scene, showWireframe, asset.id]);

  // Inform parent of measured bounds stably without re-render thrashing
  const onBoundsRef = useRef(onModelBoundsMeasured);
  onBoundsRef.current = onModelBoundsMeasured;

  useEffect(() => {
    if (onBoundsRef.current) {
      onBoundsRef.current(bounds);
    }
  }, [bounds.radius, bounds.size[0], bounds.size[1], bounds.size[2]]);

  return (
    <group>
      <primitive object={clonedScene} />

      {/* =================================================================== */}
      {/* INTERACTIVE STATE OVERLAYS FOR FLAGSHIP EXPERIMENTS                 */}
      {/* =================================================================== */}

      {/* 1. Glass Prism Refraction & Dispersion Beam Overlay */}
      {asset.id === 'glass-prism-refraction' && (
        <group position={[0, 0.035, 0]}>
          {/* Incident Collimated White Beam */}
          {stateIndex >= 1 && (
            <mesh position={[-0.08, 0, 0.035]} rotation={[0, 0.38, 0]}>
              <cylinderGeometry args={[0.0018, 0.0022, 0.12, 16]} />
              <meshStandardMaterial
                color="#ffffff"
                emissive="#ffffff"
                emissiveIntensity={4.0}
                toneMapped={false}
              />
            </mesh>
          )}

          {/* Internal Refraction Beams */}
          {stateIndex >= 2 && (
            <group>
              {SPECTRUM_RAYS.map((ray) => {
                const devRad = THREE.MathUtils.degToRad(30.0 - ray.devDeg);
                const dx = Math.cos(devRad) * 0.035;
                const dz = Math.sin(devRad) * 0.035;
                return (
                  <mesh key={ray.name} position={[-0.01 + dx / 2, 0, 0.015 - dz / 2]}>
                    <cylinderGeometry args={[0.0008, 0.0008, 0.035, 8]} />
                    <meshStandardMaterial
                      color={ray.hex}
                      emissive={ray.hex}
                      emissiveIntensity={3.0}
                      toneMapped={false}
                    />
                  </mesh>
                );
              })}
            </group>
          )}

          {/* Emergent VIBGYOR Rainbow Spectrum Fan */}
          {stateIndex >= 3 && (
            <group>
              {SPECTRUM_RAYS.map((ray, idx) => {
                const spreadAngle = (idx - 3) * 0.028 + 0.52;
                const len = 0.13;
                const px = Math.cos(spreadAngle) * (len / 2) + 0.025;
                const pz = -Math.sin(spreadAngle) * (len / 2) - 0.01;
                return (
                  <group key={ray.name} position={[px, 0, pz]} rotation={[0, spreadAngle, 0]}>
                    <mesh>
                      <cylinderGeometry args={[0.0012, 0.0016, len, 8]} />
                      <meshStandardMaterial
                        color={ray.hex}
                        emissive={ray.hex}
                        emissiveIntensity={4.5}
                        toneMapped={false}
                      />
                    </mesh>
                  </group>
                );
              })}
            </group>
          )}
        </group>
      )}

      {/* 2. Magnesium Burning Setup Reaction State Overlay */}
      {asset.id === 'magnesium-burning-setup' && (
        <group position={[0, 0.145, 0]}>
          {/* Heating Stage: Red-Orange Incandescent Tip */}
          {stateIndex === 1 && (
            <mesh position={[0, 0, 0]}>
              <sphereGeometry args={[0.006, 16, 16]} />
              <meshStandardMaterial
                color="#ff5500"
                emissive="#ff3300"
                emissiveIntensity={3.5}
                toneMapped={false}
              />
            </mesh>
          )}

          {/* Combustion Stage: Blinding Dazzling White Flame Emission */}
          {stateIndex === 2 && (
            <group ref={flameRef} position={[0, 0, 0]}>
              <mesh>
                <sphereGeometry args={[0.016, 24, 24]} />
                <meshStandardMaterial
                  color="#ffffff"
                  emissive="#ffffff"
                  emissiveIntensity={8.0}
                  toneMapped={false}
                />
              </mesh>
              <pointLight color="#ffffff" intensity={5.0} distance={0.5} />
            </group>
          )}
        </group>
      )}
    </group>
  );
}

/**
 * Main Asset Studio Inspector Viewport Component
 */
export function AssetStudioInspector({
  asset,
  stateIndex,
  showSockets,
  showWireframe,
  showDimensions,
  onModelBoundsMeasured,
}: AssetStudioInspectorProps) {
  const [currentBounds, setCurrentBounds] = useState<ModelBounds>({
    center: [0, 0.05, 0],
    size: [0.1, 0.1, 0.1],
    radius: 0.08,
  });

  const handleBoundsMeasured = useCallback((b: ModelBounds) => {
    setCurrentBounds((prev) => {
      if (
        prev &&
        Math.abs(prev.radius - b.radius) < 0.001 &&
        Math.abs(prev.size[0] - b.size[0]) < 0.001 &&
        Math.abs(prev.size[1] - b.size[1]) < 0.001 &&
        Math.abs(prev.size[2] - b.size[2]) < 0.001
      ) {
        return prev;
      }
      return b;
    });
    if (onModelBoundsMeasured) {
      onModelBoundsMeasured(b);
    }
  }, [onModelBoundsMeasured]);

  // Compute dynamic floor radius based on model dimensions
  const floorRadius = useMemo(() => {
    const horizontalExtent = Math.hypot(currentBounds.size[0] / 2, currentBounds.size[2] / 2);
    return Math.max(0.16, horizontalExtent * 1.45);
  }, [currentBounds]);

  return (
    <group position={[0, 0, 0]}>
      {/* ===================================================================== */}
      {/* 1. DYNAMIC ADAPTIVE STUDIO PEDESTAL (Grounded at Y = 0)               */}
      {/* ===================================================================== */}
      <group position={[0, 0, 0]}>
        {/* Heavy Circular Studio Base Pedestal */}
        <mesh receiveShadow position={[0, -0.006, 0]}>
          <cylinderGeometry args={[floorRadius, floorRadius * 1.04, 0.012, 64]} />
          <meshStandardMaterial color="#1e293b" roughness={0.7} metalness={0.25} />
        </mesh>

        {/* Polished Inset Turntable Top Disk */}
        <mesh receiveShadow position={[0, -0.0005, 0]}>
          <cylinderGeometry args={[floorRadius * 0.96, floorRadius * 0.96, 0.002, 64]} />
          <meshStandardMaterial color="#0b1120" roughness={0.4} metalness={0.15} />
        </mesh>

        {/* Studio Floor Grid */}
        <gridHelper
          args={[floorRadius * 2.0, 16, '#38bdf8', '#1e293b']}
          position={[0, 0.001, 0]}
        />

        {/* Measurement Rings on Floor */}
        <mesh receiveShadow position={[0, 0.0015, 0]} rotation={[-Math.PI / 2, 0, 0]}>
          <ringGeometry args={[floorRadius * 0.45, floorRadius * 0.455, 48]} />
          <meshBasicMaterial color="#38bdf8" transparent opacity={0.25} />
        </mesh>
        <mesh receiveShadow position={[0, 0.0015, 0]} rotation={[-Math.PI / 2, 0, 0]}>
          <ringGeometry args={[floorRadius * 0.85, floorRadius * 0.855, 48]} />
          <meshBasicMaterial color="#38bdf8" transparent opacity={0.2} />
        </mesh>

        {/* Cardinal Orientation Indicator Badges */}
        <Text
          position={[0, 0.002, floorRadius * 0.90]}
          rotation={[-Math.PI / 2, 0, 0]}
          fontSize={Math.max(0.007, floorRadius * 0.045)}
          color="#38bdf8"
          anchorX="center"
          anchorY="middle"
        >
          ▲ FRONT (VIEW)
        </Text>
        <Text
          position={[0, 0.002, -floorRadius * 0.90]}
          rotation={[-Math.PI / 2, 0, Math.PI]}
          fontSize={Math.max(0.006, floorRadius * 0.04)}
          color="#64748b"
          anchorX="center"
          anchorY="middle"
        >
          ▼ BACK
        </Text>
        <Text
          position={[-floorRadius * 0.90, 0.002, 0]}
          rotation={[-Math.PI / 2, 0, -Math.PI / 2]}
          fontSize={Math.max(0.006, floorRadius * 0.04)}
          color="#64748b"
          anchorX="center"
          anchorY="middle"
        >
          ◀ LEFT
        </Text>
        <Text
          position={[floorRadius * 0.90, 0.002, 0]}
          rotation={[-Math.PI / 2, 0, Math.PI / 2]}
          fontSize={Math.max(0.006, floorRadius * 0.04)}
          color="#64748b"
          anchorX="center"
          anchorY="middle"
        >
          RIGHT ▶
        </Text>
      </group>

      {/* ===================================================================== */}
      {/* 2. AUTHENTIC 3D GLB MODEL LOADER (For All 57 Assets)                   */}
      {/* ===================================================================== */}
      <GLBErrorBoundary key={asset.id}>
        <Suspense fallback={null}>
          <GLBAssetRenderer
            asset={asset}
            stateIndex={stateIndex}
            showWireframe={showWireframe}
            onModelBoundsMeasured={handleBoundsMeasured}
          />
        </Suspense>
      </GLBErrorBoundary>

      {/* ===================================================================== */}
      {/* 3. LIVE 3D BOUNDING BOX & SCALE DIMENSIONS OVERLAY                    */}
      {/* ===================================================================== */}
      {showDimensions && (
        <group position={[0, currentBounds.size[1] / 2, 0]}>
          <mesh>
            <boxGeometry
              args={[currentBounds.size[0], currentBounds.size[1], currentBounds.size[2]]}
            />
            <meshBasicMaterial color="#38bdf8" wireframe transparent opacity={0.3} />
          </mesh>
          <Text
            position={[
              0,
              -currentBounds.size[1] / 2 - 0.012 * (floorRadius / 0.2),
              currentBounds.size[2] / 2 + 0.008,
            ]}
            fontSize={Math.max(0.007, currentBounds.radius * 0.055)}
            color="#38bdf8"
            anchorX="center"
          >
            Width: {Math.round(currentBounds.size[0] * 1000)} mm
          </Text>
          <Text
            position={[
              -currentBounds.size[0] / 2 - 0.012 * (floorRadius / 0.2),
              0,
              0,
            ]}
            fontSize={Math.max(0.007, currentBounds.radius * 0.055)}
            color="#38bdf8"
            rotation={[0, -Math.PI / 2, 0]}
            anchorX="center"
          >
            Depth: {Math.round(currentBounds.size[2] * 1000)} mm
          </Text>
          <Text
            position={[
              currentBounds.size[0] / 2 + 0.012 * (floorRadius / 0.2),
              0,
              0,
            ]}
            fontSize={Math.max(0.007, currentBounds.radius * 0.055)}
            color="#38bdf8"
            rotation={[0, 0, -Math.PI / 2]}
            anchorX="center"
          >
            Height: {Math.round(currentBounds.size[1] * 1000)} mm
          </Text>
        </group>
      )}

      {/* ===================================================================== */}
      {/* 4. SNAP / ANCHOR SOCKET PINS                                          */}
      {/* ===================================================================== */}
      {showSockets && asset.anchorPoints && (
        <group>
          {Object.entries(asset.anchorPoints).map(([name, [sx, sy, sz]]) => (
            <group key={name} position={[sx, sz, -sy]}>
              <mesh>
                <sphereGeometry args={[Math.max(0.003, currentBounds.radius * 0.025), 16, 16]} />
                <meshStandardMaterial color="#38bdf8" emissive="#38bdf8" emissiveIntensity={3.0} />
              </mesh>
              <Text
                position={[0, Math.max(0.008, currentBounds.radius * 0.06), 0]}
                fontSize={Math.max(0.006, currentBounds.radius * 0.045)}
                color="#e0f2fe"
                anchorX="center"
                anchorY="bottom"
              >
                📍 {name}
              </Text>
            </group>
          ))}
        </group>
      )}
    </group>
  );
}
