import { useRef, useState, useEffect } from 'react';
import * as THREE from 'three';
import { useGLTF, Center } from '@react-three/drei';
import { useFrame } from '@react-three/fiber';

export interface MagnesiumBurningProps {
  burnStage: 'unheated' | 'heating' | 'burning' | 'collected';
  selectedPart: string | null;
  onSelectPart: (partName: string) => void;
}

export function MagnesiumBurningModel({
  burnStage,
  selectedPart,
  onSelectPart,
}: MagnesiumBurningProps) {
  const { scene } = useGLTF('/assets/magnesium-burning-setup.glb');
  const groupRef = useRef<THREE.Group>(null);
  const [hovered, setHovered] = useState<string | null>(null);

  // Dynamic flame flicker & burning dazzle pulse
  useFrame(({ clock }) => {
    if (groupRef.current) {
      const t = clock.getElapsedTime();
      scene.traverse((child) => {
        if ((child as THREE.Mesh).isMesh) {
          const mesh = child as THREE.Mesh;
          const name = mesh.name.toLowerCase();
          if (name.includes('flame')) {
            const flicker = 1.0 + 0.12 * Math.sin(t * 12.0) + 0.08 * Math.cos(t * 7.5);
            mesh.scale.set(flicker, flicker, flicker);
          } else if (name.includes('ribbon') && burnStage === 'burning') {
            const mat = mesh.material as THREE.MeshStandardMaterial;
            if (mat && mat.emissive) {
              const dazzle = 3.0 + 1.2 * Math.sin(t * 20.0);
              mat.emissiveIntensity = dazzle;
            }
          }
        }
      });
    }
  });

  useEffect(() => {
    scene.traverse((child) => {
      if ((child as THREE.Mesh).isMesh) {
        const mesh = child as THREE.Mesh;
        const name = mesh.name.toLowerCase();
        const mat = (mesh.material as THREE.MeshStandardMaterial).clone();
        mesh.material = mat;

        // 1. Flame visibility
        if (name.includes('flame')) {
          mesh.visible = burnStage !== 'unheated';
        }

        // 2. Ribbon material transitions
        if (name.includes('ribbon')) {
          if (burnStage === 'unheated') {
            mat.color = new THREE.Color(0xd1d5db); // Metallic silver
            mat.emissive = new THREE.Color(0x000000);
            mat.emissiveIntensity = 0.0;
          } else if (burnStage === 'heating') {
            mat.color = new THREE.Color(0xf97316); // Dull orange glow
            mat.emissive = new THREE.Color(0xea580c);
            mat.emissiveIntensity = 1.2;
          } else if (burnStage === 'burning') {
            mat.color = new THREE.Color(0xffffff); // Dazzling white combustion
            mat.emissive = new THREE.Color(0xffffff);
            mat.emissiveIntensity = 3.5;
          } else if (burnStage === 'collected') {
            mat.color = new THREE.Color(0x9ca3af); // Spent crumbly ash
            mat.emissive = new THREE.Color(0x000000);
            mat.emissiveIntensity = 0.0;
          }
        }

        // 3. MgO powder heap visibility
        if (name.includes('mgo-powder')) {
          mesh.visible = burnStage === 'burning' || burnStage === 'collected';
        }

        // 4. Highlight selected or hovered part
        const isTargetSelected =
          (selectedPart === 'chem-bunsen-burner' && (name.includes('burner') || name.includes('flame') || name.includes('stem') || name.includes('collar'))) ||
          (selectedPart === 'chem-magnesium-ribbon' && name.includes('ribbon')) ||
          (selectedPart === 'chem-tongs' && name.includes('tongs')) ||
          (selectedPart === 'chem-watch-glass' && (name.includes('watch-glass') || name.includes('mgo-powder'))) ||
          (selectedPart === 'chem-sandpaper' && name.includes('sandpaper'));

        const isTargetHovered = hovered && name.includes(hovered);

        if (isTargetSelected) {
          mat.emissive = new THREE.Color(0xfff388);
          mat.emissiveIntensity = 1.8;
        } else if (isTargetHovered) {
          mat.emissive = new THREE.Color(0x38bdf8);
          mat.emissiveIntensity = 0.8;
        }
      }
    });
  }, [scene, burnStage, selectedPart, hovered]);

  const handleMeshClick = (meshName: string) => {
    const name = meshName.toLowerCase();
    if (name.includes('burner') || name.includes('flame') || name.includes('stem') || name.includes('collar') || name.includes('hose')) {
      onSelectPart('chem-bunsen-burner');
    } else if (name.includes('ribbon')) {
      onSelectPart('chem-magnesium-ribbon');
    } else if (name.includes('tongs')) {
      onSelectPart('chem-tongs');
    } else if (name.includes('watch-glass') || name.includes('mgo-powder')) {
      onSelectPart('chem-watch-glass');
    } else if (name.includes('sandpaper')) {
      onSelectPart('chem-sandpaper');
    } else {
      onSelectPart('chem-bunsen-burner');
    }
  };

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
            handleMeshClick(e.object.name);
          }}
        />
      </Center>
    </group>
  );
}

useGLTF.preload('/assets/magnesium-burning-setup.glb');
