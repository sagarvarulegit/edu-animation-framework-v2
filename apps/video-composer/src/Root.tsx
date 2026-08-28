import React from 'react';
import { Composition } from 'remotion';
import { MagnesiumRibbonLesson } from './compositions/MagnesiumRibbonLesson';
import { IntroTitleCard, type IntroTitleCardProps } from './components/IntroTitleCard';
import { MolecularDiagramCard } from './components/MolecularDiagramCard';
import { AnimatedEquation } from './components/AnimatedEquation';
import { OutroSummaryCard } from './components/OutroSummaryCard';

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* 1. MASTER LESSON (1080p 30fps, 88 seconds) */}
      <Composition
        id="MagnesiumRibbonLesson"
        component={MagnesiumRibbonLesson}
        durationInFrames={2640}
        fps={30}
        width={1920}
        height={1080}
      />

      {/* 2. MODULAR SCENE PREVIEWS FOR RAPID ITERATION */}
      <Composition
        id="Scene-01-TitleCard"
        component={IntroTitleCard as any}
        durationInFrames={240}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          curriculum: 'CBSE',
          grade: 10,
          subject: 'Chemistry',
          chapter: 'Chapter 1: Chemical Reactions & Equations',
          title: 'Burning of Magnesium Ribbon',
          objectives: [
            'Observe the burning of magnesium ribbon in air',
            'Identify the dazzling white flame and white solid product',
            'Understand valence electron transfer: Mg + O₂ → MgO',
            'Master the balanced chemical equation: 2Mg + O₂ → 2MgO'
          ]
        }}
      />

      <Composition
        id="Scene-04-MolecularMechanism"
        component={MolecularDiagramCard}
        durationInFrames={540}
        fps={30}
        width={1920}
        height={1080}
      />

      <Composition
        id="Scene-05-EquationBalancing"
        component={AnimatedEquation}
        durationInFrames={360}
        fps={30}
        width={1920}
        height={1080}
      />

      <Composition
        id="Scene-06-ExamSummary"
        component={OutroSummaryCard}
        durationInFrames={180}
        fps={30}
        width={1920}
        height={1080}
      />
    </>
  );
};
