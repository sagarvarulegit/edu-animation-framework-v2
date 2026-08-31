import React from 'react';
import { spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { Award, CheckCircle2, Lightbulb, ArrowRight, BookMarked, ShieldCheck } from 'lucide-react';
import { getOkfConcept } from '../data/generated/okfKnowledge';

export interface OutroSummaryCardProps {
  conceptId?: string;
}

export const OutroSummaryCard: React.FC<OutroSummaryCardProps> = ({
  conceptId = 'magnesium-ribbon-combustion',
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const concept = getOkfConcept(conceptId);
  const cbse = concept?.cbse_mapping;

  const cardScale = spring({
    frame,
    fps,
    config: { damping: 14, mass: 0.8, stiffness: 90 }
  });

  return (
    <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950 p-16 font-sans text-white">
      {/* Glows */}
      <div className="absolute top-1/3 left-1/4 h-96 w-96 rounded-full bg-emerald-500/10 blur-3xl pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 h-96 w-96 rounded-full bg-cyan-500/15 blur-3xl pointer-events-none" />

      {/* Main Glass Card */}
      <div
        style={{ transform: `scale(${cardScale})` }}
        className="relative z-10 w-full max-w-5xl rounded-3xl border border-slate-700/80 bg-slate-900/90 p-10 shadow-2xl backdrop-blur-2xl"
      >
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-5">
          <div className="flex items-center gap-3">
            <span className="flex items-center gap-1.5 rounded-full bg-emerald-500/20 px-4 py-1.5 text-xs font-bold uppercase tracking-wider text-emerald-300 border border-emerald-500/40">
              <Award className="h-4 w-4" /> Lesson Summary & Exam Takeaways
            </span>
          </div>
          <span className="text-xs font-semibold tracking-wider text-slate-400 uppercase">
            CBSE Class 10 Chemistry • Chapter 1
          </span>
        </div>

        {/* 3 Summary Columns */}
        <div className="mt-8 grid grid-cols-3 gap-6">
          {/* Column 1: Observations */}
          <div className="flex flex-col rounded-2xl bg-slate-950/60 p-5 border border-slate-800">
            <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-cyan-400 mb-3">
              <CheckCircle2 className="h-4 w-4" /> Key Observations
            </div>
            <ul className="space-y-2.5 text-xs text-slate-300 leading-relaxed">
              <li className="flex items-start gap-2">
                <span className="text-cyan-400 font-bold">•</span>
                <span>Burns with a <strong>dazzling white flame</strong>.</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-cyan-400 font-bold">•</span>
                <span>Forms a <strong>white powder</strong>: Magnesium Oxide (MgO).</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-cyan-400 font-bold">•</span>
                <span>Highly <strong>exothermic</strong> reaction.</span>
              </li>
            </ul>
          </div>

          {/* Column 2: Reaction Equation */}
          <div className="flex flex-col rounded-2xl bg-slate-950/60 p-5 border border-slate-800">
            <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-emerald-400 mb-3">
              <BookMarked className="h-4 w-4" /> Balanced Equation
            </div>
            <div className="my-auto py-3 text-center">
              <div className="font-mono-code text-xl font-black text-emerald-300 bg-slate-900/90 py-2.5 px-3 rounded-xl border border-emerald-500/30 shadow-inner">
                2Mg + O₂ → 2MgO
              </div>
              <p className="mt-3 text-[11px] text-slate-400">
                Combination reaction forming basic metallic oxide.
              </p>
            </div>
          </div>

          {/* Column 3: CBSE High-Yield Exam Tip */}
          <div className="flex flex-col rounded-2xl bg-gradient-to-br from-amber-500/10 to-slate-950 p-5 border border-amber-500/30">
            <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-amber-400 mb-3">
              <Lightbulb className="h-4 w-4 text-amber-400" /> CBSE Board Exam Tip
            </div>
            <p className="text-xs text-slate-200 leading-relaxed">
              <strong>Question:</strong> Why is magnesium ribbon cleaned with sandpaper before burning?
            </p>
            <p className="mt-2 text-xs text-amber-300/90 bg-amber-500/10 p-2 rounded-lg border border-amber-500/20 leading-relaxed">
              <strong>Answer:</strong> To remove the protective layer of <em>basic magnesium carbonate</em> that prevents combustion!
            </p>
          </div>
        </div>

        {/* Footer Next Lesson */}
        <div className="mt-8 flex items-center justify-between rounded-xl bg-slate-800/60 px-6 py-3.5 border border-slate-700/60">
          <span className="text-xs text-slate-300 font-medium">
            Next Lesson: <strong>Types of Chemical Reactions (Decomposition & Displacement)</strong>
          </span>
          <span className="flex items-center gap-1.5 text-xs font-bold text-cyan-400">
            Continue Learning <ArrowRight className="h-3.5 w-3.5" />
          </span>
        </div>
      </div>
    </div>
  );
};
