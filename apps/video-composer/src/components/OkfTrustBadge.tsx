import React from 'react';
import { spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { ShieldCheck, BookOpen, Layers } from 'lucide-react';
import { getOkfConcept } from '../data/generated/okfKnowledge';

export interface OkfTrustBadgeProps {
  conceptId: string;
  position?: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right';
  delayFrames?: number;
}

export const OkfTrustBadge: React.FC<OkfTrustBadgeProps> = ({
  conceptId,
  position = 'top-left',
  delayFrames = 0,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const concept = getOkfConcept(conceptId);
  if (!concept) return null;

  const currentFrame = Math.max(0, frame - delayFrames);
  const opacity = spring({
    frame: currentFrame,
    fps,
    config: { damping: 14, mass: 0.6, stiffness: 100 },
  });

  const translateY = spring({
    frame: currentFrame,
    fps,
    from: -20,
    to: 0,
    config: { damping: 12, mass: 0.6, stiffness: 120 },
  });

  const positionClasses = {
    'top-left': 'top-8 left-8',
    'top-right': 'top-8 right-8',
    'bottom-left': 'bottom-16 left-8',
    'bottom-right': 'bottom-16 right-8',
  }[position];

  const primarySource = concept.sources && concept.sources.length > 0 ? concept.sources[0] : null;

  return (
    <div
      style={{
        opacity,
        transform: `translateY(${translateY}px)`,
      }}
      className={`absolute ${positionClasses} z-30 flex items-center gap-3 rounded-2xl border border-slate-700/80 bg-slate-950/85 px-4 py-2.5 shadow-2xl backdrop-blur-xl font-sans`}
    >
      {/* Archetype & Trust Tier */}
      <div className="flex items-center gap-1.5 border-r border-slate-800 pr-3">
        <span className="rounded bg-cyan-950 px-1.5 py-0.5 text-[10px] font-extrabold uppercase tracking-wider text-cyan-400 border border-cyan-800/60 font-mono">
          {concept.type}
        </span>
        <span
          className={`flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-bold border ${
            concept.verified === 'human-reviewed'
              ? 'bg-emerald-950/90 text-emerald-300 border-emerald-700/60'
              : 'bg-blue-950/90 text-blue-300 border-blue-700/60'
          }`}
        >
          <ShieldCheck className="h-3 w-3 text-emerald-400" />
          {concept.verified === 'human-reviewed' ? 'Human-Reviewed' : concept.verified}
        </span>
      </div>

      {/* NCERT Provenance Citation */}
      {primarySource && (
        <div className="flex items-center gap-1.5 text-xs text-slate-300">
          <BookOpen className="h-3.5 w-3.5 text-amber-400" />
          <span className="font-semibold text-slate-100">{primarySource.name}</span>
          {primarySource.activity && (
            <span className="text-amber-400 font-bold">({primarySource.activity})</span>
          )}
        </div>
      )}
    </div>
  );
};
