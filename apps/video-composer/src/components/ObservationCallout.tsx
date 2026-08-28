import React from 'react';
import { spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { Eye, Flame, AlertCircle, Info, Sparkles } from 'lucide-react';
import clsx from 'clsx';

interface ObservationCalloutProps {
  type?: 'observation' | 'flame' | 'product' | 'caution' | 'info';
  title: string;
  description: string;
  formula?: string;
  position?: 'top-right' | 'bottom-right' | 'top-left' | 'center-right';
  delayFrames?: number;
}

export const ObservationCallout: React.FC<ObservationCalloutProps> = ({
  type = 'observation',
  title,
  description,
  formula,
  position = 'top-right',
  delayFrames = 0
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const popSpring = spring({
    frame: frame - delayFrames,
    fps,
    config: { damping: 12, mass: 0.6, stiffness: 120 }
  });

  if (frame < delayFrames) return null;

  const positionClasses = {
    'top-right': 'top-10 right-10',
    'bottom-right': 'bottom-28 right-10',
    'top-left': 'top-10 left-10',
    'center-right': 'top-1/3 right-10'
  }[position];

  const typeConfig = {
    observation: {
      icon: Eye,
      border: 'border-cyan-500/50',
      bg: 'bg-slate-900/90',
      accent: 'text-cyan-400',
      badgeBg: 'bg-cyan-500/20',
      badgeText: 'Observation'
    },
    flame: {
      icon: Flame,
      border: 'border-amber-500/60',
      bg: 'bg-slate-900/90',
      accent: 'text-amber-400',
      badgeBg: 'bg-amber-500/20',
      badgeText: 'Combustion'
    },
    product: {
      icon: Sparkles,
      border: 'border-emerald-500/50',
      bg: 'bg-slate-900/90',
      accent: 'text-emerald-400',
      badgeBg: 'bg-emerald-500/20',
      badgeText: 'Reaction Product'
    },
    caution: {
      icon: AlertCircle,
      border: 'border-rose-500/50',
      bg: 'bg-slate-900/90',
      accent: 'text-rose-400',
      badgeBg: 'bg-rose-500/20',
      badgeText: 'Important'
    },
    info: {
      icon: Info,
      border: 'border-indigo-500/50',
      bg: 'bg-slate-900/90',
      accent: 'text-indigo-400',
      badgeBg: 'bg-indigo-500/20',
      badgeText: 'Concept'
    }
  }[type];

  const Icon = typeConfig.icon;

  return (
    <div
      style={{
        transform: `scale(${popSpring}) translateY(${(1 - popSpring) * 20}px)`,
        opacity: Math.min(1, Math.max(0, popSpring))
      }}
      className={clsx(
        'absolute z-30 w-96 rounded-2xl border p-5 shadow-2xl backdrop-blur-xl',
        positionClasses,
        typeConfig.border,
        typeConfig.bg
      )}
    >
      <div className="flex items-center justify-between">
        <span
          className={clsx(
            'flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-bold uppercase tracking-wider',
            typeConfig.badgeBg,
            typeConfig.accent
          )}
        >
          <Icon className="h-3.5 w-3.5" />
          {typeConfig.badgeText}
        </span>
        {formula && (
          <span className="font-mono-code text-xs font-bold text-slate-300 bg-slate-800/80 px-2.5 py-1 rounded-lg border border-slate-700">
            {formula}
          </span>
        )}
      </div>

      <h4 className="mt-3 text-lg font-bold text-white tracking-tight">
        {title}
      </h4>

      <p className="mt-1.5 text-sm text-slate-300 leading-relaxed">
        {description}
      </p>
    </div>
  );
};
