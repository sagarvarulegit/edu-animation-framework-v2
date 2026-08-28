import { useRef, useState, useMemo } from 'react';
import * as THREE from 'three';
import { useFrame } from '@react-three/fiber';
import { Text } from '@react-three/drei';

export interface PrismRefractionProps {
  step: 1 | 2 | 3 | 4; // 1: Room + Floor + Table with just Prism, 2: Torch On, 3: Refraction, 4: 7 Rainbow Colors
  selectedPart: string | null;
  onSelectPart: (partName: string) => void;
}

export function PrismRefractionModel({
  step,
  selectedPart,
  onSelectPart,
}: PrismRefractionProps) {
  const groupRef = useRef<THREE.Group>(null);
  const [hovered, setHovered] = useState<string | null>(null);

  // Coordinate Geometry Conventions
  // Table top surface is at Z = 0.0
  // Floor is at Z = -0.22
  const floorZ = -0.22;
  const tableH = 0.22; // Height from floor to tabletop

  // Room Dimensions
  const roomW = 1.8;   // X: -0.9 to +0.9
  const roomD = 1.6;   // Y: -0.8 to +0.8
  const wallH = 0.70;  // Z: floorZ to floorZ + wallH

  // Prism Dimensions
  const prismSide = 0.090; // 90mm equilateral side
  const prismH = 0.065;    // 65mm prism height
  const triH = (prismSide * Math.sqrt(3)) / 2;
  const yApex = (2 * triH) / 3 - 0.015;
  const yBase = -triH / 3 - 0.015;
  const xHalf = prismSide / 2;

  // Prism Vertices (Apex pointing +Y)
  const A: [number, number] = [0, yApex];
  const B: [number, number] = [-xHalf, yBase];
  const C: [number, number] = [xHalf, yBase];

  const rayZ = 0.035;

  // Incident Hit Point E on Face AB
  const tHit = 0.48;
  const E_pos = new THREE.Vector3(
    B[0] + tHit * (A[0] - B[0]),
    B[1] + tHit * (A[1] - B[1]),
    rayZ
  );

  const incAngle = THREE.MathUtils.degToRad(18);
  const dInc = new THREE.Vector3(Math.cos(incAngle), Math.sin(incAngle), 0).normalize();
  const torchPos = E_pos.clone().sub(dInc.clone().multiplyScalar(0.13));
  const screenPos = new THREE.Vector3(0.135, -0.045, rayZ);

  // 7 Spectral Colors Data (VIBGYOR)
  const spectrumData = [
    { name: 'Red', hex: '#ef4444', wavelength: '700nm', n: 1.513, eDeg: 49.8, label: 'R' },
    { name: 'Orange', hex: '#f97316', wavelength: '620nm', n: 1.515, eDeg: 50.3, label: 'O' },
    { name: 'Yellow', hex: '#eab308', wavelength: '580nm', n: 1.517, eDeg: 50.7, label: 'Y' },
    { name: 'Green', hex: '#22c55e', wavelength: '530nm', n: 1.520, eDeg: 51.4, label: 'G' },
    { name: 'Blue', hex: '#3b82f6', wavelength: '480nm', n: 1.525, eDeg: 52.5, label: 'B' },
    { name: 'Indigo', hex: '#6366f1', wavelength: '440nm', n: 1.529, eDeg: 53.4, label: 'I' },
    { name: 'Violet', hex: '#a855f7', wavelength: '400nm', n: 1.534, eDeg: 54.6, label: 'V' },
  ];

  const spectralRays = spectrumData.map((spec) => {
    const iRad = THREE.MathUtils.degToRad(48.0);
    const r1Rad = Math.asin(Math.sin(iRad) / spec.n);
    const r1Deg = THREE.MathUtils.radToDeg(r1Rad);

    const refAngle = THREE.MathUtils.degToRad(150.0 - 180.0 + r1Deg);
    const dRef = new THREE.Vector3(Math.cos(refAngle), Math.sin(refAngle), 0).normalize();

    const p1 = new THREE.Vector2(E_pos.x, E_pos.y);
    const p2 = p1.clone().add(new THREE.Vector2(dRef.x, dRef.y));
    const p3 = new THREE.Vector2(A[0], A[1]);
    const p4 = new THREE.Vector2(C[0], C[1]);
    const denom = (p1.x - p2.x) * (p3.y - p4.y) - (p1.y - p2.y) * (p3.x - p4.x);
    const tInter = ((p1.x - p3.x) * (p3.y - p4.y) - (p1.y - p3.y) * (p3.x - p4.x)) / denom;
    const F_xy = p1.clone().add(new THREE.Vector2(dRef.x, dRef.y).multiplyScalar(tInter));
    const F_pos = new THREE.Vector3(F_xy.x, F_xy.y, rayZ);

    const emAngle = THREE.MathUtils.degToRad(30.0 - spec.eDeg);
    const dEm = new THREE.Vector3(Math.cos(emAngle), Math.sin(emAngle), 0).normalize();
    const S_pos = F_pos.clone().add(dEm.clone().multiplyScalar(0.11));

    return {
      ...spec,
      F_pos,
      S_pos,
      dRef,
      dEm,
    };
  });

  // Dynamic light emission pulse
  useFrame(({ clock }) => {
    if (groupRef.current) {
      const t = clock.getElapsedTime();
      const pulse = 1.0 + 0.08 * Math.sin(t * 5.0);
      groupRef.current.traverse((child) => {
        if ((child as THREE.Mesh).isMesh) {
          const mesh = child as THREE.Mesh;
          if (mesh.name.startsWith('ray-') || mesh.name.startsWith('band-')) {
            const mat = mesh.material as THREE.MeshStandardMaterial;
            if (mat && mat.emissive) {
              mat.emissiveIntensity = pulse * 2.2;
            }
          }
        }
      });
    }
  });

  // Extrude equilateral prism shape
  const prismShape = useMemo(() => {
    const shape = new THREE.Shape();
    shape.moveTo(B[0], B[1]);
    shape.lineTo(C[0], C[1]);
    shape.lineTo(A[0], A[1]);
    shape.closePath();
    return shape;
  }, []);

  // Multi-Color Floor Tiles Generator (Alternating Slate Grey & Ivory White Lab Tiles)
  const floorTiles = useMemo(() => {
    const tiles = [];
    const numX = 10;
    const numY = 8;
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
      {/* 1. SCIENCE LAB ROOM: 4 WALLS + ARCHITECTURAL WINDOW                       */}
      {/* ========================================================================= */}
      
      {/* --- WALL 1: BACK WALL (Y = +0.80) --- */}
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
        {/* Science Lab Chalkboard on Back Wall */}
        <mesh position={[0, -0.012, 0.08]} receiveShadow>
          <boxGeometry args={[0.75, 0.010, 0.28]} />
          <meshStandardMaterial color="#064e3b" roughness={0.6} />
        </mesh>
        <mesh position={[0, -0.008, 0.08]}>
          <boxGeometry args={[0.77, 0.008, 0.30]} />
          <meshStandardMaterial color="#78350f" roughness={0.5} />
        </mesh>
        <Text position={[0, -0.020, 0.08]} fontSize={0.018} color="#ecfdf5" anchorX="center" anchorY="middle">
          PHYSICS LAB — SNELL'S LAW & DISPERSION
        </Text>
      </group>

      {/* --- WALL 2: LEFT WALL WITH ARCHITECTURAL WINDOW (X = -0.90) --- */}
      <group position={[-roomW / 2, 0, floorZ + wallH / 2]}>
        <mesh position={[0, 0, 0]} receiveShadow>
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

        {/* The Window Frame & Glass */}
        <group position={[0.005, 0.0, 0.08]}>
          <mesh position={[0, 0, 0]} castShadow>
            <boxGeometry args={[0.03, 0.52, 0.38]} />
            <meshStandardMaterial color="#1e293b" roughness={0.4} />
          </mesh>
          <mesh position={[0.002, 0, 0]}>
            <boxGeometry args={[0.004, 0.48, 0.34]} />
            <meshPhysicalMaterial
              color="#e0f2fe"
              transmission={0.85}
              transparent
              opacity={0.8}
              roughness={0.05}
              ior={1.5}
            />
          </mesh>
          <mesh position={[0.006, 0, 0]}>
            <boxGeometry args={[0.012, 0.48, 0.016]} />
            <meshStandardMaterial color="#334155" roughness={0.4} />
          </mesh>
          <mesh position={[0.006, 0, 0]}>
            <boxGeometry args={[0.012, 0.016, 0.34]} />
            <meshStandardMaterial color="#334155" roughness={0.4} />
          </mesh>
          <mesh position={[0.025, 0, -0.20]} castShadow receiveShadow>
            <boxGeometry args={[0.06, 0.58, 0.025]} />
            <meshStandardMaterial color="#cbd5e1" roughness={0.3} />
          </mesh>
        </group>
      </group>

      {/* --- WALL 3: RIGHT WALL (X = +0.90) --- */}
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
        <mesh position={[-0.012, 0.05, 0.06]} receiveShadow>
          <boxGeometry args={[0.010, 0.45, 0.30]} />
          <meshStandardMaterial color="#3b82f6" roughness={0.5} />
        </mesh>
      </group>

      {/* --- WALL 4: FRONT WALL (Y = -0.80) --- */}
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

      {/* ========================================================================= */}
      {/* 2. MULTI-COLOR TILED FLOOR (Alternating Slate Grey & Ivory White Tiles)   */}
      {/* ========================================================================= */}
      <mesh position={[0, 0, floorZ - 0.005]} receiveShadow>
        <boxGeometry args={[roomW + 0.02, roomD + 0.02, 0.01]} />
        <meshStandardMaterial color="#334155" roughness={0.8} />
      </mesh>

      {floorTiles.map((tile) => (
        <mesh
          key={tile.id}
          position={[tile.x, tile.y, floorZ]}
          receiveShadow
        >
          <boxGeometry args={[tile.w, tile.d, 0.004]} />
          <meshStandardMaterial
            color={tile.color}
            roughness={tile.roughness}
            metalness={0.06}
          />
        </mesh>
      ))}

      {/* ========================================================================= */}
      {/* 3. THE WOODEN LABORATORY TABLE (Oak Top + 4 Perpendicular Legs)          */}
      {/* ========================================================================= */}
      <mesh
        position={[0.02, 0.0, -0.010]}
        receiveShadow
        castShadow
        onClick={(e) => {
          e.stopPropagation();
          onSelectPart('table-wood');
        }}
      >
        <boxGeometry args={[0.46, 0.34, 0.020]} />
        <meshStandardMaterial
          color="#a16207"
          roughness={0.4}
          metalness={0.05}
        />
      </mesh>

      <mesh position={[0.02, 0.0, -0.028]} castShadow receiveShadow>
        <boxGeometry args={[0.40, 0.28, 0.018]} />
        <meshStandardMaterial color="#854d0e" roughness={0.5} />
      </mesh>

      {[
        [-0.17, -0.13],
        [0.21, -0.13],
        [-0.17, 0.13],
        [0.21, 0.13],
      ].map(([lx, ly], idx) => (
        <mesh
          key={idx}
          position={[lx, ly, floorZ + (tableH - 0.02) / 2]}
          castShadow
          receiveShadow
        >
          <boxGeometry args={[0.022, 0.022, tableH - 0.02]} />
          <meshStandardMaterial color="#78350f" roughness={0.55} />
        </mesh>
      ))}

      {/* ========================================================================= */}
      {/* 4. THE GLASS PRISM (Kept cleanly on the table)                            */}
      {/* ========================================================================= */}
      <mesh
        position={[0, 0, 0.0005]}
        castShadow
        receiveShadow
        onClick={(e) => {
          e.stopPropagation();
          onSelectPart('prism-glass-body');
        }}
        onPointerOver={(e) => {
          e.stopPropagation();
          setHovered('prism-glass-body');
        }}
        onPointerOut={() => setHovered(null)}
      >
        <extrudeGeometry
          args={[
            prismShape,
            { depth: prismH, bevelEnabled: true, bevelSegments: 3, steps: 1, bevelSize: 0.0015, bevelThickness: 0.0015 },
          ]}
        />
        <meshPhysicalMaterial
          color={selectedPart === 'prism-glass-body' ? '#bae6fd' : (hovered === 'prism-glass-body' ? '#e0f2fe' : '#f0f9ff')}
          transmission={0.96}
          opacity={1.0}
          transparent={true}
          roughness={0.015}
          ior={1.517}
          thickness={0.085}
          specularIntensity={1.0}
          specularColor={new THREE.Color('#ffffff')}
          clearcoat={1.0}
          clearcoatRoughness={0.02}
          attenuationColor={new THREE.Color('#e0f2fe')}
          attenuationDistance={0.2}
          emissive={selectedPart === 'prism-glass-body' ? new THREE.Color('#38bdf8') : (hovered === 'prism-glass-body' ? new THREE.Color('#0284c7') : new THREE.Color('#000000'))}
          emissiveIntensity={selectedPart === 'prism-glass-body' ? 0.3 : (hovered === 'prism-glass-body' ? 0.15 : 0.0)}
        />
      </mesh>

      <Text
        position={[A[0], A[1] + 0.014, prismH + 0.006]}
        fontSize={0.010}
        color="#0369a1"
        anchorX="center"
        anchorY="bottom"
      >
        Glass Prism (A = 60°)
      </Text>

      {/* ========================================================================= */}
      {/* 5. APPARATUS FOR STEPS 2, 3, 4: TORCH, BEAM, RAINBOW, SCREEN              */}
      {/* ========================================================================= */}
      {step >= 2 && (
        <group
          position={[torchPos.x, torchPos.y, rayZ]}
          rotation={[0, 0, incAngle]}
          onClick={(e) => {
            e.stopPropagation();
            onSelectPart('prism-incident-ray');
          }}
        >
          <mesh position={[-0.035, 0, 0]} rotation={[0, Math.PI / 2, 0]} castShadow>
            <cylinderGeometry args={[0.010, 0.012, 0.065, 24]} />
            <meshStandardMaterial color="#1e293b" metalness={0.8} roughness={0.3} />
          </mesh>
          <mesh position={[0.003, 0, 0]} rotation={[0, Math.PI / 2, 0]}>
            <cylinderGeometry args={[0.014, 0.010, 0.015, 24]} />
            <meshStandardMaterial color="#e2e8f0" metalness={0.95} roughness={0.15} />
          </mesh>
          <mesh position={[0.010, 0, 0]} rotation={[0, Math.PI / 2, 0]}>
            <cylinderGeometry args={[0.012, 0.012, 0.003, 24]} />
            <meshStandardMaterial color="#ffffff" emissive="#ffffff" emissiveIntensity={3.5} />
          </mesh>
          <Text position={[-0.035, 0, 0.022]} fontSize={0.008} color="#0f172a">
            White Light Torch
          </Text>
        </group>
      )}

      {step >= 2 && (
        <group>
          {(() => {
            const diff = E_pos.clone().sub(torchPos);
            const center = torchPos.clone().add(E_pos).multiplyScalar(0.5);
            const rotQuat = new THREE.Quaternion().setFromUnitVectors(
              new THREE.Vector3(0, 1, 0),
              diff.clone().normalize()
            );
            return (
              <mesh position={center} quaternion={rotQuat} name="ray-incident">
                <cylinderGeometry args={[0.0022, 0.0028, diff.length(), 16]} />
                <meshStandardMaterial color="#ffffff" emissive="#ffffff" emissiveIntensity={2.8} />
              </mesh>
            );
          })()}

          <Text
            position={[E_pos.x - 0.04, E_pos.y - 0.025, rayZ + 0.018]}
            fontSize={0.0085}
            color="#0f172a"
          >
            White Light Beam (i = 48°)
          </Text>
        </group>
      )}

      {step >= 3 && (
        <group>
          {spectralRays.map((ray, idx) => {
            const diff = ray.F_pos.clone().sub(E_pos);
            const center = E_pos.clone().add(ray.F_pos).multiplyScalar(0.5);
            const rotQuat = new THREE.Quaternion().setFromUnitVectors(
              new THREE.Vector3(0, 1, 0),
              diff.clone().normalize()
            );
            return (
              <mesh key={idx} position={center} quaternion={rotQuat} name={`ray-refracted-${ray.name}`}>
                <cylinderGeometry args={[0.0011, 0.0011, diff.length(), 12]} />
                <meshStandardMaterial
                  color={step === 3 ? '#fbbf24' : ray.hex}
                  emissive={step === 3 ? '#f59e0b' : ray.hex}
                  emissiveIntensity={2.5}
                />
              </mesh>
            );
          })}
        </group>
      )}

      {step === 4 && (
        <group>
          <group position={[screenPos.x, screenPos.y, 0]}>
            <mesh position={[0, 0, 0.003]} castShadow>
              <boxGeometry args={[0.020, 0.085, 0.006]} />
              <meshStandardMaterial color="#334155" roughness={0.5} />
            </mesh>
            <mesh
              position={[0, 0, 0.038]}
              rotation={[0, 0, THREE.MathUtils.degToRad(70)]}
              receiveShadow
            >
              <boxGeometry args={[0.006, 0.090, 0.070]} />
              <meshStandardMaterial color="#ffffff" roughness={0.85} />
            </mesh>
            <Text position={[0, 0, 0.082]} fontSize={0.008} color="#0f172a" anchorX="center">
              Observation Screen
            </Text>
          </group>

          {spectralRays.map((ray, idx) => {
            const diff = ray.S_pos.clone().sub(ray.F_pos);
            const center = ray.F_pos.clone().add(ray.S_pos).multiplyScalar(0.5);
            const rotQuat = new THREE.Quaternion().setFromUnitVectors(
              new THREE.Vector3(0, 1, 0),
              diff.clone().normalize()
            );
            return (
              <group key={idx}>
                <mesh position={center} quaternion={rotQuat} name={`ray-emergent-${ray.name}`}>
                  <cylinderGeometry args={[0.0014, 0.0016, diff.length(), 16]} />
                  <meshStandardMaterial color={ray.hex} emissive={ray.hex} emissiveIntensity={3.0} />
                </mesh>

                <mesh position={[ray.S_pos.x - 0.002, ray.S_pos.y, rayZ]} name={`band-${ray.name}`}>
                  <boxGeometry args={[0.002, 0.006, 0.008]} />
                  <meshStandardMaterial color={ray.hex} emissive={ray.hex} emissiveIntensity={3.5} />
                </mesh>

                <Text
                  position={[ray.S_pos.x + 0.008, ray.S_pos.y, rayZ + 0.014]}
                  fontSize={0.0065}
                  color={ray.hex}
                  anchorX="left"
                >
                  {ray.label} ({ray.name})
                </Text>
              </group>
            );
          })}
        </group>
      )}
    </group>
  );
}