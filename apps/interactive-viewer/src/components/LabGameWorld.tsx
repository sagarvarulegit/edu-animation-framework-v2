import { useRef, useEffect, useMemo } from 'react';
import * as THREE from 'three';
import { useFrame } from '@react-three/fiber';
import { Text } from '@react-three/drei';

export type LabStationId = 'optics' | 'chemistry' | 'biology';

export interface LabGameWorldProps {
  activeStation: LabStationId;
  onSelectStation: (station: LabStationId) => void;
  // Optics controls
  prismStep: 1 | 2 | 3 | 4;
  // Chemistry controls
  burnStage: 'unheated' | 'heating' | 'burning' | 'collected';
  // Selected component
  selectedPart: string | null;
  onSelectPart: (partName: string) => void;
  // Player Position
  playerPosition: [number, number];
  onMovePlayer: (x: number, y: number) => void;
  isFPSMode?: boolean;
}

export function LabGameWorld({
  activeStation,
  onSelectStation,
  prismStep,
  burnStage,
  selectedPart,
  onSelectPart,
  playerPosition,
  onMovePlayer,
  isFPSMode = true,
}: LabGameWorldProps) {
  const groupRef = useRef<THREE.Group>(null);
  const playerRef = useRef<THREE.Group>(null);

  // Keyboard navigation state
  const keysPressed = useRef<{ [key: string]: boolean }>({});

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      keysPressed.current[e.key.toLowerCase()] = true;
      // Quick interaction key [E]
      if (e.key.toLowerCase() === 'e') {
        const [px, py] = playerPosition;
        if (Math.hypot(px - (-0.45), py - 0.0) < 0.50) onSelectStation('optics');
        else if (Math.hypot(px - 0.45, py - 0.0) < 0.50) onSelectStation('chemistry');
        else if (Math.hypot(px - 0.0, py - 0.55) < 0.50) onSelectStation('biology');
      }
    };
    const handleKeyUp = (e: KeyboardEvent) => {
      keysPressed.current[e.key.toLowerCase()] = false;
    };
    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
    };
  }, [playerPosition, onSelectStation]);

  // Player movement update in game loop
  useFrame((_, delta) => {
    let [px, py] = playerPosition;
    const speed = 1.0 * delta;
    let moved = false;

    if (keysPressed.current['w'] || keysPressed.current['arrowup']) {
      py += speed;
      moved = true;
    }
    if (keysPressed.current['s'] || keysPressed.current['arrowdown']) {
      py -= speed;
      moved = true;
    }
    if (keysPressed.current['a'] || keysPressed.current['arrowleft']) {
      px -= speed;
      moved = true;
    }
    if (keysPressed.current['d'] || keysPressed.current['arrowright']) {
      px += speed;
      moved = true;
    }

    if (moved) {
      // Room boundaries
      px = Math.max(-1.15, Math.min(1.15, px));
      py = Math.max(-0.95, Math.min(0.95, py));
      onMovePlayer(px, py);
    }

    // Smoothly update player avatar mesh position
    if (playerRef.current) {
      playerRef.current.position.x = THREE.MathUtils.lerp(playerRef.current.position.x, playerPosition[0], 0.2);
      playerRef.current.position.y = THREE.MathUtils.lerp(playerRef.current.position.y, playerPosition[1], 0.2);
    }
  });

  // Room Dimensions
  const floorZ = -0.22;
  const tableH = 0.22;
  const roomW = 2.6; // X: -1.3 to +1.3
  const roomD = 2.2; // Y: -1.1 to +1.1
  const wallH = 0.75;

  // Floor Tiles Generator (13x11 Checkerboard Lab Floor)
  const floorTiles = useMemo(() => {
    const tiles = [];
    const numX = 13;
    const numY = 11;
    const tileW = roomW / numX;
    const tileD = roomD / numY;
    const startX = -roomW / 2 + tileW / 2;
    const startY = -roomD / 2 + tileD / 2;

    for (let i = 0; i < numX; i++) {
      for (let j = 0; j < numY; j++) {
        const isDark = (i + j) % 2 === 1;
        tiles.push({
          id: `${i}-${j}`,
          x: startX + i * tileW,
          y: startY + j * tileD,
          w: tileW - 0.003,
          d: tileD - 0.003,
          color: isDark ? '#94a3b8' : '#f1f5f9',
          roughness: isDark ? 0.35 : 0.25,
        });
      }
    }
    return tiles;
  }, [roomW, roomD]);

  // Prism Shape for Extrusion
  const prismSide = 0.080;
  const prismH = 0.055;
  const triH = (prismSide * Math.sqrt(3)) / 2;
  const yApex = (2 * triH) / 3;
  const yBase = -triH / 3;
  const xHalf = prismSide / 2;

  const prismShape = useMemo(() => {
    const shape = new THREE.Shape();
    shape.moveTo(-xHalf, yBase);
    shape.lineTo(xHalf, yBase);
    shape.lineTo(0, yApex);
    shape.closePath();
    return shape;
  }, [prismSide]);

  // 7 Spectral Rainbow Rays
  const spectrumData = [
    { name: 'Red', hex: '#ef4444', eDeg: 49.8 },
    { name: 'Orange', hex: '#f97316', eDeg: 50.3 },
    { name: 'Yellow', hex: '#eab308', eDeg: 50.7 },
    { name: 'Green', hex: '#22c55e', eDeg: 51.4 },
    { name: 'Blue', hex: '#3b82f6', eDeg: 52.5 },
    { name: 'Indigo', hex: '#6366f1', eDeg: 53.4 },
    { name: 'Violet', hex: '#a855f7', eDeg: 54.6 },
  ];

  return (
    <group ref={groupRef}>
      {/* ========================================================================= */}
      {/* 1. SCIENCE LAB ROOM ARCHITECTURE (4 WALLS + 2 WINDOWS + FLOOR)            */}
      {/* ========================================================================= */}

      {/* --- WALL 1: BACK WALL (Y = +1.10) --- */}
      <group position={[0, roomD / 2, floorZ + wallH / 2]}>
        <mesh receiveShadow>
          <boxGeometry args={[roomW, 0.02, wallH]} />
          <meshStandardMaterial color="#f8fafc" roughness={0.85} />
        </mesh>
        <mesh position={[0, -0.002, -wallH / 2 + 0.12]} receiveShadow>
          <boxGeometry args={[roomW, 0.022, 0.24]} />
          <meshStandardMaterial color="#e2e8f0" roughness={0.75} />
        </mesh>
        <mesh position={[0, -0.006, -wallH / 2 + 0.02]} receiveShadow>
          <boxGeometry args={[roomW, 0.028, 0.04]} />
          <meshStandardMaterial color="#64748b" roughness={0.5} />
        </mesh>
        {/* Large Physics Chalkboard */}
        <mesh position={[0, -0.012, 0.08]} receiveShadow>
          <boxGeometry args={[1.1, 0.010, 0.32]} />
          <meshStandardMaterial color="#064e3b" roughness={0.6} />
        </mesh>
        <mesh position={[0, -0.008, 0.08]}>
          <boxGeometry args={[1.12, 0.008, 0.34]} />
          <meshStandardMaterial color="#78350f" roughness={0.5} />
        </mesh>
        <Text position={[0, -0.020, 0.08]} fontSize={0.022} color="#ecfdf5" anchorX="center" anchorY="middle">
          CENTRAL SCIENCE LAB — INTERACTIVE APPARATUS WORLD
        </Text>
      </group>

      {/* --- WALL 2: LEFT WALL WITH 2 ARCHITECTURAL SUNLIT WINDOWS (X = -1.30) --- */}
      <group position={[-roomW / 2, 0, floorZ + wallH / 2]}>
        <mesh receiveShadow>
          <boxGeometry args={[0.02, roomD, wallH]} />
          <meshStandardMaterial color="#f8fafc" roughness={0.85} />
        </mesh>
        <mesh position={[0.002, 0, -wallH / 2 + 0.12]} receiveShadow>
          <boxGeometry args={[0.022, roomD, 0.24]} />
          <meshStandardMaterial color="#e2e8f0" roughness={0.75} />
        </mesh>
        <mesh position={[0.006, 0, -wallH / 2 + 0.02]} receiveShadow>
          <boxGeometry args={[0.028, roomD, 0.04]} />
          <meshStandardMaterial color="#64748b" roughness={0.5} />
        </mesh>

        {/* 2 Windows */}
        {[-0.45, 0.45].map((wy, idx) => (
          <group key={idx} position={[0.005, wy, 0.08]}>
            <mesh castShadow>
              <boxGeometry args={[0.03, 0.45, 0.36]} />
              <meshStandardMaterial color="#1e293b" roughness={0.4} />
            </mesh>
            <mesh position={[0.002, 0, 0]}>
              <boxGeometry args={[0.004, 0.41, 0.32]} />
              <meshPhysicalMaterial color="#e0f2fe" transmission={0.85} transparent opacity={0.8} roughness={0.05} ior={1.5} />
            </mesh>
            <mesh position={[0.006, 0, 0]}>
              <boxGeometry args={[0.012, 0.41, 0.014]} />
              <meshStandardMaterial color="#334155" roughness={0.4} />
            </mesh>
            <mesh position={[0.006, 0, 0]}>
              <boxGeometry args={[0.012, 0.014, 0.32]} />
              <meshStandardMaterial color="#334155" roughness={0.4} />
            </mesh>
            <mesh position={[0.025, 0, -0.19]} castShadow receiveShadow>
              <boxGeometry args={[0.06, 0.50, 0.025]} />
              <meshStandardMaterial color="#cbd5e1" roughness={0.3} />
            </mesh>
          </group>
        ))}
      </group>

      {/* --- WALL 3: RIGHT WALL (X = +1.30) --- */}
      <group position={[roomW / 2, 0, floorZ + wallH / 2]}>
        <mesh receiveShadow>
          <boxGeometry args={[0.02, roomD, wallH]} />
          <meshStandardMaterial color="#f8fafc" roughness={0.85} />
        </mesh>
        <mesh position={[-0.002, 0, -wallH / 2 + 0.12]} receiveShadow>
          <boxGeometry args={[0.022, roomD, 0.24]} />
          <meshStandardMaterial color="#e2e8f0" roughness={0.75} />
        </mesh>
        <mesh position={[-0.006, 0, -wallH / 2 + 0.02]} receiveShadow>
          <boxGeometry args={[0.028, roomD, 0.04]} />
          <meshStandardMaterial color="#64748b" roughness={0.5} />
        </mesh>
        {/* Periodic Table Chart */}
        <mesh position={[-0.012, 0.0, 0.08]} receiveShadow>
          <boxGeometry args={[0.010, 0.65, 0.32]} />
          <meshStandardMaterial color="#2563eb" roughness={0.5} />
        </mesh>
        <Text position={[-0.020, 0.0, 0.08]} rotation={[0, -Math.PI / 2, 0]} fontSize={0.014} color="#ffffff" anchorX="center">
          PERIODIC TABLE OF ELEMENTS
        </Text>
      </group>

      {/* --- WALL 4: FRONT WALL (Y = -1.10) --- */}
      <group position={[0, -roomD / 2, floorZ + wallH / 2]}>
        <mesh position={[0, 0, -wallH / 2 + 0.08]} receiveShadow>
          <boxGeometry args={[roomW, 0.02, 0.16]} />
          <meshStandardMaterial color="#e2e8f0" roughness={0.85} />
        </mesh>
        <mesh position={[0, 0.006, -wallH / 2 + 0.02]} receiveShadow>
          <boxGeometry args={[roomW, 0.028, 0.04]} />
          <meshStandardMaterial color="#64748b" roughness={0.5} />
        </mesh>
      </group>

      {/* --- MULTI-COLOR TILED FLOOR (Click on floor to walk) --- */}
      <mesh
        position={[0, 0, floorZ - 0.005]}
        receiveShadow
        onClick={(e) => {
          e.stopPropagation();
          onMovePlayer(e.point.x, e.point.y);
        }}
      >
        <boxGeometry args={[roomW + 0.02, roomD + 0.02, 0.01]} />
        <meshStandardMaterial color="#334155" roughness={0.8} />
      </mesh>

      {floorTiles.map((tile) => (
        <mesh
          key={tile.id}
          position={[tile.x, tile.y, floorZ]}
          receiveShadow
          onClick={(e) => {
            e.stopPropagation();
            onMovePlayer(tile.x, tile.y);
          }}
        >
          <boxGeometry args={[tile.w, tile.d, 0.004]} />
          <meshStandardMaterial color={tile.color} roughness={tile.roughness} metalness={0.06} />
        </mesh>
      ))}

      {/* ========================================================================= */}
      {/* 2. THE 3 LAB WORKSTATIONS IN THE GAME WORLD                               */}
      {/* ========================================================================= */}

      {/* ------------------------------------------------------------------------- */}
      {/* STATION 1: OPTICS BENCH (Prism Experiment Table at X = -0.15, Y = 0.0)    */}
      {/* ------------------------------------------------------------------------- */}
      <group
        position={[-0.15, 0.0, 0.0]}
        onClick={(e) => {
          e.stopPropagation();
          onSelectStation('optics');
        }}
      >
        {/* Wooden Bench (Solid Oak) */}
        <mesh position={[0, 0, -0.010]} castShadow receiveShadow name="prism-table">
          <boxGeometry args={[0.54, 0.38, 0.020]} />
          <meshStandardMaterial
            color={activeStation === 'optics' ? '#d97706' : '#a16207'}
            roughness={0.4}
            metalness={0.05}
          />
        </mesh>
        <mesh position={[0, 0, -0.028]} castShadow receiveShadow>
          <boxGeometry args={[0.48, 0.32, 0.018]} />
          <meshStandardMaterial color="#854d0e" roughness={0.5} />
        </mesh>
        {[
          [-0.22, -0.14],
          [0.22, -0.14],
          [-0.22, 0.14],
          [0.22, 0.14],
        ].map(([lx, ly], idx) => (
          <mesh key={idx} position={[lx, ly, floorZ + (tableH - 0.02) / 2]} castShadow receiveShadow>
            <boxGeometry args={[0.024, 0.024, tableH - 0.02]} />
            <meshStandardMaterial color="#78350f" roughness={0.55} />
          </mesh>
        ))}

        {/* White Drawing Sheet Pinned to Table */}
        <mesh position={[0, 0, 0.001]} receiveShadow>
          <boxGeometry args={[0.38, 0.28, 0.0015]} />
          <meshStandardMaterial color="#fdfbf7" roughness={0.9} />
        </mesh>

        {/* Glass Prism (Schott N-BK7 Crown Glass) */}
        <mesh
          position={[0, 0, 0.002]}
          castShadow
          receiveShadow
          name="prism-glass-body"
          onClick={(e) => {
            e.stopPropagation();
            onSelectPart('prism-glass-body');
          }}
        >
          <extrudeGeometry args={[prismShape, { depth: prismH, bevelEnabled: true, bevelSegments: 3, steps: 1, bevelSize: 0.0015, bevelThickness: 0.0015 }]} />
          <meshPhysicalMaterial
            color={selectedPart === 'prism-glass-body' ? '#bae6fd' : '#f0f9ff'}
            transmission={0.96}
            opacity={1.0}
            transparent
            roughness={0.015}
            ior={1.517}
            thickness={0.085}
            specularIntensity={1.0}
            clearcoat={1.0}
            attenuationColor={new THREE.Color('#e0f2fe')}
            emissive={selectedPart === 'prism-glass-body' ? new THREE.Color('#38bdf8') : new THREE.Color('#000000')}
            emissiveIntensity={selectedPart === 'prism-glass-body' ? 0.35 : 0.0}
          />
        </mesh>

        <Text position={[0, yApex + 0.012, prismH + 0.006]} fontSize={0.009} color="#0369a1" anchorX="center">
          Glass Prism (A = 60°)
        </Text>

        {/* White Light Torch on Laboratory Stand */}
        {prismStep >= 2 && (
          <group position={[-0.14, -0.045, 0.03]} rotation={[0, 0, THREE.MathUtils.degToRad(18)]} name="prism-torch">
            <mesh position={[-0.035, 0, 0]} rotation={[0, Math.PI / 2, 0]} castShadow>
              <cylinderGeometry args={[0.009, 0.012, 0.065, 20]} />
              <meshStandardMaterial color="#1e293b" metalness={0.85} roughness={0.25} />
            </mesh>
            <mesh position={[0.008, 0, 0]} rotation={[0, Math.PI / 2, 0]}>
              <cylinderGeometry args={[0.012, 0.012, 0.004, 20]} />
              <meshStandardMaterial color="#ffffff" emissive="#ffffff" emissiveIntensity={3.5} />
            </mesh>
            {/* White Incident Beam (i = 48 deg) */}
            <mesh position={[0.065, 0, 0]} rotation={[0, 0, Math.PI / 2]} name="prism-incident-ray">
              <cylinderGeometry args={[0.0022, 0.0028, 0.11, 16]} />
              <meshStandardMaterial color="#ffffff" emissive="#ffffff" emissiveIntensity={3.0} />
            </mesh>
            <Text position={[-0.035, 0, 0.022]} fontSize={0.0075} color="#0f172a">
              White Light Torch (i = 48°)
            </Text>
          </group>
        )}

        {/* Internal Refraction Paths (Step 3 & 4) */}
        {prismStep >= 3 && (
          <group>
            {spectrumData.map((ray, idx) => {
              const devAngle = THREE.MathUtils.degToRad(30.0 - ray.eDeg);
              const dX = Math.cos(devAngle) * 0.045;
              const dY = Math.sin(devAngle) * 0.045;
              return (
                <mesh key={idx} position={[-0.02 + dX / 2, -0.01 + dY / 2, 0.03]} rotation={[0, 0, devAngle * 0.4]}>
                  <cylinderGeometry args={[0.0011, 0.0011, 0.045, 12]} />
                  <meshStandardMaterial
                    color={prismStep === 3 ? '#fbbf24' : ray.hex}
                    emissive={prismStep === 3 ? '#f59e0b' : ray.hex}
                    emissiveIntensity={2.5}
                  />
                </mesh>
              );
            })}
          </group>
        )}

        {/* 7 Rainbow Dispersed Emergent Rays & Screen (Step 4) */}
        {prismStep === 4 && (
          <group>
            {spectrumData.map((ray, idx) => {
              const devAngle = THREE.MathUtils.degToRad(30.0 - ray.eDeg);
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
                    {ray.name}
                  </Text>
                </group>
              );
            })}
            {/* White Observation Screen */}
            <mesh position={[0.145, -0.045, 0.038]} rotation={[0, 0, THREE.MathUtils.degToRad(70)]} receiveShadow name="prism-screen">
              <boxGeometry args={[0.006, 0.095, 0.075]} />
              <meshStandardMaterial color="#ffffff" roughness={0.85} />
            </mesh>
            <Text position={[0.145, -0.045, 0.088]} fontSize={0.008} color="#0f172a" anchorX="center">
              Observation Screen
            </Text>
          </group>
        )}

        {/* 3D Floating Beacon & Interactive Prompt */}
        <group position={[0, 0, 0.16]}>
          <mesh>
            <sphereGeometry args={[0.008, 16, 16]} />
            <meshStandardMaterial color="#38bdf8" emissive="#38bdf8" emissiveIntensity={2.5} />
          </mesh>
          <Text position={[0, 0, 0.018]} fontSize={0.014} color="#38bdf8" anchorX="center" anchorY="bottom">
            📍 PRISM EXPERIMENT TABLE
          </Text>
          <Text position={[0, 0, 0.006]} fontSize={0.009} color="#e0f2fe" anchorX="center" anchorY="top">
            {prismStep === 1 && '⚡ Press [E] or Left-Click: Turn ON Torch'}
            {prismStep === 2 && '⚡ Press [E] or Left-Click: Trace Refraction'}
            {prismStep === 3 && '⚡ Press [E] or Left-Click: Disperse 7 Rainbow Colors'}
            {prismStep === 4 && '✨ 7 Colors Dispersed (VIBGYOR)! Press [E] to Restart'}
          </Text>
        </group>
      </group>

      {/* ------------------------------------------------------------------------- */}
      {/* STATION 2: CHEMISTRY BENCH (Right Table at X = +0.45, Y = 0.0)            */}
      {/* ------------------------------------------------------------------------- */}
      <group
        position={[0.45, 0.0, 0.0]}
        onClick={(e) => {
          e.stopPropagation();
          onSelectStation('chemistry');
        }}
      >
        {/* Wooden Bench */}
        <mesh position={[0, 0, -0.010]} castShadow receiveShadow>
          <boxGeometry args={[0.42, 0.32, 0.020]} />
          <meshStandardMaterial
            color={activeStation === 'chemistry' ? '#f59e0b' : '#a16207'}
            roughness={0.4}
            metalness={0.05}
          />
        </mesh>
        <mesh position={[0, 0, -0.028]} castShadow receiveShadow>
          <boxGeometry args={[0.36, 0.26, 0.018]} />
          <meshStandardMaterial color="#854d0e" roughness={0.5} />
        </mesh>
        {[
          [-0.16, -0.11],
          [0.16, -0.11],
          [-0.16, 0.11],
          [0.16, 0.11],
        ].map(([lx, ly], idx) => (
          <mesh key={idx} position={[lx, ly, floorZ + (tableH - 0.02) / 2]} castShadow receiveShadow>
            <boxGeometry args={[0.022, 0.022, tableH - 0.02]} />
            <meshStandardMaterial color="#78350f" roughness={0.55} />
          </mesh>
        ))}

        {/* Ceramic Safety Tile */}
        <mesh position={[-0.04, 0, 0.003]} receiveShadow>
          <boxGeometry args={[0.16, 0.16, 0.005]} />
          <meshStandardMaterial color="#e2e8f0" roughness={0.3} />
        </mesh>

        {/* Bunsen Burner */}
        <group position={[-0.04, 0, 0.006]}>
          <mesh position={[0, 0, 0.004]} castShadow>
            <cylinderGeometry args={[0.024, 0.026, 0.008, 20]} />
            <meshStandardMaterial color="#1e293b" metalness={0.8} roughness={0.3} />
          </mesh>
          <mesh position={[0, 0, 0.038]} castShadow>
            <cylinderGeometry args={[0.0055, 0.0055, 0.060, 20]} />
            <meshStandardMaterial color="#94a3b8" metalness={0.9} roughness={0.2} />
          </mesh>
          {/* Flame */}
          {burnStage !== 'unheated' && (
            <mesh position={[0, 0, 0.082]}>
              <coneGeometry args={[0.009, 0.032, 16]} />
              <meshStandardMaterial
                color={burnStage === 'burning' ? '#ffffff' : '#38bdf8'}
                emissive={burnStage === 'burning' ? '#ffffff' : '#0284c7'}
                emissiveIntensity={burnStage === 'burning' ? 5.0 : 3.0}
                transparent
                opacity={0.85}
              />
            </mesh>
          )}
        </group>

        {/* Watch Glass with MgO Powder */}
        <group position={[0.08, 0, 0.003]}>
          <mesh position={[0, 0, 0.003]} castShadow>
            <cylinderGeometry args={[0.025, 0.020, 0.005, 20]} />
            <meshPhysicalMaterial color="#ffffff" transmission={0.9} roughness={0.1} transparent opacity={0.8} />
          </mesh>
          {burnStage === 'collected' && (
            <mesh position={[0, 0, 0.006]}>
              <coneGeometry args={[0.015, 0.008, 16]} />
              <meshStandardMaterial color="#ffffff" roughness={0.9} emissive="#f8fafc" emissiveIntensity={0.5} />
            </mesh>
          )}
        </group>

        {/* Station Title Badge */}
        <Text position={[0, 0, 0.12]} fontSize={0.016} color={activeStation === 'chemistry' ? '#fbbf24' : '#cbd5e1'} anchorX="center">
          2. CHEMISTRY BENCH (Magnesium Burning)
        </Text>
      </group>

      {/* ------------------------------------------------------------------------- */}
      {/* STATION 3: BIOLOGY BENCH (Back Table at X = 0.0, Y = +0.55)               */}
      {/* ------------------------------------------------------------------------- */}
      <group
        position={[0.0, 0.55, 0.0]}
        onClick={(e) => {
          e.stopPropagation();
          onSelectStation('biology');
        }}
      >
        {/* Wooden Bench */}
        <mesh position={[0, 0, -0.010]} castShadow receiveShadow>
          <boxGeometry args={[0.42, 0.32, 0.020]} />
          <meshStandardMaterial
            color={activeStation === 'biology' ? '#f43f5e' : '#a16207'}
            roughness={0.4}
            metalness={0.05}
          />
        </mesh>
        <mesh position={[0, 0, -0.028]} castShadow receiveShadow>
          <boxGeometry args={[0.36, 0.26, 0.018]} />
          <meshStandardMaterial color="#854d0e" roughness={0.5} />
        </mesh>
        {[
          [-0.16, -0.11],
          [0.16, -0.11],
          [-0.16, 0.11],
          [0.16, 0.11],
        ].map(([lx, ly], idx) => (
          <mesh key={idx} position={[lx, ly, floorZ + (tableH - 0.02) / 2]} castShadow receiveShadow>
            <boxGeometry args={[0.022, 0.022, tableH - 0.02]} />
            <meshStandardMaterial color="#78350f" roughness={0.55} />
          </mesh>
        ))}

        {/* Anatomical Heart Model Base */}
        <mesh position={[0, 0, 0.008]} castShadow>
          <cylinderGeometry args={[0.035, 0.040, 0.014, 24]} />
          <meshStandardMaterial color="#334155" metalness={0.7} roughness={0.4} />
        </mesh>
        {/* Stylized Pulsating Organ */}
        <mesh position={[0, 0, 0.045]} castShadow>
          <sphereGeometry args={[0.028, 24, 24]} />
          <meshStandardMaterial color="#e11d48" roughness={0.3} emissive="#be123c" emissiveIntensity={0.6} />
        </mesh>

        {/* Station Title Badge */}
        <Text position={[0, 0, 0.12]} fontSize={0.016} color={activeStation === 'biology' ? '#fb7185' : '#cbd5e1'} anchorX="center">
          3. BIOLOGY BENCH (Heart & Circulation)
        </Text>
      </group>

      {/* ========================================================================= */}
      {/* 3. PLAYER SCIENTIST AVATAR (Visible only in 3rd-person observer mode)     */}
      {/* ========================================================================= */}
      {!isFPSMode && (
        <group ref={playerRef} position={[playerPosition[0], playerPosition[1], floorZ + 0.08]}>
          {/* Scientist Shadow Ring */}
          <mesh position={[0, 0, -0.075]}>
            <ringGeometry args={[0.02, 0.05, 24]} />
            <meshBasicMaterial color="#000000" opacity={0.35} transparent />
          </mesh>
          {/* Lab Coat Body */}
          <mesh position={[0, 0, 0]} castShadow>
            <capsuleGeometry args={[0.022, 0.065, 8, 16]} />
            <meshStandardMaterial color="#ffffff" roughness={0.4} />
          </mesh>
          {/* Scientist Head */}
          <mesh position={[0, 0, 0.058]} castShadow>
            <sphereGeometry args={[0.018, 16, 16]} />
            <meshStandardMaterial color="#fed7aa" roughness={0.5} />
          </mesh>
          {/* Safety Goggles */}
          <mesh position={[0, -0.012, 0.060]}>
            <boxGeometry args={[0.022, 0.008, 0.008]} />
            <meshStandardMaterial color="#0284c7" emissive="#0284c7" emissiveIntensity={1.0} />
          </mesh>
          {/* Player Name Badge */}
          <Text position={[0, 0, 0.095]} fontSize={0.013} color="#38bdf8" anchorX="center">
            Scientist (You)
          </Text>
        </group>
      )}
    </group>
  );
}

