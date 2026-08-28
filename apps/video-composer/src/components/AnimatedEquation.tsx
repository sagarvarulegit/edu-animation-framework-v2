import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { CheckCircle2, Scale, ArrowRight, Flame, Layers } from 'lucide-react';

export const AnimatedEquation: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Step 1: Word Equation (frames 0 - 60)
  // Step 2: Skeleton Unbalanced (frames 60 - 140)
  // Step 3: Balanced Equation (frames 140+)
  const step = frame < 60 ? 1 : frame < 140 ? 2 : 3;

  const cardScale = spring({
    frame,
    fps,
    config: { damping: 14, mass: 0.8, stiffness: 90 }
  });

  const step1Opacity = interpolate(frame, [0, 20], [0, 1], { extrapolateRight: 'clamp' });
  const step2Opacity = interpolate(frame, [60, 80], [0, 1], { extrapolateRight: 'clamp' });
  const step3Opacity = interpolate(frame, [140, 160], [0, 1], { extrapolateRight: 'clamp' });

  // Highlight pulse for stoichiometric coefficients
  const coeffScale = step === 3
    ? spring({ frame: frame - 140, fps, config: { damping: 10, stiffness: 120 } })
    : 1;

  return (
    <div className="absolute inset-0 flex flex-col items-center justify-center bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950 p-12 text-white font-sans">
      {/* Header */}
      <div className="text-center mb-8">
        <div className="inline-flex items-center gap-2 rounded-full border border-cyan-500/40 bg-cyan-500/10 px-4 py-1.5 text-xs font-bold uppercase tracking-wider text-cyan-300 mb-3">
          <Scale className="h-4 w-4 text-cyan-400" /> Chemical Reaction Representation
        </div>
        <h2 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-white via-slate-100 to-cyan-200 font-outfit">
          Balanced Chemical Equation
        </h2>
      </div>

      {/* Main Glass Card */}
      <div
        style={{ transform: `scale(${cardScale})` }}
        className="relative flex w-full max-w-5xl flex-col items-center rounded-3xl border border-slate-800 bg-slate-900/90 p-10 shadow-2xl backdrop-blur-xl"
      >
        {/* Step Progression Indicators */}
        <div className="flex items-center gap-8 mb-8">
          <div className={`flex items-center gap-2 text-xs font-bold uppercase tracking-wider ${step >= 1 ? 'text-cyan-400' : 'text-slate-500'}`}>
            <span className={`flex h-6 w-6 items-center justify-center rounded-full text-xs ${step >= 1 ? 'bg-cyan-500/20 border border-cyan-500/50' : 'bg-slate-800'}`}>1</span>
            Word Equation
          </div>
          <div className="h-0.5 w-12 bg-slate-800" />
          <div className={`flex items-center gap-2 text-xs font-bold uppercase tracking-wider ${step >= 2 ? 'text-amber-400' : 'text-slate-500'}`}>
            <span className={`flex h-6 w-6 items-center justify-center rounded-full text-xs ${step >= 2 ? 'bg-amber-500/20 border border-amber-500/50' : 'bg-slate-800'}`}>2</span>
            Skeletal Equation
          </div>
          <div className="h-0.5 w-12 bg-slate-800" />
          <div className={`flex items-center gap-2 text-xs font-bold uppercase tracking-wider ${step >= 3 ? 'text-emerald-400' : 'text-slate-500'}`}>
            <span className={`flex h-6 w-6 items-center justify-center rounded-full text-xs ${step >= 3 ? 'bg-emerald-500/20 border border-emerald-500/50' : 'bg-slate-800'}`}>3</span>
            Balanced Equation
          </div>
        </div>

        {/* 1. WORD EQUATION */}
        {step === 1 && (
          <div
            style={{ opacity: step1Opacity }}
            className="flex flex-col items-center justify-center py-6 text-center"
          >
            <div className="flex items-center gap-4 text-3xl font-bold text-slate-100 font-outfit">
              <span className="rounded-xl bg-slate-800/80 px-5 py-3 border border-slate-700">Magnesium (s)</span>
              <span className="text-cyan-400 font-light text-2xl">+</span>
              <span className="rounded-xl bg-slate-800/80 px-5 py-3 border border-slate-700">Oxygen (g)</span>
              <ArrowRight className="h-8 w-8 text-amber-400 mx-2" />
              <span className="rounded-xl bg-slate-800/80 px-5 py-3 border border-slate-700 text-emerald-300">Magnesium Oxide (s)</span>
            </div>
            <p className="mt-6 text-sm text-slate-400">
              Reactants combine in the presence of heat to form a single compound product.
            </p>
          </div>
        )}

        {/* 2. SKELETAL EQUATION */}
        {step === 2 && (
          <div
            style={{ opacity: step2Opacity }}
            className="flex flex-col items-center justify-center py-6 text-center"
          >
            <div className="flex items-center gap-4 text-4xl font-black text-slate-100 font-mono-code">
              <span className="rounded-xl bg-slate-800/80 px-6 py-3 border border-slate-700">Mg</span>
              <span className="text-amber-400 font-light text-3xl">+</span>
              <span className="rounded-xl bg-slate-800/80 px-6 py-3 border border-slate-700">O₂</span>
              <ArrowRight className="h-8 w-8 text-amber-400 mx-2" />
              <span className="rounded-xl bg-slate-800/80 px-6 py-3 border border-slate-700 text-rose-300">MgO</span>
            </div>
            <div className="mt-6 flex items-center gap-3 rounded-xl bg-rose-500/10 px-4 py-2 border border-rose-500/30 text-rose-300 text-xs font-semibold">
              <span>⚠️ Unbalanced: Reactants have 2 Oxygen atoms (O₂), but Product has only 1 Oxygen atom (MgO).</span>
            </div>
          </div>
        )}

        {/* 3. BALANCED EQUATION */}
        {step === 3 && (
          <div
            style={{ opacity: step3Opacity }}
            className="flex flex-col items-center justify-center py-6 text-center"
          >
            <div className="flex items-center gap-3 text-5xl font-black text-slate-100 font-mono-code">
              {/* 2Mg */}
              <div className="flex items-center rounded-2xl bg-slate-800/90 px-6 py-4 border border-cyan-500/60 shadow-[0_0_20px_rgba(6,182,212,0.3)]">
                <span
                  style={{ transform: `scale(${coeffScale})` }}
                  className="text-cyan-400 mr-1.5 font-extrabold text-5xl"
                >
                  2
                </span>
                <span>Mg</span>
                <span className="text-xs text-slate-400 ml-1.5 self-end mb-1 font-sans">(s)</span>
              </div>

              <span className="text-cyan-400 font-light text-3xl mx-2">+</span>

              {/* O2 */}
              <div className="flex items-center rounded-2xl bg-slate-800/90 px-6 py-4 border border-slate-700 shadow-md">
                <span>O₂</span>
                <span className="text-xs text-slate-400 ml-1.5 self-end mb-1 font-sans">(g)</span>
              </div>

              <div className="flex flex-col items-center mx-3">
                <span className="text-[11px] font-bold uppercase tracking-wider text-amber-400 mb-0.5">Heat (Δ)</span>
                <ArrowRight className="h-8 w-8 text-amber-400" />
              </div>

              {/* 2MgO */}
              <div className="flex items-center rounded-2xl bg-slate-800/90 px-6 py-4 border border-emerald-500/60 shadow-[0_0_20px_rgba(16,185,129,0.3)]">
                <span
                  style={{ transform: `scale(${coeffScale})` }}
                  className="text-emerald-400 mr-1.5 font-extrabold text-5xl"
                >
                  2
                </span>
                <span className="text-emerald-300">MgO</span>
                <span className="text-xs text-slate-400 ml-1.5 self-end mb-1 font-sans">(s)</span>
              </div>
            </div>

            {/* Atom Count Balance Check */}
            <div className="mt-8 grid grid-cols-2 gap-6 w-full max-w-2xl">
              <div className="flex items-center justify-between rounded-xl bg-slate-950/60 p-3.5 border border-slate-800 text-xs">
                <span className="text-slate-400 font-medium">Reactants Side:</span>
                <span className="font-mono-code font-bold text-cyan-300">2 Mg atoms & 2 O atoms</span>
              </div>
              <div className="flex items-center justify-between rounded-xl bg-slate-950/60 p-3.5 border border-slate-800 text-xs">
                <span className="text-slate-400 font-medium">Products Side:</span>
                <span className="font-mono-code font-bold text-emerald-300">2 Mg atoms & 2 O atoms</span>
              </div>
            </div>
          </div>
        )}

        {/* Reaction Type Badges */}
        <div className="mt-8 flex items-center justify-center gap-4 border-t border-slate-800 pt-6 w-full">
          <span className="flex items-center gap-1.5 rounded-full bg-indigo-500/15 px-4 py-1.5 text-xs font-semibold text-indigo-300 border border-indigo-500/30">
            <Layers className="h-3.5 w-3.5" /> Combination Reaction
          </span>
          <span className="flex items-center gap-1.5 rounded-full bg-amber-500/15 px-4 py-1.5 text-xs font-semibold text-amber-300 border border-amber-500/30">
            <Flame className="h-3.5 w-3.5" /> Exothermic Reaction
          </span>
          <span className="flex items-center gap-1.5 rounded-full bg-emerald-500/15 px-4 py-1.5 text-xs font-semibold text-emerald-300 border border-emerald-500/30">
            <CheckCircle2 className="h-3.5 w-3.5" /> Law of Conservation of Mass Satisfied
          </span>
        </div>
      </div>
    </div>
  );
};
