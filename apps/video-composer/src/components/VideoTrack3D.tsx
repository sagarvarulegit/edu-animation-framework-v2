import React from 'react';
import { OffthreadVideo, staticFile, useCurrentFrame, interpolate } from 'remotion';

interface VideoTrack3DProps {
  src: string;
  playbackRate?: number;
  label?: string;
  zoomEffect?: boolean;
}

export const VideoTrack3D: React.FC<VideoTrack3DProps> = ({
  src,
  playbackRate = 1,
  label = 'Physical Experiment — 3D Blender Simulation',
  zoomEffect = true
}) => {
  const frame = useCurrentFrame();

  // Subtle cinematic slow zoom
  const scale = zoomEffect
    ? interpolate(frame, [0, 300], [1.0, 1.05], { extrapolateRight: 'clamp' })
    : 1.0;

  return (
    <div className="absolute inset-0 overflow-hidden bg-slate-950 flex items-center justify-center">
      {/* 3D Render Video */}
      <div
        style={{ transform: `scale(${scale})` }}
        className="relative h-full w-full flex items-center justify-center transition-transform"
      >
        <OffthreadVideo
          src={src.startsWith('http') || src.startsWith('/') ? src : staticFile(src)}
          playbackRate={playbackRate}
          className="h-full w-full object-contain"
        />
      </div>

      {/* Cinematic Vignette Overlay */}
      <div className="pointer-events-none absolute inset-0 bg-radial from-transparent via-slate-950/20 to-slate-950/80" />

      {/* Top Subtle Status Badge */}
      <div className="absolute top-6 left-8 flex items-center gap-2 rounded-full border border-slate-700/60 bg-slate-900/80 px-4 py-1.5 backdrop-blur-md">
        <div className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
        <span className="text-xs font-semibold tracking-wider uppercase text-slate-300">
          {label}
        </span>
      </div>
    </div>
  );
};
