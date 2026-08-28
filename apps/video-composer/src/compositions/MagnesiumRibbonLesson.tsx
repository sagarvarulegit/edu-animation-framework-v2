import React from 'react';
import { Sequence } from 'remotion';
import { IntroTitleCard } from '../components/IntroTitleCard';
import { VideoTrack3D } from '../components/VideoTrack3D';
import { ObservationCallout } from '../components/ObservationCallout';
import { MolecularDiagramCard } from '../components/MolecularDiagramCard';
import { AnimatedEquation } from '../components/AnimatedEquation';
import { CaptionsOverlay, type NarrationCue } from '../components/CaptionsOverlay';
import { OutroSummaryCard } from '../components/OutroSummaryCard';

// Import narration data
import narrationData from '../../../../lessons/chemistry/magnesium-ribbon/narration.json';

export const MagnesiumRibbonLesson: React.FC = () => {
  // Flatten all cues for global captions synchronization
  const allCues: NarrationCue[] = narrationData.scenes.flatMap((s) => s.cues);

  return (
    <div className="relative h-full w-full bg-slate-950 overflow-hidden font-sans select-none">
      {/* =================================================================== */}
      {/* 1. INTRO TITLE CARD (0s - 8s / Frames 0 - 240)                      */}
      {/* =================================================================== */}
      <Sequence from={0} durationInFrames={240} name="Intro Title & Objectives">
        <IntroTitleCard
          curriculum="CBSE"
          grade={10}
          subject="Chemistry"
          chapter="Chapter 1: Chemical Reactions & Equations"
          title="Burning of Magnesium Ribbon"
          objectives={[
            'Observe the burning of magnesium ribbon in air',
            'Identify the dazzling white flame and white solid product',
            'Understand valence electron transfer: Mg + O₂ → MgO',
            'Master the balanced chemical equation: 2Mg + O₂ → 2MgO'
          ]}
        />
      </Sequence>

      {/* =================================================================== */}
      {/* 2. 3D SCENE 01: INTRODUCTION & SETUP (8s - 20s / Frames 240 - 600)  */}
      {/* =================================================================== */}
      <Sequence from={240} durationInFrames={360} name="3D Lab Setup">
        <VideoTrack3D
          src="/assets/videos/01-introduction.mp4"
          label="Activity 1.1 — Laboratory Apparatus Setup"
        />
        <ObservationCallout
          type="info"
          title="Apparatus Setup"
          description="Magnesium ribbon held with lab tongs above a Bunsen burner with a watch glass ready below."
          formula="Mg (s)"
          position="top-right"
          delayFrames={30}
        />
      </Sequence>

      {/* =================================================================== */}
      {/* 3. 3D SCENE 02: HEATING THE RIBBON (20s - 34s / Frames 600 - 1020)  */}
      {/* =================================================================== */}
      <Sequence from={600} durationInFrames={420} name="3D Heating in Flame">
        <VideoTrack3D
          src="/assets/videos/02-heating.mp4"
          label="Thermal Heating & Ignition"
        />
        <ObservationCallout
          type="flame"
          title="Heating in Flame"
          description="Burner ignited; heat energy provides activation energy to reach the ignition temperature."
          formula="Δ Heat"
          position="top-right"
          delayFrames={30}
        />
      </Sequence>

      {/* =================================================================== */}
      {/* 4. 3D SCENE 03: DAZZLING COMBUSTION (34s - 52s / Frames 1020 - 1560)*/}
      {/* =================================================================== */}
      <Sequence from={1020} durationInFrames={540} name="3D Dazzling Combustion">
        <VideoTrack3D
          src="/assets/videos/03-burning.mp4"
          label="Combustion & Product Collection"
        />
        <ObservationCallout
          type="flame"
          title="Dazzling White Flame"
          description="Burns with an intense, dazzling white light as magnesium reacts vigorously with atmospheric oxygen."
          formula="2Mg + O₂"
          position="top-right"
          delayFrames={20}
        />
        <ObservationCallout
          type="product"
          title="Magnesium Oxide Formed"
          description="A white powder is collected in the watch glass: Magnesium Oxide (MgO)."
          formula="MgO (s)"
          position="bottom-right"
          delayFrames={220}
        />
      </Sequence>

      {/* =================================================================== */}
      {/* 5. SCENE 04: MOLECULAR / ATOMIC MECHANISM (52s - 70s / Frames 1560 - 2100) */}
      {/* =================================================================== */}
      <Sequence from={1560} durationInFrames={540} name="Atomic Electron Transfer">
        <MolecularDiagramCard />
      </Sequence>

      {/* =================================================================== */}
      {/* 6. SCENE 05: BALANCED CHEMICAL EQUATION (70s - 82s / Frames 2100 - 2460) */}
      {/* =================================================================== */}
      <Sequence from={2100} durationInFrames={360} name="Balanced Chemical Equation">
        <AnimatedEquation />
      </Sequence>

      {/* =================================================================== */}
      {/* 7. OUTRO & CBSE EXAM SUMMARY (82s - 88s / Frames 2460 - 2640)      */}
      {/* =================================================================== */}
      <Sequence from={2460} durationInFrames={180} name="Exam Summary & Recap">
        <OutroSummaryCard />
      </Sequence>

      {/* =================================================================== */}
      {/* GLOBAL CAPTIONS OVERLAY (Synchronized subtitles across all frames)  */}
      {/* =================================================================== */}
      <CaptionsOverlay cues={allCues} />
    </div>
  );
};
