import { useRef, useEffect, useMemo, Suspense, Component, type ReactNode } from 'react';
import * as THREE from 'three';
import { useFrame } from '@react-three/fiber';
import { Text, useGLTF } from '@react-three/drei';

interface StationGLBErrorBoundaryProps {
  fallback?: ReactNode;
  children: ReactNode;
}
interface StationGLBErrorBoundaryState {
  hasError: boolean;
}

class StationGLBErrorBoundary extends Component<StationGLBErrorBoundaryProps, StationGLBErrorBoundaryState> {
  state: StationGLBErrorBoundaryState = { hasError: false };
  static getDerivedStateFromError() {
    return { hasError: true };
  }
  componentDidCatch(error: any) {
    console.warn('Station GLB load error:', error);
  }
  render() {
    if (this.state.hasError) {
      return this.props.fallback || null;
    }
    return this.props.children;
  }
}

function LabStationGLB({
  modelPath,
  scale = 1,
  position = [0, 0, 0],
  rotation = [0, 0, 0],
  onClick,
}: {
  modelPath: string;
  scale?: number;
  position?: [number, number, number];
  rotation?: [number, number, number];
  onClick?: (e: any) => void;
}) {
  const { scene } = useGLTF(modelPath);
  const cloned = useMemo(() => {
    const c = scene.clone(true);
    c.traverse((child) => {
      if ((child as THREE.Mesh).isMesh) {
        child.castShadow = true;
        child.receiveShadow = true;
      }
    });
    const box = new THREE.Box3().setFromObject(c);
    const center = new THREE.Vector3();
    box.getCenter(center);
    // Center horizontally on X and Z, ground base at Y = 0 (in glTF space)
    c.position.set(-center.x, -box.min.y, -center.z);
    return c;
  }, [scene]);

  return (
    <group position={position} onClick={onClick}>
      {/* Transform from glTF Y-up to Game World Z-up */}
      <group rotation={[Math.PI / 2, 0, 0]}>
        <group rotation={rotation} scale={scale}>
          <primitive object={cloned} />
        </group>
      </group>
    </group>
  );
}

useGLTF.preload('/assets/glass-prism-refraction.glb');
useGLTF.preload('/assets/magnesium-burning-setup.glb');
useGLTF.preload('/assets/human-heart.glb');

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

        <StationGLBErrorBoundary>
          <Suspense fallback={null}>
            <LabStationGLB
              modelPath="/assets/glass-prism-refraction.glb"
              scale={0.72}
              position={[0, 0, 0.002]}
              onClick={(e) => {
                e.stopPropagation();
                onSelectStation('optics');
              }}
            />
          </Suspense>
        </StationGLBErrorBoundary>

        {/* 3D Floating Beacon & Interactive Prompt */}
        <group position={[0, 0, 0.22]}>
          <mesh>
            <sphereGeometry args={[0.008, 16, 16]} />
            <meshStandardMaterial color="#38bdf8" emissive="#38bdf8" emissiveIntensity={2.5} />
          </mesh>
          <Text position={[0, 0, 0.018]} fontSize={0.014} color="#38bdf8" anchorX="center" anchorY="bottom">
            📍 STATION 1: PRISM EXPERIMENT BENCH
          </Text>
          <Text position={[0, 0, 0.006]} fontSize={0.009} color="#e0f2fe" anchorX="center" anchorY="top">
            {prismStep === 1 && '⚡ Press [E] or Left-Click: Inspect Apparatus'}
            {prismStep === 2 && '⚡ Press [E] or Left-Click: Trace Refracted Ray'}
            {prismStep === 3 && '⚡ Press [E] or Left-Click: Observe 7 Colors (VIBGYOR)'}
            {prismStep === 4 && '✨ Refraction & Dispersion Verified! Press [E] to Restart'}
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

        <StationGLBErrorBoundary>
          <Suspense fallback={null}>
            <LabStationGLB
              modelPath="/assets/magnesium-burning-setup.glb"
              scale={0.72}
              position={[0, 0, 0.002]}
              onClick={(e) => {
                e.stopPropagation();
                onSelectStation('chemistry');
              }}
            />
          </Suspense>
        </StationGLBErrorBoundary>

        {/* Dynamic Combustion Flash Flare */}
        {burnStage === 'burning' && (
          <group position={[-0.04, 0, 0.08]}>
            <pointLight intensity={5.0} distance={1.5} color="#ffffff" />
            <mesh>
              <sphereGeometry args={[0.018, 16, 16]} />
              <meshBasicMaterial color="#ffffff" />
            </mesh>
          </group>
        )}

        {/* Station Title Badge */}
        <group position={[0, 0, 0.22]}>
          <mesh>
            <sphereGeometry args={[0.008, 16, 16]} />
            <meshStandardMaterial color="#f59e0b" emissive="#f59e0b" emissiveIntensity={2.5} />
          </mesh>
          <Text position={[0, 0, 0.018]} fontSize={0.014} color="#fbbf24" anchorX="center" anchorY="bottom">
            📍 STATION 2: CHEMISTRY BENCH (Magnesium Combustion)
          </Text>
          <Text position={[0, 0, 0.006]} fontSize={0.009} color="#fef3c7" anchorX="center" anchorY="top">
            Stage: {burnStage.toUpperCase()} — Press [E] or Left-Click to Heat & Burn
          </Text>
        </group>
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

        {/* Specimen Stand Pedestal */}
        <mesh position={[0, 0, 0.008]} castShadow>
          <cylinderGeometry args={[0.045, 0.050, 0.016, 32]} />
          <meshStandardMaterial color="#1e293b" metalness={0.8} roughness={0.25} />
        </mesh>
        <mesh position={[0, 0, 0.024]} castShadow>
          <cylinderGeometry args={[0.004, 0.004, 0.020, 16]} />
          <meshStandardMaterial color="#94a3b8" metalness={0.9} roughness={0.15} />
        </mesh>

        <StationGLBErrorBoundary>
          <Suspense fallback={null}>
            <LabStationGLB
              modelPath="/assets/human-heart.glb"
              scale={1.25}
              position={[0, 0, 0.035]}
              onClick={(e) => {
                e.stopPropagation();
                onSelectStation('biology');
              }}
            />
          </Suspense>
        </StationGLBErrorBoundary>

        {/* Station Title Badge */}
        <group position={[0, 0, 0.22]}>
          <mesh>
            <sphereGeometry args={[0.008, 16, 16]} />
            <meshStandardMaterial color="#f43f5e" emissive="#f43f5e" emissiveIntensity={2.5} />
          </mesh>
          <Text position={[0, 0, 0.018]} fontSize={0.014} color="#fb7185" anchorX="center" anchorY="bottom">
            📍 STATION 3: BIOLOGY BENCH (Human Heart Anatomy)
          </Text>
          <Text position={[0, 0, 0.006]} fontSize={0.009} color="#ffe4e6" anchorX="center" anchorY="top">
            Aorta, Ventricles, Coronary Arteries & Double Circulation
          </Text>
        </group>
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

