import { useRef, useState, useEffect } from 'react';
import * as THREE from 'three';
import { useGLTF, Center } from '@react-three/drei';
import { useFrame } from '@react-three/fiber';

export interface HeartProps {
  activeCircuit: 'all' | 'pulmonary' | 'systemic';
  selectedPart: string | null;
  onSelectPart: (partName: string) => void;
}

export function HeartModel({ activeCircuit, selectedPart, onSelectPart }: HeartProps) {
  const { scene } = useGLTF('/assets/human-heart.glb');
  const groupRef = useRef<THREE.Group>(null);
  const [hovered, setHovered] = useState<string | null>(null);

  // Subtle natural cardiac idle pulse animation
  useFrame(({ clock }) => {
    if (groupRef.current) {
      const t = clock.getElapsedTime();
      // Cardiac cycle beat: quick lub-dub contraction
      const beat = Math.sin(t * 4.5) * Math.pow(Math.sin(t * 2.25), 4) * 0.035;
      groupRef.current.scale.set(1 + beat, 1 + beat * 1.2, 1 + beat);
    }
  });

  useEffect(() => {
    scene.traverse((child) => {
      if ((child as THREE.Mesh).isMesh) {
        const mesh = child as THREE.Mesh;
        const name = mesh.name.toLowerCase();
        const mat = (mesh.material as THREE.MeshStandardMaterial).clone();
        mesh.material = mat;

        const isOxy = name.includes('left') || name.includes('aorta') || name.includes('pulmonary-vein');
        const isDeoxy = name.includes('right') || name.includes('cava') || name.includes('pulmonary-artery') || name.includes('pulmonary-trunk');

        // Apply circuit opacity filtering
        if (activeCircuit === 'pulmonary') {
          if (isDeoxy) {
            mat.opacity = 1.0;
            mat.transparent = false;
          } else {
            mat.opacity = 0.15;
            mat.transparent = true;
          }
        } else if (activeCircuit === 'systemic') {
          if (isOxy) {
            mat.opacity = 1.0;
            mat.transparent = false;
          } else {
            mat.opacity = 0.15;
            mat.transparent = true;
          }
        } else {
          mat.opacity = 1.0;
          mat.transparent = false;
        }

        // Highlight selected or hovered part
        if (mesh.name === selectedPart) {
          mat.emissive = new THREE.Color(0xfff388);
          mat.emissiveIntensity = 0.45;
        } else if (mesh.name === hovered) {
          mat.emissive = new THREE.Color(0x38bdf8);
          mat.emissiveIntensity = 0.3;
        } else {
          mat.emissive = new THREE.Color(0x000000);
          mat.emissiveIntensity = 0.0;
        }
      }
    });
  }, [scene, activeCircuit, selectedPart, hovered]);

  return (
    <group ref={groupRef}>
      <Center top>
        <primitive
          object={scene}
          onPointerOver={(e: any) => {
            e.stopPropagation();
            setHovered(e.object.name);
          }}
          onPointerOut={(e: any) => {
            e.stopPropagation();
            setHovered(null);
          }}
          onClick={(e: any) => {
            e.stopPropagation();
            onSelectPart(e.object.name);
          }}
        />
      </Center>
    </group>
  );
}

useGLTF.preload('/assets/human-heart.glb');
