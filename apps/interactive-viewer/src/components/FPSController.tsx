import { useEffect, useRef } from 'react';
import * as THREE from 'three';
import { useThree, useFrame } from '@react-three/fiber';

export interface FPSControllerProps {
  playerPosition: [number, number];
  onMovePlayer: (x: number, y: number) => void;
  isFPSMode: boolean;
  onInteract: () => void;
  onAimApparatus?: (name: string | null) => void;
}

export function FPSController({
  playerPosition,
  onMovePlayer,
  isFPSMode,
  onInteract,
  onAimApparatus,
}: FPSControllerProps) {
  const { camera, gl, scene } = useThree();
  const keys = useRef<{ [key: string]: boolean }>({});
  const isPointerLocked = useRef(false);

  // Pure Left/Right (Yaw) and Up/Down (Pitch) angles
  // yaw = 0 faces forward (+Y towards the physics chalkboard)
  const yaw = useRef(0.0);
  const pitch = useRef(0.0);

  const raycaster = useRef(new THREE.Raycaster());
  const walkTime = useRef(0);

  // Eye height in the Science Lab relative to floor (Z = -0.22 -> Eye Z = 0.08)
  const eyeHeight = 0.08;

  // Initialize camera orientation
  useEffect(() => {
    if (isFPSMode) {
      camera.up.set(0, 0, 1);
      camera.position.set(playerPosition[0], playerPosition[1], eyeHeight);
      yaw.current = 0.0;
      pitch.current = 0.0;
      camera.lookAt(playerPosition[0], playerPosition[1] + 1.0, eyeHeight);
    }
  }, [isFPSMode]);

  // Keyboard Event Listeners (WASD + Arrows + E Interact)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      keys.current[e.key.toLowerCase()] = true;
      if (e.key.toLowerCase() === 'e') {
        onInteract();
      }
    };
    const handleKeyUp = (e: KeyboardEvent) => {
      keys.current[e.key.toLowerCase()] = false;
    };

    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
    };
  }, [onInteract]);

  // Pointer Lock & Mouse Look Listeners (Left/Right & Up/Down Look)
  useEffect(() => {
    const domElement = gl.domElement;

    const handlePointerLockChange = () => {
      isPointerLocked.current = document.pointerLockElement === domElement;
    };

    const handleMouseMove = (e: MouseEvent) => {
      if (!isFPSMode) return;
      if (document.pointerLockElement !== domElement && (e.buttons & 1) === 0) return;

      const movementX = e.movementX || 0;
      const movementY = e.movementY || 0;

      // Look Left / Right (Yaw around vertical Z axis)
      yaw.current -= movementX * 0.0028;

      // Look Up / Down (Pitch tilt)
      pitch.current -= movementY * 0.0024;

      // Clamp vertical look strictly (-80 deg looking down at floor to +80 deg looking up at ceiling)
      pitch.current = Math.max(-1.40, Math.min(1.40, pitch.current));
    };

    const handleClick = () => {
      if (isFPSMode && document.pointerLockElement !== domElement) {
        domElement.requestPointerLock?.();
      }
    };

    document.addEventListener('pointerlockchange', handlePointerLockChange);
    window.addEventListener('mousemove', handleMouseMove);
    domElement.addEventListener('click', handleClick);

    return () => {
      document.removeEventListener('pointerlockchange', handlePointerLockChange);
      window.removeEventListener('mousemove', handleMouseMove);
      domElement.removeEventListener('click', handleClick);
    };
  }, [isFPSMode, gl]);

  // Game Loop: Pure FPS Movement (Front/Back/Left/Right) & Look (Left/Right/Up/Down)
  useFrame((_, delta) => {
    if (!isFPSMode) return;

    let [px, py] = playerPosition;
    const moveSpeed = 1.35 * delta;

    // Unit direction vectors relative to current horizontal facing angle (yaw)
    // Forward Vector (Front / Back)
    const forwardX = -Math.sin(yaw.current);
    const forwardY = Math.cos(yaw.current);

    // Right Vector (Left / Right strafe)
    const rightX = Math.cos(yaw.current);
    const rightY = Math.sin(yaw.current);

    let isMoving = false;

    // Front (W / Up Arrow)
    if (keys.current['w'] || keys.current['arrowup']) {
      px += forwardX * moveSpeed;
      py += forwardY * moveSpeed;
      isMoving = true;
    }
    // Back (S / Down Arrow)
    if (keys.current['s'] || keys.current['arrowdown']) {
      px -= forwardX * moveSpeed;
      py -= forwardY * moveSpeed;
      isMoving = true;
    }
    // Right (D / Right Arrow)
    if (keys.current['d'] || keys.current['arrowright']) {
      px += rightX * moveSpeed;
      py += rightY * moveSpeed;
      isMoving = true;
    }
    // Left (A / Left Arrow)
    if (keys.current['a'] || keys.current['arrowleft']) {
      px -= rightX * moveSpeed;
      py -= rightY * moveSpeed;
      isMoving = true;
    }

    // Physical Lab Room Perimeter Boundaries (inside walls)
    px = Math.max(-1.18, Math.min(1.18, px));
    py = Math.max(-0.98, Math.min(0.98, py));

    if (isMoving) {
      walkTime.current += delta;
      onMovePlayer(px, py);
    }

    // Subtle natural head bob while walking
    const headBob = isMoving ? Math.sin(walkTime.current * 13.0) * 0.0035 : 0;
    const currentZ = eyeHeight + headBob;

    // Calculate 3D Look Vector (Left/Right yaw + Up/Down pitch)
    const cosPitch = Math.cos(pitch.current);
    const dirX = -Math.sin(yaw.current) * cosPitch;
    const dirY = Math.cos(yaw.current) * cosPitch;
    const dirZ = Math.sin(pitch.current);

    camera.position.set(px, py, currentZ);
    camera.up.set(0, 0, 1);
    camera.lookAt(px + dirX, py + dirY, currentZ + dirZ);

    // Crosshair Raycast to detect interactive apparatus
    if (onAimApparatus) {
      raycaster.current.set(
        new THREE.Vector3(px, py, currentZ),
        new THREE.Vector3(dirX, dirY, dirZ).normalize()
      );
      const intersects = raycaster.current.intersectObjects(scene.children, true);
      let detectedName: string | null = null;

      for (const hit of intersects) {
        if (hit.distance > 2.0) break;
        let obj: THREE.Object3D | null = hit.object;
        while (obj && obj !== scene) {
          if (obj.name && (obj.name.includes('prism') || obj.name.includes('torch') || obj.name.includes('ray') || obj.name.includes('burner') || obj.name.includes('table'))) {
            detectedName = obj.name;
            break;
          }
          obj = obj.parent;
        }
        if (detectedName) break;
      }
      onAimApparatus(detectedName);
    }
  });

  return null;
}


