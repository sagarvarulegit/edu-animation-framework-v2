import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { Zap, ShieldCheck } from 'lucide-react';

export const MolecularDiagramCard: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Intro transition
  const cardScale = spring({
    frame,
    fps,
    config: { damping: 14, mass: 0.8, stiffness: 90 }
  });

  // Reaction Progress: 0 (initial) -> 1 (electrons transfer) -> 2 (ions formed & attract)
  // Phase 1 (0-60f): Reveal atoms
  // Phase 2 (60-150f): Electron transfer jump
  // Phase 3 (150-240f): Ion charges & lattice formation
  const electronJumpProgress = interpolate(frame, [60, 130], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp'
  });

  const ionAttractionProgress = interpolate(frame, [140, 200], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp'
  });

  // Atomic shell rotation
  const mgRotation = (frame * 1.5) % 360;
  const oRotation = (-frame * 1.8) % 360;

  // Magnesium & Oxygen atom positions
  const mgXOffset = interpolate(ionAttractionProgress, [0, 1], [0, 90]);
  const oXOffset = interpolate(ionAttractionProgress, [0, 1], [0, -90]);

  return (
    <div className="absolute inset-0 flex flex-col items-center justify-center bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 p-12 text-white">
      {/* Header Banner */}
      <div className="text-center mb-8">
        <div className="inline-flex items-center gap-2 rounded-full border border-indigo-500/40 bg-indigo-500/10 px-4 py-1.5 text-xs font-bold uppercase tracking-wider text-indigo-300 mb-3">
          <Zap className="h-4 w-4 text-amber-400" /> Sub-Microscopic Atomic Mechanism
        </div>
        <h2 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-white via-slate-100 to-cyan-300 font-outfit">
          Electron Transfer & Ionic Bond Formation
        </h2>
        <p className="text-sm text-slate-400 mt-1 max-w-xl mx-auto">
          Magnesium donates 2 valence electrons to Oxygen, achieving stable noble gas octets.
        </p>
      </div>

      {/* Main Interactive Atomic Arena */}
      <div
        style={{ transform: `scale(${cardScale})` }}
        className="relative flex h-[480px] w-full max-w-5xl items-center justify-around rounded-3xl border border-slate-800 bg-slate-900/90 p-8 shadow-2xl backdrop-blur-xl"
      >
        {/* ================= MAGNESIUM ATOM (LEFT) ================= */}
        <div
          style={{ transform: `translateX(${mgXOffset}px)` }}
          className="relative flex flex-col items-center transition-transform"
        >
          <div className="relative flex h-72 w-72 items-center justify-center">
            {/* Outer M-Shell (2 valence e-) */}
            <div
              style={{ transform: `rotate(${mgRotation}deg)` }}
              className="absolute h-64 w-64 rounded-full border border-dashed border-cyan-500/40"
            >
              {/* Valence Electron 1 */}
              {electronJumpProgress < 0.9 && (
                <div
                  style={{
                    transform: `translate(${electronJumpProgress * 280}px, ${Math.sin(electronJumpProgress * Math.PI) * -60}px)`
                  }}
                  className="absolute top-0 left-1/2 h-4 w-4 -translate-x-1/2 -translate-y-1/2 rounded-full bg-cyan-300 shadow-[0_0_12px_rgba(6,182,212,0.9)]"
                />
              )}
              {/* Valence Electron 2 */}
              {electronJumpProgress < 0.9 && (
                <div
                  style={{
                    transform: `translate(${electronJumpProgress * 280}px, ${Math.sin(electronJumpProgress * Math.PI) * 60}px)`
                  }}
                  className="absolute bottom-0 left-1/2 h-4 w-4 -translate-x-1/2 translate-y-1/2 rounded-full bg-cyan-300 shadow-[0_0_12px_rgba(6,182,212,0.9)]"
                />
              )}
            </div>

            {/* L-Shell (8 e-) */}
            <div className="absolute h-44 w-44 rounded-full border border-slate-700/60" />

            {/* K-Shell (2 e-) */}
            <div className="absolute h-28 w-28 rounded-full border border-slate-700/80" />

            {/* Nucleus */}
            <div className="relative z-10 flex h-16 w-16 flex-col items-center justify-center rounded-full bg-gradient-to-br from-cyan-600 to-blue-700 shadow-[0_0_20px_rgba(6,182,212,0.5)] border-2 border-cyan-300">
              <span className="text-base font-black">Mg</span>
              <span className="text-[10px] text-cyan-200">12p 12n</span>
            </div>
          </div>

          {/* Magnesium Label & Config */}
          <div className="mt-4 text-center">
            <h4 className="text-xl font-bold text-cyan-300">
              {electronJumpProgress > 0.8 ? 'Mg²⁺ Cation' : 'Magnesium Atom (Mg)'}
            </h4>
            <div className="mt-1 flex items-center justify-center gap-2">
              <span className="rounded-md bg-slate-800 px-2.5 py-0.5 text-xs font-mono text-slate-300 border border-slate-700">
                {electronJumpProgress > 0.8 ? 'Config: 2, 8 [Octet]' : 'Config: 2, 8, 2'}
              </span>
              {electronJumpProgress > 0.8 && (
                <span className="rounded-md bg-emerald-500/20 px-2 py-0.5 text-xs font-semibold text-emerald-300 border border-emerald-500/40 flex items-center gap-1">
                  <ShieldCheck className="h-3 w-3" /> Stable
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Transfer Arrow & Status */}
        <div className="flex flex-col items-center justify-center px-4">
          <div className="text-xs font-bold uppercase tracking-widest text-amber-400 mb-2">
            {electronJumpProgress < 0.3
              ? '2 Valence Electrons'
              : electronJumpProgress < 0.9
              ? 'Transferring 2e⁻...'
              : 'Ionic Bond (Mg²⁺ + O²⁻)'}
          </div>
          <div className="relative h-1.5 w-36 rounded-full bg-slate-800 overflow-hidden border border-slate-700">
            <div
              style={{ width: `${electronJumpProgress * 100}%` }}
              className="h-full bg-gradient-to-r from-cyan-400 to-amber-400 shadow-[0_0_10px_rgba(245,158,11,0.8)]"
            />
          </div>
          <span className="mt-2 text-xs font-mono text-slate-400">
            2e⁻ Transfer
          </span>
        </div>

        {/* ================= OXYGEN ATOM (RIGHT) ================= */}
        <div
          style={{ transform: `translateX(${oXOffset}px)` }}
          className="relative flex flex-col items-center transition-transform"
        >
          <div className="relative flex h-72 w-72 items-center justify-center">
            {/* Outer L-Shell (6 valence e- + accepts 2) */}
            <div
              style={{ transform: `rotate(${oRotation}deg)` }}
              className="absolute h-52 w-52 rounded-full border border-dashed border-rose-500/40"
            >
              {/* Accepted Electron 1 */}
              {electronJumpProgress >= 0.9 && (
                <div className="absolute top-0 left-1/2 h-4 w-4 -translate-x-1/2 -translate-y-1/2 rounded-full bg-cyan-300 shadow-[0_0_12px_rgba(6,182,212,0.9)] animate-pulse" />
              )}
              {/* Accepted Electron 2 */}
              {electronJumpProgress >= 0.9 && (
                <div className="absolute bottom-0 left-1/2 h-4 w-4 -translate-x-1/2 translate-y-1/2 rounded-full bg-cyan-300 shadow-[0_0_12px_rgba(6,182,212,0.9)] animate-pulse" />
              )}
            </div>

            {/* K-Shell (2 e-) */}
            <div className="absolute h-28 w-28 rounded-full border border-slate-700/80" />

            {/* Nucleus */}
            <div className="relative z-10 flex h-16 w-16 flex-col items-center justify-center rounded-full bg-gradient-to-br from-rose-600 to-red-700 shadow-[0_0_20px_rgba(244,63,94,0.5)] border-2 border-rose-300">
              <span className="text-base font-black">O</span>
              <span className="text-[10px] text-rose-200">8p 8n</span>
            </div>
          </div>

          {/* Oxygen Label & Config */}
          <div className="mt-4 text-center">
            <h4 className="text-xl font-bold text-rose-300">
              {electronJumpProgress > 0.8 ? 'O²⁻ Anion (Oxide)' : 'Oxygen Atom (O)'}
            </h4>
            <div className="mt-1 flex items-center justify-center gap-2">
              <span className="rounded-md bg-slate-800 px-2.5 py-0.5 text-xs font-mono text-slate-300 border border-slate-700">
                {electronJumpProgress > 0.8 ? 'Config: 2, 8 [Octet]' : 'Config: 2, 6'}
              </span>
              {electronJumpProgress > 0.8 && (
                <span className="rounded-md bg-emerald-500/20 px-2 py-0.5 text-xs font-semibold text-emerald-300 border border-emerald-500/40 flex items-center gap-1">
                  <ShieldCheck className="h-3 w-3" /> Stable
                </span>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
