import { useRef, useMemo, useState } from 'react';
import * as THREE from 'three';
import { useFrame } from '@react-three/fiber';
import { Text } from '@react-three/drei';

export interface BohrElementData {
  symbol: string;
  name: string;
  atomicNumber: number;
  massNumber: number;
  shells: number[]; // e.g. [2, 8, 2]
  period: number;
  group: number;
  color: string;
  valenceColor: string;
}

export const ELEMENT_DATABASE: Record<string, BohrElementData> = {
  H: { symbol: 'H', name: 'Hydrogen', atomicNumber: 1, massNumber: 1, shells: [1], period: 1, group: 1, color: '#f8fafc', valenceColor: '#38bdf8' },
  He: { symbol: 'He', name: 'Helium', atomicNumber: 2, massNumber: 4, shells: [2], period: 1, group: 18, color: '#f8fafc', valenceColor: '#38bdf8' },
  Li: { symbol: 'Li', name: 'Lithium', atomicNumber: 3, massNumber: 7, shells: [2, 1], period: 2, group: 1, color: '#cbd5e1', valenceColor: '#38bdf8' },
  C: { symbol: 'C', name: 'Carbon', atomicNumber: 6, massNumber: 12, shells: [2, 4], period: 2, group: 14, color: '#94a3b8', valenceColor: '#38bdf8' },
  N: { symbol: 'N', name: 'Nitrogen', atomicNumber: 7, massNumber: 14, shells: [2, 5], period: 2, group: 15, color: '#60a5fa', valenceColor: '#38bdf8' },
  O: { symbol: 'O', name: 'Oxygen', atomicNumber: 8, massNumber: 16, shells: [2, 6], period: 2, group: 16, color: '#f87171', valenceColor: '#fb7185' },
  F: { symbol: 'F', name: 'Fluorine', atomicNumber: 9, massNumber: 19, shells: [2, 7], period: 2, group: 17, color: '#4ade80', valenceColor: '#38bdf8' },
  Ne: { symbol: 'Ne', name: 'Neon', atomicNumber: 10, massNumber: 20, shells: [2, 8], period: 2, group: 18, color: '#38bdf8', valenceColor: '#38bdf8' },
  Na: { symbol: 'Na', name: 'Sodium', atomicNumber: 11, massNumber: 23, shells: [2, 8, 1], period: 3, group: 1, color: '#a78bfa', valenceColor: '#38bdf8' },
  Mg: { symbol: 'Mg', name: 'Magnesium', atomicNumber: 12, massNumber: 24, shells: [2, 8, 2], period: 3, group: 2, color: '#38bdf8', valenceColor: '#06b6d4' },
  Al: { symbol: 'Al', name: 'Aluminium', atomicNumber: 13, massNumber: 27, shells: [2, 8, 3], period: 3, group: 13, color: '#94a3b8', valenceColor: '#38bdf8' },
  Cl: { symbol: 'Cl', name: 'Chlorine', atomicNumber: 17, massNumber: 35, shells: [2, 8, 7], period: 3, group: 17, color: '#4ade80', valenceColor: '#a3e635' },
  Ca: { symbol: 'Ca', name: 'Calcium', atomicNumber: 20, massNumber: 40, shells: [2, 8, 8, 2], period: 4, group: 2, color: '#facc15', valenceColor: '#38bdf8' },
};

export interface BohrAtomModelProps {
  element?: keyof typeof ELEMENT_DATABASE | string;
  charge?: number; // 0 for neutral, +2 for Mg2+, -2 for O2-
  scale?: number;
  position?: [number, number, number];
  rotation?: [number, number, number];
  showShellLabels?: boolean;
  showNucleusDetails?: boolean;
  orbitSpeedMultiplier?: number;
  highlightValence?: boolean;
  onHoverShell?: (shellIndex: number | null) => void;
}

const SHELL_NAMES = ['K (n=1)', 'L (n=2)', 'M (n=3)', 'N (n=4)'];
const BASE_SHELL_RADII = [0.055, 0.095, 0.138, 0.180]; // in meters (visualization scale)

export function BohrAtomModel({
  element = 'Mg',
  charge = 0,
  scale = 1.0,
  position = [0, 0, 0],
  rotation = [0, 0, 0],
  showShellLabels = true,
  showNucleusDetails = true,
  orbitSpeedMultiplier = 1.0,
  highlightValence = true,
  onHoverShell,
}: BohrAtomModelProps) {
  const groupRef = useRef<THREE.Group>(null);
  const electronsGroupRef = useRef<THREE.Group>(null);
  const [hoveredShell, setHoveredShell] = useState<number | null>(null);

  const elementData: BohrElementData =
    ELEMENT_DATABASE[element as keyof typeof ELEMENT_DATABASE] || ELEMENT_DATABASE.Mg;

  // Compute effective electron distribution based on charge
  const effectiveShells = useMemo(() => {
    const raw = [...elementData.shells];
    if (charge === 0) return raw;

    let remCharge = charge;
    if (remCharge > 0) {
      // Cation: remove valence electrons from outermost shells
      for (let i = raw.length - 1; i >= 0 && remCharge > 0; i--) {
        const take = Math.min(raw[i], remCharge);
        raw[i] -= take;
        remCharge -= take;
      }
      // Filter out completely empty outer shells
      while (raw.length > 1 && raw[raw.length - 1] === 0) {
        raw.pop();
      }
    } else if (remCharge < 0) {
      // Anion: add electrons to outermost shell
      const add = Math.abs(remCharge);
      raw[raw.length - 1] += add;
    }
    return raw;
  }, [elementData, charge]);

  // Procedural Nucleon Clusters (Protons + Neutrons packed inside core)
  const nucleons = useMemo(() => {
    const protons = elementData.atomicNumber;
    const neutrons = elementData.massNumber - protons;
    const total = Math.min(protons + neutrons, 24); // cap visual density for performance
    const points: { pos: [number, number, number]; isProton: boolean }[] = [];

    const goldenRatio = (1 + Math.sqrt(5)) / 2;
    const nucleusRadius = 0.022;

    for (let i = 0; i < total; i++) {
      const theta = 2 * Math.PI * i / goldenRatio;
      const phi = Math.acos(1 - 2 * (i + 0.5) / total);
      const r = nucleusRadius * Math.cbrt((i + 1) / total);

      const x = r * Math.sin(phi) * Math.cos(theta);
      const y = r * Math.sin(phi) * Math.sin(theta);
      const z = r * Math.cos(phi);

      points.push({
        pos: [x, y, z],
        isProton: i < protons,
      });
    }
    return points;
  }, [elementData]);

  // Real-time orbital rotation of electrons
  useFrame(({ clock }) => {
    const t = clock.getElapsedTime() * orbitSpeedMultiplier;
    if (!electronsGroupRef.current) return;

    electronsGroupRef.current.children.forEach((shellGroup) => {
      const shellIdx = shellGroup.userData.shellIndex;
      if (shellIdx !== undefined) {
        // Bohr frequency: inner shells orbit faster: omega_n = omega_0 / sqrt(n)
        const omega = 1.6 / Math.sqrt(shellIdx + 1);
        shellGroup.rotation.z = t * omega;
      }
    });
  });

  return (
    <group ref={groupRef} position={position} rotation={rotation} scale={scale}>
      {/* ========================================================================= */}
      {/* 1. CENTRAL NUCLEUS                                                        */}
      {/* ========================================================================= */}
      <group position={[0, 0, 0]}>
        {/* Luminous Nuclear Core Sphere */}
        <mesh>
          <sphereGeometry args={[0.024, 32, 32]} />
          <meshStandardMaterial
            color={elementData.color}
            emissive={elementData.color}
            emissiveIntensity={1.4}
            roughness={0.25}
            metalness={0.1}
          />
        </mesh>

        {/* Nucleons (Protons in warm red, Neutrons in neutral slate) */}
        {nucleons.map((n, idx) => (
          <mesh key={idx} position={n.pos}>
            <sphereGeometry args={[0.0055, 12, 12]} />
            <meshStandardMaterial
              color={n.isProton ? '#ef4444' : '#64748b'}
              emissive={n.isProton ? '#dc2626' : '#334155'}
              emissiveIntensity={0.8}
              roughness={0.4}
            />
          </mesh>
        ))}

        {/* Central Element Symbol Badge */}
        <Text
          position={[0, 0, 0.026]}
          fontSize={0.016}
          fontWeight="bold"
          color="#ffffff"
          anchorX="center"
          anchorY="middle"
        >
          {elementData.symbol}
        </Text>

        {/* Subscript Nucleus Info (e.g. 12p 12n) */}
        {showNucleusDetails && (
          <Text
            position={[0, -0.012, 0.026]}
            fontSize={0.0055}
            color="#e2e8f0"
            anchorX="center"
            anchorY="middle"
          >
            {elementData.atomicNumber}p {elementData.massNumber - elementData.atomicNumber}n
          </Text>
        )}

        {/* Charge Badge (if ionized: e.g. Mg²⁺ or O²⁻) */}
        {charge !== 0 && (
          <group position={[0.025, 0.025, 0.02]}>
            <mesh>
              <sphereGeometry args={[0.011, 16, 16]} />
              <meshStandardMaterial
                color={charge > 0 ? '#0284c7' : '#e11d48'}
                emissive={charge > 0 ? '#38bdf8' : '#fb7185'}
                emissiveIntensity={2.5}
              />
            </mesh>
            <Text
              position={[0, 0, 0.012]}
              fontSize={0.009}
              fontWeight="bold"
              color="#ffffff"
              anchorX="center"
              anchorY="middle"
            >
              {charge > 0 ? `+${charge}` : `${charge}`}
            </Text>
          </group>
        )}
      </group>

      {/* ========================================================================= */}
      {/* 2. CONCENTRIC QUANTUM ELECTRON SHELLS                                     */}
      {/* ========================================================================= */}
      <group ref={electronsGroupRef}>
        {effectiveShells.map((eCount, sIdx) => {
          const radius = BASE_SHELL_RADII[sIdx] || (0.055 + sIdx * 0.045);
          const isValence = sIdx === effectiveShells.length - 1;
          const isHovered = hoveredShell === sIdx;
          const maxCapacity = 2 * (sIdx + 1) * (sIdx + 1);

          return (
            <group
              key={sIdx}
              userData={{ shellIndex: sIdx }}
              onPointerOver={(e) => {
                e.stopPropagation();
                setHoveredShell(sIdx);
                onHoverShell?.(sIdx);
              }}
              onPointerOut={() => {
                setHoveredShell(null);
                onHoverShell?.(null);
              }}
            >
              {/* Orbital Ring Torus Guide */}
              <mesh rotation={[0, 0, 0]}>
                <torusGeometry args={[radius, isHovered ? 0.0016 : 0.0008, 16, 64]} />
                <meshStandardMaterial
                  color={
                    isHovered
                      ? '#38bdf8'
                      : isValence && highlightValence
                      ? elementData.valenceColor
                      : '#475569'
                  }
                  emissive={
                    isHovered
                      ? '#38bdf8'
                      : isValence && highlightValence
                      ? elementData.valenceColor
                      : '#1e293b'
                  }
                  emissiveIntensity={isHovered ? 2.5 : isValence ? 1.2 : 0.4}
                  transparent
                  opacity={isHovered ? 0.95 : 0.65}
                />
              </mesh>

              {/* Electrons on this shell */}
              {Array.from({ length: eCount }).map((_, eIdx) => {
                const angle = (2 * Math.PI * eIdx) / eCount;
                const ex = radius * Math.cos(angle);
                const ey = radius * Math.sin(angle);

                return (
                  <group key={eIdx} position={[ex, ey, 0]}>
                    {/* Glowing Electron Sphere */}
                    <mesh>
                      <sphereGeometry args={[0.0052, 16, 16]} />
                      <meshStandardMaterial
                        color={isValence && highlightValence ? elementData.valenceColor : '#38bdf8'}
                        emissive={isValence && highlightValence ? elementData.valenceColor : '#38bdf8'}
                        emissiveIntensity={isHovered ? 4.0 : 2.5}
                        roughness={0.2}
                      />
                    </mesh>

                    {/* Electron Halo Glow Disc */}
                    <mesh position={[0, 0, 0]}>
                      <circleGeometry args={[0.009, 16]} />
                      <meshBasicMaterial
                        color={isValence && highlightValence ? elementData.valenceColor : '#38bdf8'}
                        transparent
                        opacity={0.35}
                        side={THREE.DoubleSide}
                      />
                    </mesh>
                  </group>
                );
              })}

              {/* Shell Name & Capacity Label */}
              {showShellLabels && (
                <Text
                  position={[0, radius + 0.008, 0]}
                  fontSize={0.0065}
                  color={isHovered ? '#38bdf8' : '#94a3b8'}
                  anchorX="center"
                  anchorY="bottom"
                >
                  {SHELL_NAMES[sIdx] || `n=${sIdx + 1}`}: {eCount}/{maxCapacity}e⁻
                </Text>
              )}
            </group>
          );
        })}
      </group>

      {/* ========================================================================= */}
      {/* 3. ATOM FOOTER ANNOTATIONS                                                */}
      {/* ========================================================================= */}
      <group position={[0, -(BASE_SHELL_RADII[effectiveShells.length - 1] || 0.14) - 0.025, 0]}>
        <Text
          position={[0, 0, 0]}
          fontSize={0.010}
          fontWeight="bold"
          color="#f8fafc"
          anchorX="center"
          anchorY="top"
        >
          {elementData.name} ({elementData.symbol})
        </Text>
        <Text
          position={[0, -0.012, 0]}
          fontSize={0.0075}
          color="#38bdf8"
          anchorX="center"
          anchorY="top"
        >
          Config: [{effectiveShells.join(', ')}]{charge !== 0 ? ` → Net: ${charge > 0 ? `+${charge}` : charge}` : ''}
        </Text>
      </group>
    </group>
  );
}
