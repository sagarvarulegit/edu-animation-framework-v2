import { useMemo, useRef } from 'react';
import * as THREE from 'three';
import { useFrame } from '@react-three/fiber';
import { Text } from '@react-three/drei';
import type { AssetRegistryItem } from '../data/assetRegistry';
import { BohrAtomModel } from './BohrAtomModel';
import { IonicReaction3DModel } from './IonicReaction3DModel';

export interface AssetStudioInspectorProps {
  asset: AssetRegistryItem;
  stateIndex: number;
  showSockets: boolean;
  showWireframe: boolean;
  showDimensions: boolean;
  lightingMode: 'daylight' | 'studio' | 'darkroom';
}

export function AssetStudioInspector({
  asset,
  stateIndex,
  showSockets,
  showWireframe,
  showDimensions,
  lightingMode: _lightingMode,
}: AssetStudioInspectorProps) {
  const modelGroupRef = useRef<THREE.Group>(null);
  const heartParticlesRef = useRef<THREE.Group>(null);

  // Subtle rotation for preview inspection
  useFrame((_, delta) => {
    if (heartParticlesRef.current) {
      heartParticlesRef.current.rotation.z += delta * 0.5;
    }
  });

  // Equilateral Prism Triangle Shape (Side = 0.08m, Height = 0.06m)
  const prismShape = useMemo(() => {
    const s = new THREE.Shape();
    const side = 0.08;
    const h = (Math.sqrt(3) / 2) * side;
    s.moveTo(-side / 2, -h / 3);
    s.lineTo(side / 2, -h / 3);
    s.lineTo(0, (2 * h) / 3);
    s.closePath();
    return s;
  }, []);

  // 7 Rainbow Spectral Colors (VIBGYOR)
  const spectrumRays = [
    { name: 'Red', hex: '#ef4444', devDeg: 37.8, lambda: '700nm' },
    { name: 'Orange', hex: '#f97316', devDeg: 38.6, lambda: '620nm' },
    { name: 'Yellow', hex: '#eab308', devDeg: 39.4, lambda: '580nm' },
    { name: 'Green', hex: '#22c55e', devDeg: 40.3, lambda: '530nm' },
    { name: 'Blue', hex: '#3b82f6', devDeg: 41.2, lambda: '480nm' },
    { name: 'Indigo', hex: '#6366f1', devDeg: 42.0, lambda: '440nm' },
    { name: 'Violet', hex: '#a855f7', devDeg: 42.6, lambda: '400nm' },
  ];

  return (
    <group ref={modelGroupRef} position={[0, 0, 0]}>
      {/* ===================================================================== */}
      {/* 0. STUDIO LABORATORY FLOOR / PEDESTAL PLATFORM                         */}
      {/* ===================================================================== */}
      <group position={[0, 0, -0.022]}>
        {/* Heavy Circular Studio Base Pedestal */}
        <mesh receiveShadow position={[0, 0, -0.006]}>
          <cylinderGeometry args={[0.34, 0.36, 0.012, 64]} />
          <meshStandardMaterial color="#1e293b" roughness={0.65} metalness={0.25} />
        </mesh>

        {/* Polished Inset Turntable Top with subtle bevel */}
        <mesh receiveShadow position={[0, 0, 0.0005]}>
          <cylinderGeometry args={[0.33, 0.33, 0.002, 64]} />
          <meshStandardMaterial color="#0f172a" roughness={0.5} metalness={0.1} />
        </mesh>

        {/* Radial Measurement Rings on Floor */}
        <mesh receiveShadow position={[0, 0, 0.002]}>
          <ringGeometry args={[0.08, 0.082, 48]} />
          <meshBasicMaterial color="#38bdf8" transparent opacity={0.3} />
        </mesh>
        <mesh receiveShadow position={[0, 0, 0.002]}>
          <ringGeometry args={[0.16, 0.162, 48]} />
          <meshBasicMaterial color="#38bdf8" transparent opacity={0.25} />
        </mesh>
        <mesh receiveShadow position={[0, 0, 0.002]}>
          <ringGeometry args={[0.24, 0.242, 48]} />
          <meshBasicMaterial color="#38bdf8" transparent opacity={0.2} />
        </mesh>

        {/* Studio Floor Grid */}
        <gridHelper
          args={[0.64, 16, '#38bdf8', '#1e293b']}
          position={[0, 0, 0.003]}
          rotation={[Math.PI / 2, 0, 0]}
        />

        {/* Cardinal Orientation Indicator Badges */}
        <Text position={[0, -0.28, 0.005]} fontSize={0.012} color="#38bdf8" anchorX="center" anchorY="middle">
          ▲ FRONT (VIEW)
        </Text>
        <Text position={[0, 0.28, 0.005]} fontSize={0.010} color="#64748b" anchorX="center" anchorY="middle">
          ▼ BACK
        </Text>
        <Text position={[-0.28, 0, 0.005]} fontSize={0.010} color="#64748b" anchorX="center" anchorY="middle">
          ◀ LEFT
        </Text>
        <Text position={[0.28, 0, 0.005]} fontSize={0.010} color="#64748b" anchorX="center" anchorY="middle">
          RIGHT ▶
        </Text>
      </group>

      {/* ===================================================================== */}
      {/* 1. 3D APPARATUS GEOMETRIES BY ASSET ID                                */}
      {/* ===================================================================== */}

      {/* --- ASSET: glass-prism-refraction --- */}
      {asset.id === 'glass-prism-refraction' && (
        <group position={[0, 0, 0]}>
          {/* Beechwood Drawing Board */}
          <mesh position={[0, 0, -0.012]} receiveShadow castShadow>
            <boxGeometry args={[0.34, 0.26, 0.018]} />
            <meshStandardMaterial
              color="#d97706"
              roughness={0.45}
              metalness={0.05}
              wireframe={showWireframe}
            />
          </mesh>

          {/* Pinned White Drawing Sheet */}
          <mesh position={[0, 0, -0.002]} receiveShadow>
            <boxGeometry args={[0.30, 0.22, 0.002]} />
            <meshStandardMaterial
              color="#fdfbf7"
              roughness={0.9}
              wireframe={showWireframe}
            />
          </mesh>

          {/* Triangular Glass Prism (Schott N-BK7 Crown Glass) */}
          <mesh position={[0, 0, 0.0]} castShadow receiveShadow>
            <extrudeGeometry
              args={[
                prismShape,
                {
                  depth: 0.06,
                  bevelEnabled: true,
                  bevelSegments: 3,
                  steps: 1,
                  bevelSize: 0.0015,
                  bevelThickness: 0.0015,
                },
              ]}
            />
            <meshPhysicalMaterial
              color="#e0f2fe"
              transmission={showWireframe ? 0 : 0.96}
              opacity={1.0}
              transparent
              roughness={showWireframe ? 1 : 0.015}
              ior={1.517}
              thickness={0.08}
              specularIntensity={1.0}
              clearcoat={1.0}
              attenuationColor={new THREE.Color('#e0f2fe')}
              wireframe={showWireframe}
            />
          </mesh>

          {/* White Light Torch on Stand */}
          <group position={[-0.14, -0.045, 0.03]} rotation={[0, 0, THREE.MathUtils.degToRad(18)]}>
            <mesh position={[-0.035, 0, 0]} rotation={[0, Math.PI / 2, 0]} castShadow>
              <cylinderGeometry args={[0.009, 0.012, 0.065, 20]} />
              <meshStandardMaterial color="#1e293b" metalness={0.85} roughness={0.25} wireframe={showWireframe} />
            </mesh>
            <mesh position={[0.008, 0, 0]} rotation={[0, Math.PI / 2, 0]}>
              <cylinderGeometry args={[0.012, 0.012, 0.004, 20]} />
              <meshStandardMaterial
                color="#ffffff"
                emissive={stateIndex >= 1 ? '#ffffff' : '#000000'}
                emissiveIntensity={stateIndex >= 1 ? 3.5 : 0}
              />
            </mesh>

            {/* Incident White Beam (State >= 1) */}
            {stateIndex >= 1 && (
              <mesh position={[0.065, 0, 0]} rotation={[0, 0, Math.PI / 2]}>
                <cylinderGeometry args={[0.0022, 0.0028, 0.11, 16]} />
                <meshStandardMaterial color="#ffffff" emissive="#ffffff" emissiveIntensity={3.0} />
              </mesh>
            )}
          </group>

          {/* Internal Refraction Paths (State >= 2) */}
          {stateIndex >= 2 && (
            <group>
              {spectrumRays.map((ray, idx) => {
                const devAngle = THREE.MathUtils.degToRad(30.0 - ray.devDeg);
                const dX = Math.cos(devAngle) * 0.045;
                const dY = Math.sin(devAngle) * 0.045;
                return (
                  <mesh key={idx} position={[-0.02 + dX / 2, -0.01 + dY / 2, 0.03]} rotation={[0, 0, devAngle * 0.4]}>
                    <cylinderGeometry args={[0.0011, 0.0011, 0.045, 12]} />
                    <meshStandardMaterial
                      color={stateIndex === 2 ? '#fbbf24' : ray.hex}
                      emissive={stateIndex === 2 ? '#f59e0b' : ray.hex}
                      emissiveIntensity={2.5}
                    />
                  </mesh>
                );
              })}
            </group>
          )}

          {/* 7 Rainbow Emergent Rays & Screen (State 3) */}
          {stateIndex >= 3 && (
            <group>
              {spectrumRays.map((ray, idx) => {
                const devAngle = THREE.MathUtils.degToRad(30.0 - ray.devDeg);
                const dX = Math.cos(devAngle) * 0.11;
                const dY = Math.sin(devAngle) * 0.11;
                return (
                  <group key={idx}>
                    <mesh position={[0.025 + dX / 2, -0.01 + dY / 2, 0.03]} rotation={[0, 0, devAngle]}>
                      <cylinderGeometry args={[0.0013, 0.0016, 0.11, 14]} />
                      <meshStandardMaterial color={ray.hex} emissive={ray.hex} emissiveIntensity={3.2} />
                    </mesh>
                    <mesh position={[0.025 + dX, -0.01 + dY, 0.03]}>
                      <boxGeometry args={[0.002, 0.006, 0.008]} />
                      <meshStandardMaterial color={ray.hex} emissive={ray.hex} emissiveIntensity={3.5} />
                    </mesh>
                    <Text position={[0.035 + dX, -0.01 + dY, 0.04]} fontSize={0.0065} color={ray.hex} anchorX="left">
                      {ray.name} ({ray.lambda})
                    </Text>
                  </group>
                );
              })}
              {/* White Observation Screen */}
              <mesh position={[0.145, -0.045, 0.038]} rotation={[0, 0, THREE.MathUtils.degToRad(70)]} receiveShadow>
                <boxGeometry args={[0.006, 0.095, 0.075]} />
                <meshStandardMaterial color="#ffffff" roughness={0.85} wireframe={showWireframe} />
              </mesh>
            </group>
          )}
        </group>
      )}

      {/* --- ASSET: glass-prism (Standalone) --- */}
      {asset.id === 'glass-prism' && (
        <group position={[0, 0, -0.02]}>
          <mesh castShadow receiveShadow>
            <extrudeGeometry
              args={[
                prismShape,
                {
                  depth: 0.07,
                  bevelEnabled: true,
                  bevelSegments: 3,
                  steps: 1,
                  bevelSize: 0.002,
                  bevelThickness: 0.002,
                },
              ]}
            />
            <meshPhysicalMaterial
              color="#e0f2fe"
              transmission={showWireframe ? 0 : 0.98}
              roughness={showWireframe ? 1 : 0.01}
              ior={1.517}
              thickness={0.09}
              specularIntensity={1.0}
              clearcoat={1.0}
              wireframe={showWireframe}
            />
          </mesh>
        </group>
      )}

      {/* --- ASSET: convex-lens --- */}
      {asset.id === 'convex-lens' && (
        <group position={[0, 0, 0]}>
          {/* Base Stand */}
          <mesh position={[0, 0, 0.008]} castShadow>
            <cylinderGeometry args={[0.035, 0.04, 0.016, 24]} />
            <meshStandardMaterial color="#334155" metalness={0.8} roughness={0.3} wireframe={showWireframe} />
          </mesh>
          <mesh position={[0, 0, 0.045]} castShadow>
            <cylinderGeometry args={[0.005, 0.005, 0.08, 16]} />
            <meshStandardMaterial color="#94a3b8" metalness={0.9} roughness={0.2} wireframe={showWireframe} />
          </mesh>
          {/* Black Frame Rim */}
          <mesh position={[0, 0, 0.09]} rotation={[Math.PI / 2, 0, 0]} castShadow>
            <torusGeometry args={[0.035, 0.004, 16, 32]} />
            <meshStandardMaterial color="#0f172a" metalness={0.7} roughness={0.3} wireframe={showWireframe} />
          </mesh>
          {/* Convex Glass Lens */}
          <mesh position={[0, 0, 0.09]} rotation={[Math.PI / 2, 0, 0]}>
            <sphereGeometry args={[0.034, 32, 16, 0, Math.PI * 2, 0, Math.PI * 0.45]} />
            <meshPhysicalMaterial
              color="#e0f2fe"
              transmission={showWireframe ? 0 : 0.95}
              roughness={showWireframe ? 1 : 0.02}
              ior={1.52}
              thickness={0.03}
              wireframe={showWireframe}
            />
          </mesh>
        </group>
      )}

      {/* --- ASSET: glass-slab --- */}
      {asset.id === 'glass-slab' && (
        <group position={[0, 0, 0.015]}>
          <mesh castShadow receiveShadow>
            <boxGeometry args={[0.12, 0.08, 0.03]} />
            <meshPhysicalMaterial
              color="#e0f2fe"
              transmission={showWireframe ? 0 : 0.96}
              roughness={showWireframe ? 1 : 0.02}
              ior={1.517}
              thickness={0.08}
              clearcoat={1.0}
              wireframe={showWireframe}
            />
          </mesh>
        </group>
      )}

      {/* --- ASSET: magnesium-burning-setup --- */}
      {asset.id === 'magnesium-burning-setup' && (
        <group position={[0, 0, 0]}>
          {/* Bunsen Burner */}
          <mesh position={[-0.04, 0, 0.01]} castShadow>
            <cylinderGeometry args={[0.03, 0.035, 0.02, 20]} />
            <meshStandardMaterial color="#334155" metalness={0.8} roughness={0.3} wireframe={showWireframe} />
          </mesh>
          <mesh position={[-0.04, 0, 0.05]} castShadow>
            <cylinderGeometry args={[0.007, 0.007, 0.07, 16]} />
            <meshStandardMaterial color="#94a3b8" metalness={0.85} roughness={0.2} wireframe={showWireframe} />
          </mesh>
          {/* Flame */}
          {stateIndex >= 1 && (
            <mesh position={[-0.04, 0, 0.095]}>
              <coneGeometry args={[0.012, 0.03, 16]} />
              <meshStandardMaterial
                color={stateIndex === 2 ? '#ffffff' : '#38bdf8'}
                emissive={stateIndex === 2 ? '#ffffff' : '#0284c7'}
                emissiveIntensity={stateIndex === 2 ? 5.0 : 2.5}
              />
            </mesh>
          )}

          {/* Tongs holding Magnesium Ribbon */}
          <mesh position={[0.01, 0, 0.085]} rotation={[0, 0, THREE.MathUtils.degToRad(-25)]} castShadow>
            <boxGeometry args={[0.08, 0.008, 0.004]} />
            <meshStandardMaterial color="#64748b" metalness={0.9} roughness={0.2} wireframe={showWireframe} />
          </mesh>
          {/* Magnesium Ribbon Tip */}
          <mesh position={[-0.03, 0, 0.095]}>
            <boxGeometry args={[0.025, 0.004, 0.002]} />
            <meshStandardMaterial
              color={stateIndex === 3 ? '#ffffff' : '#cbd5e1'}
              emissive={stateIndex === 2 ? '#ffffff' : '#000000'}
              emissiveIntensity={stateIndex === 2 ? 6.0 : 0}
              metalness={0.9}
            />
          </mesh>

          {/* Watch Glass & White MgO Ash */}
          <mesh position={[0.07, 0, 0.008]} receiveShadow>
            <cylinderGeometry args={[0.035, 0.035, 0.004, 24]} />
            <meshPhysicalMaterial color="#e0f2fe" transmission={0.9} roughness={0.1} wireframe={showWireframe} />
          </mesh>
          {stateIndex === 3 && (
            <mesh position={[0.07, 0, 0.014]}>
              <coneGeometry args={[0.015, 0.008, 16]} />
              <meshStandardMaterial color="#ffffff" roughness={0.9} />
            </mesh>
          )}
        </group>
      )}

      {/* --- ASSET: magnesium-atom --- */}
      {asset.id === 'magnesium-atom' && (
        <group position={[0, 0, 0.08]} rotation={[Math.PI / 2, 0, 0]}>
          <BohrAtomModel
            element="Mg"
            charge={stateIndex === 2 ? 2 : 0}
            highlightValence={stateIndex < 2}
            orbitSpeedMultiplier={stateIndex === 1 ? 2.0 : 1.0}
            showNucleusDetails={true}
            showShellLabels={true}
          />
        </group>
      )}

      {/* --- ASSET: oxygen-atom --- */}
      {asset.id === 'oxygen-atom' && (
        <group position={[0, 0, 0.08]} rotation={[Math.PI / 2, 0, 0]}>
          <BohrAtomModel
            element="O"
            charge={stateIndex === 2 ? -2 : 0}
            highlightValence={stateIndex < 2}
            orbitSpeedMultiplier={stateIndex === 1 ? 2.0 : 1.0}
            showNucleusDetails={true}
            showShellLabels={true}
          />
        </group>
      )}

      {/* --- ASSET: magnesium-oxide-lattice --- */}
      {asset.id === 'magnesium-oxide-lattice' && (
        <group position={[0, 0, 0.08]} rotation={[Math.PI / 2, 0, 0]}>
          <IonicReaction3DModel
            stage={((stateIndex % 4) + 1) as 1 | 2 | 3 | 4}
            showElectricField={true}
          />
        </group>
      )}

      {/* --- ASSET: bunsen-burner --- */}
      {asset.id === 'bunsen-burner' && (
        <group position={[0, 0, 0]}>
          <mesh position={[0, 0, 0.015]} castShadow>
            <cylinderGeometry args={[0.035, 0.042, 0.03, 24]} />
            <meshStandardMaterial color="#1e293b" metalness={0.8} roughness={0.3} wireframe={showWireframe} />
          </mesh>
          <mesh position={[0, 0, 0.04]} castShadow>
            <cylinderGeometry args={[0.012, 0.012, 0.02, 20]} />
            <meshStandardMaterial color="#eab308" metalness={0.7} roughness={0.3} wireframe={showWireframe} />
          </mesh>
          <mesh position={[0, 0, 0.085]} castShadow>
            <cylinderGeometry args={[0.008, 0.008, 0.08, 16]} />
            <meshStandardMaterial color="#64748b" metalness={0.85} roughness={0.2} wireframe={showWireframe} />
          </mesh>
          {/* Clean Blue Flame */}
          <mesh position={[0, 0, 0.14]}>
            <coneGeometry args={[0.014, 0.04, 16]} />
            <meshStandardMaterial color="#38bdf8" emissive="#0284c7" emissiveIntensity={3.0} />
          </mesh>
        </group>
      )}

      {/* --- ASSET: beaker --- */}
      {asset.id === 'beaker' && (
        <group position={[0, 0, 0.045]}>
          <mesh castShadow receiveShadow>
            <cylinderGeometry args={[0.032, 0.03, 0.09, 24, 1, true]} />
            <meshPhysicalMaterial
              color="#e0f2fe"
              transmission={showWireframe ? 0 : 0.94}
              roughness={showWireframe ? 1 : 0.03}
              ior={1.47}
              thickness={0.02}
              wireframe={showWireframe}
            />
          </mesh>
          {/* Bottom */}
          <mesh position={[0, 0, -0.044]}>
            <cylinderGeometry args={[0.03, 0.03, 0.003, 24]} />
            <meshPhysicalMaterial color="#e0f2fe" transmission={0.94} roughness={0.03} wireframe={showWireframe} />
          </mesh>
          {/* Blue Chemical Solution */}
          <mesh position={[0, 0, -0.01]}>
            <cylinderGeometry args={[0.029, 0.029, 0.05, 20]} />
            <meshPhysicalMaterial color="#38bdf8" transmission={0.8} roughness={0.1} transparent opacity={0.85} />
          </mesh>
        </group>
      )}

      {/* --- ASSET: human-heart --- */}
      {asset.id === 'human-heart' && (
        <group position={[0, 0, 0.05]} ref={heartParticlesRef}>
          {/* Muscular Ventricles */}
          <mesh position={[-0.015, 0, -0.01]} castShadow>
            <sphereGeometry args={[0.035, 24, 24]} />
            <meshStandardMaterial color="#dc2626" roughness={0.6} metalness={0.1} wireframe={showWireframe} />
          </mesh>
          <mesh position={[0.018, 0, 0.0]} castShadow>
            <sphereGeometry args={[0.032, 24, 24]} />
            <meshStandardMaterial color="#b91c1c" roughness={0.6} metalness={0.1} wireframe={showWireframe} />
          </mesh>
          {/* Aorta Arch (Red) */}
          <mesh position={[0.005, 0, 0.04]} rotation={[0, 0, Math.PI / 4]} castShadow>
            <torusGeometry args={[0.022, 0.007, 16, 24, Math.PI]} />
            <meshStandardMaterial color="#ef4444" roughness={0.5} wireframe={showWireframe} />
          </mesh>
          {/* Pulmonary Artery (Blue) */}
          <mesh position={[-0.015, 0.01, 0.03]} rotation={[0, Math.PI / 3, 0]} castShadow>
            <cylinderGeometry args={[0.006, 0.006, 0.035, 16]} />
            <meshStandardMaterial color="#2563eb" roughness={0.5} wireframe={showWireframe} />
          </mesh>
        </group>
      )}

      {/* --- ASSET: human-eye --- */}
      {asset.id === 'human-eye' && (
        <group position={[0, 0, 0.04]}>
          {/* Sclera White Eyeball */}
          <mesh castShadow>
            <sphereGeometry args={[0.038, 32, 32]} />
            <meshStandardMaterial color="#f8fafc" roughness={0.3} metalness={0.05} wireframe={showWireframe} />
          </mesh>
          {/* Iris (Cyan) */}
          <mesh position={[0, 0, 0.032]}>
            <cylinderGeometry args={[0.016, 0.016, 0.002, 24]} />
            <meshStandardMaterial color="#0284c7" roughness={0.4} wireframe={showWireframe} />
          </mesh>
          {/* Pupil (Black) */}
          <mesh position={[0, 0, 0.034]}>
            <cylinderGeometry args={[0.007, 0.007, 0.002, 20]} />
            <meshStandardMaterial color="#0f172a" roughness={0.1} />
          </mesh>
          {/* Clear Cornea Dome */}
          <mesh position={[0, 0, 0.032]}>
            <sphereGeometry args={[0.020, 24, 16, 0, Math.PI * 2, 0, Math.PI * 0.45]} />
            <meshPhysicalMaterial color="#e0f2fe" transmission={0.95} roughness={0.02} ior={1.376} wireframe={showWireframe} />
          </mesh>
        </group>
      )}

      {/* --- ASSET: full-circuit --- */}
      {asset.id === 'full-circuit' && (
        <group position={[0, 0, 0]}>
          {/* Circuit Board Base */}
          <mesh position={[0, 0, 0.005]} receiveShadow castShadow>
            <boxGeometry args={[0.32, 0.22, 0.012]} />
            <meshStandardMaterial color="#1e293b" roughness={0.4} metalness={0.2} wireframe={showWireframe} />
          </mesh>
          {/* Battery Eliminator */}
          <mesh position={[-0.10, -0.05, 0.025]} castShadow>
            <boxGeometry args={[0.06, 0.05, 0.03]} />
            <meshStandardMaterial color="#dc2626" metalness={0.7} roughness={0.3} wireframe={showWireframe} />
          </mesh>
          {/* Ammeter */}
          <mesh position={[-0.03, 0.05, 0.025]} castShadow>
            <cylinderGeometry args={[0.025, 0.025, 0.025, 20]} />
            <meshStandardMaterial color="#475569" metalness={0.5} roughness={0.4} wireframe={showWireframe} />
          </mesh>
          {/* Voltmeter */}
          <mesh position={[0.04, 0.07, 0.025]} castShadow>
            <cylinderGeometry args={[0.025, 0.025, 0.025, 20]} />
            <meshStandardMaterial color="#475569" metalness={0.5} roughness={0.4} wireframe={showWireframe} />
          </mesh>
          {/* Resistor Wire */}
          <mesh position={[0.04, 0.02, 0.015]} rotation={[0, 0, Math.PI / 2]}>
            <cylinderGeometry args={[0.002, 0.002, 0.06, 12]} />
            <meshStandardMaterial color="#b45309" metalness={0.9} roughness={0.2} />
          </mesh>
          {/* Rheostat */}
          <mesh position={[0.09, -0.04, 0.025]} rotation={[0, 0, Math.PI / 2]} castShadow>
            <cylinderGeometry args={[0.012, 0.012, 0.08, 16]} />
            <meshStandardMaterial color="#94a3b8" metalness={0.8} roughness={0.25} wireframe={showWireframe} />
          </mesh>
        </group>
      )}

      {/* --- ASSET: voltmeter or ammeter --- */}
      {(asset.id === 'voltmeter' || asset.id === 'ammeter') && (
        <group position={[0, 0, 0.025]}>
          <mesh castShadow receiveShadow>
            <boxGeometry args={[0.085, 0.085, 0.05]} />
            <meshStandardMaterial color="#1e293b" roughness={0.3} metalness={0.6} wireframe={showWireframe} />
          </mesh>
          {/* Glass Dial Window */}
          <mesh position={[0, 0, 0.026]}>
            <boxGeometry args={[0.07, 0.065, 0.002]} />
            <meshPhysicalMaterial color="#ffffff" transmission={0.9} roughness={0.05} wireframe={showWireframe} />
          </mesh>
          {/* Red & Black Terminals */}
          <mesh position={[-0.025, -0.032, 0.015]}>
            <cylinderGeometry args={[0.005, 0.005, 0.015, 16]} />
            <meshStandardMaterial color="#ef4444" metalness={0.8} />
          </mesh>
          <mesh position={[0.025, -0.032, 0.015]}>
            <cylinderGeometry args={[0.005, 0.005, 0.015, 16]} />
            <meshStandardMaterial color="#0f172a" metalness={0.8} />
          </mesh>
          <Text position={[0, 0.01, 0.028]} fontSize={0.014} color="#38bdf8" anchorX="center">
            {asset.id === 'voltmeter' ? 'V (0-3V)' : 'A (0-3A)'}
          </Text>
        </group>
      )}

      {/* ===================================================================== */}
      {/* 2. SNAP / ANCHOR POINT VISUALIZER PINS                                */}
      {/* ===================================================================== */}
      {showSockets && asset.anchorPoints && (
        <group>
          {Object.entries(asset.anchorPoints).map(([name, [sx, sy, sz]]) => (
            <group key={name} position={[sx, sy, sz]}>
              <mesh>
                <sphereGeometry args={[0.0045, 16, 16]} />
                <meshStandardMaterial color="#38bdf8" emissive="#38bdf8" emissiveIntensity={3.0} />
              </mesh>
              <mesh position={[0, 0, 0.006]}>
                <cylinderGeometry args={[0.0006, 0.0006, 0.012, 8]} />
                <meshStandardMaterial color="#38bdf8" />
              </mesh>
              <Text
                position={[0, 0, 0.016]}
                fontSize={0.007}
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

      {/* ===================================================================== */}
      {/* 3. 3D BOUNDING BOX & SCALE DIMENSIONS                                 */}
      {/* ===================================================================== */}
      {showDimensions && asset.dimensions && (
        <group>
          {(() => {
            const w = asset.dimensions.width_mm / 1000;
            const h = asset.dimensions.height_mm / 1000;
            const d = asset.dimensions.depth_mm / 1000;
            return (
              <group position={[0, 0, h / 2]}>
                <mesh>
                  <boxGeometry args={[w, d, h]} />
                  <meshBasicMaterial color="#38bdf8" wireframe transparent opacity={0.4} />
                </mesh>
                <Text position={[0, -d / 2 - 0.015, -h / 2]} fontSize={0.008} color="#38bdf8">
                  Width: {asset.dimensions.width_mm} mm
                </Text>
                <Text position={[-w / 2 - 0.015, 0, -h / 2]} fontSize={0.008} color="#38bdf8" rotation={[0, 0, Math.PI / 2]}>
                  Depth: {asset.dimensions.depth_mm} mm
                </Text>
                <Text position={[w / 2 + 0.015, 0, 0]} fontSize={0.008} color="#38bdf8">
                  Height: {asset.dimensions.height_mm} mm
                </Text>
              </group>
            );
          })()}
        </group>
      )}
    </group>
  );
}