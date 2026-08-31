import { useRef, useMemo } from 'react';
import * as THREE from 'three';
import { useFrame } from '@react-three/fiber';
import { Text } from '@react-three/drei';
import { BohrAtomModel } from './BohrAtomModel';

export interface IonicReaction3DModelProps {
  stage?: 1 | 2 | 3 | 4; // 1: Neutral Atoms, 2: Electron Transfer, 3: Ionization, 4: Coulomb Attraction & Bond
  progress?: number; // 0.0 to 1.0 continuous scrubber
  showElectricField?: boolean;
}

export function IonicReaction3DModel({
  stage = 1,
  progress: manualProgress,
  showElectricField = true,
}: IonicReaction3DModelProps) {
  const groupRef = useRef<THREE.Group>(null);
  const electronsTrailRef = useRef<THREE.Group>(null);

  // Compute normalized progress u in [0, 1] based on stage or manualProgress
  const u = useMemo(() => {
    if (manualProgress !== undefined) return manualProgress;
    if (stage === 1) return 0.0;
    if (stage === 2) return 0.45;
    if (stage === 3) return 0.85;
    return 1.0; // stage 4
  }, [stage, manualProgress]);

  // Dynamic atom positions (approaching from +/- 0.26m to +/- 0.12m during stage 4)
  const separationProgress = Math.max(0, Math.min(1, (u - 0.70) / 0.30));
  const mgX = THREE.MathUtils.lerp(-0.25, -0.11, separationProgress);
  const oX = THREE.MathUtils.lerp(0.25, 0.11, separationProgress);

  // Transfer arc interpolation: 0 when u <= 0.15, 1 when u >= 0.70
  const transferU = Math.max(0, Math.min(1, (u - 0.15) / 0.55));

  // 3D Quadratic Bézier curve for transferring electron 1 (top arc)
  const e1Pos = useMemo(() => {
    const p0 = new THREE.Vector3(-0.25 + 0.138, 0.0, 0.0); // from Mg M-shell right side
    const p1 = new THREE.Vector3(0.0, 0.06, 0.08); // elevated curved apex
    const p2 = new THREE.Vector3(0.25 - 0.095, 0.03, 0.0); // into O L-shell left vacancy
    const t = transferU;
    return new THREE.Vector3()
      .addScaledVector(p0, (1 - t) * (1 - t))
      .addScaledVector(p1, 2 * (1 - t) * t)
      .addScaledVector(p2, t * t);
  }, [transferU]);

  // 3D Quadratic Bézier curve for transferring electron 2 (bottom arc)
  const e2Pos = useMemo(() => {
    const p0 = new THREE.Vector3(-0.25 + 0.138, 0.0, 0.0); // from Mg M-shell
    const p1 = new THREE.Vector3(0.0, -0.06, -0.08); // lower curved apex
    const p2 = new THREE.Vector3(0.25 - 0.095, -0.03, 0.0); // into O L-shell
    const t = transferU;
    return new THREE.Vector3()
      .addScaledVector(p0, (1 - t) * (1 - t))
      .addScaledVector(p1, 2 * (1 - t) * t)
      .addScaledVector(p2, t * t);
  }, [transferU]);

  // Subtle pulsing glow during electron transfer
  useFrame(({ clock }) => {
    if (electronsTrailRef.current) {
      const pulse = 1.0 + Math.sin(clock.getElapsedTime() * 8.0) * 0.2;
      electronsTrailRef.current.scale.set(pulse, pulse, pulse);
    }
  });

  const isIonized = u >= 0.70;
  const isTransferring = u > 0.15 && u < 0.70;

  return (
    <group ref={groupRef}>
      {/* ========================================================================= */}
      {/* 1. MAGNESIUM ATOM / CATION (LEFT)                                         */}
      {/* ========================================================================= */}
      <group position={[mgX, 0, 0]}>
        <BohrAtomModel
          element="Mg"
          charge={isIonized ? 2 : 0}
          showNucleusDetails={true}
          showShellLabels={true}
          highlightValence={!isIonized}
          orbitSpeedMultiplier={isIonized ? 1.4 : 1.0}
        />

        {/* State Badge for Magnesium */}
        <group position={[0, 0.18, 0]}>
          <Text
            fontSize={0.012}
            fontWeight="bold"
            color={isIonized ? '#38bdf8' : '#cbd5e1'}
            anchorX="center"
            anchorY="bottom"
          >
            {isIonized ? 'Mg²⁺ Cation (Electropositive)' : 'Neutral Magnesium Atom (Mg)'}
          </Text>
          <Text
            position={[0, -0.010, 0]}
            fontSize={0.008}
            color={isIonized ? '#4ade80' : '#94a3b8'}
            anchorX="center"
            anchorY="top"
          >
            {isIonized ? 'Stable Neon Octet [2, 8] ✓' : 'Valence: [2, 8, 2] (2 Donors)'}
          </Text>
        </group>
      </group>

      {/* ========================================================================= */}
      {/* 2. OXYGEN ATOM / ANION (RIGHT)                                            */}
      {/* ========================================================================= */}
      <group position={[oX, 0, 0]}>
        <BohrAtomModel
          element="O"
          charge={isIonized ? -2 : 0}
          showNucleusDetails={true}
          showShellLabels={true}
          highlightValence={!isIonized}
          orbitSpeedMultiplier={isIonized ? 1.4 : 1.0}
        />

        {/* State Badge for Oxygen */}
        <group position={[0, 0.18, 0]}>
          <Text
            fontSize={0.012}
            fontWeight="bold"
            color={isIonized ? '#fb7185' : '#f87171'}
            anchorX="center"
            anchorY="bottom"
          >
            {isIonized ? 'O²⁻ Oxide Anion (Electronegative)' : 'Neutral Oxygen Atom (O)'}
          </Text>
          <Text
            position={[0, -0.010, 0]}
            fontSize={0.008}
            color={isIonized ? '#4ade80' : '#94a3b8'}
            anchorX="center"
            anchorY="top"
          >
            {isIonized ? 'Stable Neon Octet [2, 8] ✓' : 'Valence: [2, 6] (Needs 2e⁻)'}
          </Text>
        </group>
      </group>

      {/* ========================================================================= */}
      {/* 3. 3D TRANSFERRING ELECTRONS & TRAJECTORY ARCS                            */}
      {/* ========================================================================= */}
      {isTransferring && (
        <group>
          {/* Electron 1 in Flight (Top Arc) */}
          <group position={e1Pos.toArray()} ref={electronsTrailRef}>
            <mesh>
              <sphereGeometry args={[0.007, 16, 16]} />
              <meshStandardMaterial
                color="#38bdf8"
                emissive="#38bdf8"
                emissiveIntensity={4.5}
                roughness={0.1}
              />
            </mesh>
            <mesh>
              <sphereGeometry args={[0.012, 12, 12]} />
              <meshBasicMaterial color="#38bdf8" transparent opacity={0.35} />
            </mesh>
            <Text position={[0, 0.012, 0]} fontSize={0.006} color="#38bdf8">
              e⁻ (1)
            </Text>
          </group>

          {/* Electron 2 in Flight (Bottom Arc) */}
          <group position={e2Pos.toArray()}>
            <mesh>
              <sphereGeometry args={[0.007, 16, 16]} />
              <meshStandardMaterial
                color="#38bdf8"
                emissive="#38bdf8"
                emissiveIntensity={4.5}
                roughness={0.1}
              />
            </mesh>
            <mesh>
              <sphereGeometry args={[0.012, 12, 12]} />
              <meshBasicMaterial color="#38bdf8" transparent opacity={0.35} />
            </mesh>
            <Text position={[0, -0.012, 0]} fontSize={0.006} color="#38bdf8">
              e⁻ (2)
            </Text>
          </group>

          {/* Center Transfer Indicator Banner */}
          <group position={[0, 0.08, 0.05]}>
            <Text
              fontSize={0.009}
              fontWeight="bold"
              color="#facc15"
              anchorX="center"
              anchorY="middle"
            >
              ⚡ Transferring 2 Valence Electrons...
            </Text>
          </group>
        </group>
      )}

      {/* ========================================================================= */}
      {/* 4. ELECTROSTATIC COULOMB ATTRACTION & IONIC BOND (STAGE 4)                */}
      {/* ========================================================================= */}
      {isIonized && showElectricField && (
        <group position={[(mgX + oX) / 2, 0, 0]}>
          {/* Luminous Electrostatic Field Lines */}
          <mesh rotation={[0, 0, Math.PI / 2]}>
            <cylinderGeometry args={[0.0018, 0.0018, Math.abs(oX - mgX) - 0.08, 16]} />
            <meshStandardMaterial
              color="#facc15"
              emissive="#f59e0b"
              emissiveIntensity={3.2}
              transparent
              opacity={0.85}
            />
          </mesh>

          {/* Radial Electrostatic Rings between Ions */}
          <mesh rotation={[0, Math.PI / 2, 0]}>
            <torusGeometry args={[0.035, 0.001, 16, 32]} />
            <meshBasicMaterial color="#facc15" transparent opacity={0.4} />
          </mesh>
          <mesh rotation={[0, Math.PI / 2, 0]}>
            <torusGeometry args={[0.060, 0.001, 16, 32]} />
            <meshBasicMaterial color="#facc15" transparent opacity={0.25} />
          </mesh>

          {/* Ionic Bond Label Banner */}
          <group position={[0, -0.16, 0]}>
            <Text
              fontSize={0.012}
              fontWeight="bold"
              color="#facc15"
              anchorX="center"
              anchorY="middle"
            >
              ⚡ Strong Electrostatic Attraction (Ionic Bond)
            </Text>
            <Text
              position={[0, -0.012, 0]}
              fontSize={0.0085}
              color="#e2e8f0"
              anchorX="center"
              anchorY="middle"
            >
              Mg²⁺ + O²⁻ → MgO (Magnesium Oxide Crystal Lattice)
            </Text>
          </group>
        </group>
      )}
    </group>
  );
}
