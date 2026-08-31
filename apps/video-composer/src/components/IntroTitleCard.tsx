import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { Sparkles, BookOpen, Atom, CheckCircle2, ShieldCheck } from 'lucide-react';
import { getOkfConcept } from '../data/generated/okfKnowledge';

export interface IntroTitleCardProps {
  conceptId?: string;
  curriculum?: string;
  grade?: number;
  subject?: string;
  chapter?: string;
  title?: string;
  objectives?: string[];
}

export const IntroTitleCard: React.FC<IntroTitleCardProps> = ({
  conceptId = 'magnesium-ribbon-combustion',
  curriculum: customCurriculum,
  grade: customGrade,
  subject: customSubject,
  chapter: customChapter,
  title: customTitle,
  objectives: customObjectives,
}) => {
  const concept = getOkfConcept(conceptId);
  const cbse = concept?.cbse_mapping;

  const curriculum = customCurriculum || 'CBSE';
  const grade = customGrade || cbse?.class || 10;
  const subject = customSubject || (cbse?.subject ? cbse.subject.charAt(0).toUpperCase() + cbse.subject.slice(1) : 'Chemistry');
  const chapter = customChapter || (cbse?.chapter ? `Chapter: ${cbse.chapter}` : 'Chapter 1: Chemical Reactions & Equations');
  const title = customTitle || concept?.title || 'Burning of Magnesium Ribbon';
  const objectives = customObjectives || cbse?.key_takeaways || [
    'Observe the burning of magnesium ribbon in air',
    'Identify the dazzling white flame and white solid product',
    'Understand valence electron transfer: Mg + O₂ → MgO',
    'Master the balanced chemical equation: 2Mg + O₂ → 2MgO'
  ];
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Animations
  const cardScale = spring({
    frame,
    fps,
    config: { damping: 14, mass: 0.8, stiffness: 90 }
  });

  const badgeOpacity = interpolate(frame, [5, 20], [0, 1], { extrapolateRight: 'clamp' });
  const titleOpacity = interpolate(frame, [15, 35], [0, 1], { extrapolateRight: 'clamp' });
  const titleY = interpolate(frame, [15, 35], [30, 0], { extrapolateRight: 'clamp' });
  const listOpacity = interpolate(frame, [35, 55], [0, 1], { extrapolateRight: 'clamp' });

  return (
    <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950 p-16 font-sans text-white">
      {/* Subtle Background Glows */}
      <div className="absolute top-1/4 left-1/4 h-96 w-96 rounded-full bg-cyan-500/10 blur-3xl pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 h-96 w-96 rounded-full bg-indigo-500/15 blur-3xl pointer-events-none" />

      {/* Main Glass Card */}
      <div
        style={{
          transform: `scale(${cardScale})`,
          opacity: badgeOpacity
        }}
        className="relative z-10 w-full max-w-5xl rounded-3xl border border-slate-700/60 bg-slate-900/80 p-12 shadow-2xl backdrop-blur-2xl"
      >
        {/* Top Badges */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-6">
          <div className="flex items-center gap-3">
            <span className="flex items-center gap-1.5 rounded-full bg-indigo-500/20 px-4 py-1.5 text-sm font-semibold tracking-wider text-indigo-300 border border-indigo-500/40">
              <BookOpen className="h-4 w-4" />
              {curriculum} Class {grade}
            </span>
            <span className="flex items-center gap-1.5 rounded-full bg-cyan-500/20 px-4 py-1.5 text-sm font-semibold tracking-wider text-cyan-300 border border-cyan-500/40">
              <Atom className="h-4 w-4" />
              {subject}
            </span>
          </div>
          <span className="text-sm font-medium tracking-wide text-slate-400">
            {chapter}
          </span>
        </div>

        {/* Title */}
        <div
          style={{
            opacity: titleOpacity,
            transform: `translateY(${titleY}px)`
          }}
          className="mt-8 text-center"
        >
          <div className="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-amber-400 mb-2">
            <Sparkles className="h-4 w-4" /> Laboratory Investigation & Concepts
          </div>
          <h1 className="text-5xl font-black tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-white via-slate-100 to-cyan-200 font-outfit leading-tight">
            {title}
          </h1>
        </div>

        {/* Learning Objectives */}
        <div
          style={{ opacity: listOpacity }}
          className="mt-10 rounded-2xl bg-slate-950/60 p-6 border border-slate-800/80"
        >
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-4">
            Key Learning Objectives
          </h3>
          <div className="grid grid-cols-2 gap-4">
            {objectives.map((obj, i) => {
              const itemDelay = 40 + i * 8;
              const itemSpring = spring({
                frame: frame - itemDelay,
                fps,
                config: { damping: 12, stiffness: 100 }
              });
              return (
                <div
                  key={i}
                  style={{
                    opacity: Math.max(0, itemSpring),
                    transform: `translateX(${(1 - itemSpring) * 20}px)`
                  }}
                  className="flex items-start gap-3 rounded-xl bg-slate-900/90 p-3.5 border border-slate-800/60"
                >
                  <CheckCircle2 className="h-5 w-5 text-emerald-400 shrink-0 mt-0.5" />
                  <span className="text-sm font-medium text-slate-200 leading-snug">
                    {obj}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};
