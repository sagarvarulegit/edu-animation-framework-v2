import React from 'react';
import { spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { AlertTriangle, XCircle, CheckCircle2 } from 'lucide-react';
import { getOkfConcept } from '../data/generated/okfKnowledge';

export interface OkfMisconceptionCalloutProps {
  conceptId: string;
  misconceptionIndex?: number;
  position?: 'bottom-left' | 'bottom-right' | 'top-right';
  delayFrames?: number;
}

export const OkfMisconceptionCallout: React.FC<OkfMisconceptionCalloutProps> = ({
  conceptId,
  misconceptionIndex = 0,
  position = 'bottom-left',
  delayFrames = 30,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const concept = getOkfConcept(conceptId);
  if (!concept || !concept.misconceptions || concept.misconceptions.length <= misconceptionIndex) {
    return null;
  }

  const misconception = concept.misconceptions[misconceptionIndex];

  const currentFrame = Math.max(0, frame - delayFrames);
  const scale = spring({
    frame: currentFrame,
    fps,
    config: { damping: 14, mass: 0.8, stiffness: 100 },
  });

  const opacity = spring({
    frame: currentFrame,
    fps,
    config: { damping: 12, mass: 0.5, stiffness: 120 },
  });

  const positionClasses = {
    'bottom-left': 'bottom-16 left-8',
    'bottom-right': 'bottom-16 right-8',
    'top-right': 'top-8 right-8',
  }[position];

  return (
    <div
      style={{
        opacity,
        transform: `scale(${scale})`,
      }}
      className={`absolute ${positionClasses} z-30 w-full max-w-lg rounded-3xl border border-rose-900/60 bg-slate-950/90 p-5 shadow-2xl backdrop-blur-xl font-sans`}
    >
      {/* Alert Header */}
      <div className="flex items-center gap-2 border-b border-slate-800 pb-3 mb-3">
        <div className="flex h-7 w-7 items-center justify-center rounded-xl bg-rose-500/20 text-rose-400 border border-rose-500/40">
          <AlertTriangle className="h-4 w-4" />
        </div>
        <div>
          <h4 className="text-xs font-extrabold uppercase tracking-wider text-rose-400">
            CBSE Board Exam Pitfall Alert
          </h4>
          <span className="text-[10px] text-slate-400">
            Source: {concept.title}
          </span>
        </div>
      </div>

      {/* Common Trap (Claim) */}
      <div className="rounded-xl bg-rose-950/25 p-3 border border-rose-900/40 mb-2.5">
        <div className="flex items-start gap-2">
          <XCircle className="h-4 w-4 text-rose-400 shrink-0 mt-0.5" />
          <div>
            <span className="text-[10px] font-bold uppercase tracking-wider text-rose-300">
              Common Student Misconception:
            </span>
            <p className="text-xs text-rose-200 mt-0.5 leading-snug">
              "{misconception.claim}"
            </p>
          </div>
        </div>
      </div>

      {/* Verified Scientific Correction */}
      <div className="rounded-xl bg-emerald-950/30 p-3 border border-emerald-800/40">
        <div className="flex items-start gap-2">
          <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0 mt-0.5" />
          <div>
            <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-400">
              Verified Scientific Fact:
            </span>
            <p className="text-xs text-emerald-200 mt-0.5 leading-snug">
              {misconception.correction}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
