import React, { useState, useRef } from 'react';
import ReactDOM from 'react-dom/client';
import { Player, type PlayerRef } from '@remotion/player';
import { MagnesiumRibbonLesson } from './compositions/MagnesiumRibbonLesson';
import { IntroTitleCard } from './components/IntroTitleCard';
import { MolecularDiagramCard } from './components/MolecularDiagramCard';
import { AnimatedEquation } from './components/AnimatedEquation';
import { OutroSummaryCard } from './components/OutroSummaryCard';
import {
  Film,
  Play,
  Pause,
  RotateCcw,
  Sparkles,
  Layers,
  Clock,
  BookOpen,
  Volume2,
  Tv,
  CheckCircle2
} from 'lucide-react';
import './index.css';

function VideoComposerStudio() {
  const [selectedComposition, setSelectedComposition] = useState<string>('full-lesson');
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const playerRef = useRef<PlayerRef>(null);

  // Scene quick jump markers
  const sceneMarkers = [
    { name: '1. Intro & Objectives', frame: 0, time: '0:00' },
    { name: '2. 3D Lab Setup', frame: 240, time: '0:08' },
    { name: '3. 3D Heating', frame: 600, time: '0:20' },
    { name: '4. 3D Combustion', frame: 1020, time: '0:34' },
    { name: '5. Molecular Transfer', frame: 1560, time: '0:52' },
    { name: '6. Chemical Equation', frame: 2100, time: '1:10' },
    { name: '7. Exam Summary', frame: 2460, time: '1:22' }
  ];

  const handleJumpTo = (frame: number) => {
    if (playerRef.current) {
      playerRef.current.seekTo(frame);
    }
  };

  const handleTogglePlay = () => {
    if (playerRef.current) {
      if (playerRef.current.isPlaying()) {
        playerRef.current.pause();
        setIsPlaying(false);
      } else {
        playerRef.current.play();
        setIsPlaying(true);
      }
    }
  };

  return (
    <div className="flex h-screen w-screen flex-col bg-slate-950 text-slate-100 font-sans overflow-hidden">
      {/* Top Navbar */}
      <header className="flex h-14 shrink-0 items-center justify-between border-b border-slate-800/80 bg-slate-900/90 px-6 backdrop-blur-md">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-tr from-indigo-600 to-cyan-500 shadow-md">
            <Film className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="text-sm font-bold tracking-tight text-white flex items-center gap-2">
              Educational Video Composer
              <span className="rounded-md bg-cyan-500/20 px-2 py-0.5 text-[10px] font-bold text-cyan-300 border border-cyan-500/30 uppercase">
                Remotion Studio
              </span>
            </h1>
            <p className="text-[11px] text-slate-400">
              CBSE Class 10 Chemistry • Burning of Magnesium Ribbon
            </p>
          </div>
        </div>

        {/* View / Composition Selector */}
        <div className="flex items-center gap-2 bg-slate-950/70 p-1 rounded-xl border border-slate-800">
          <button
            onClick={() => setSelectedComposition('full-lesson')}
            className={`flex items-center gap-1.5 px-3 py-1 text-xs font-semibold rounded-lg transition-all ${
              selectedComposition === 'full-lesson'
                ? 'bg-indigo-600 text-white shadow-md'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Tv className="h-3.5 w-3.5" /> Full Lesson (88s)
          </button>
          <button
            onClick={() => setSelectedComposition('intro')}
            className={`flex items-center gap-1.5 px-3 py-1 text-xs font-semibold rounded-lg transition-all ${
              selectedComposition === 'intro'
                ? 'bg-indigo-600 text-white shadow-md'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <BookOpen className="h-3.5 w-3.5" /> Intro
          </button>
          <button
            onClick={() => setSelectedComposition('molecular')}
            className={`flex items-center gap-1.5 px-3 py-1 text-xs font-semibold rounded-lg transition-all ${
              selectedComposition === 'molecular'
                ? 'bg-indigo-600 text-white shadow-md'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Sparkles className="h-3.5 w-3.5" /> Molecular
          </button>
          <button
            onClick={() => setSelectedComposition('equation')}
            className={`flex items-center gap-1.5 px-3 py-1 text-xs font-semibold rounded-lg transition-all ${
              selectedComposition === 'equation'
                ? 'bg-indigo-600 text-white shadow-md'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Layers className="h-3.5 w-3.5" /> Equation
          </button>
          <button
            onClick={() => setSelectedComposition('summary')}
            className={`flex items-center gap-1.5 px-3 py-1 text-xs font-semibold rounded-lg transition-all ${
              selectedComposition === 'summary'
                ? 'bg-indigo-600 text-white shadow-md'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <CheckCircle2 className="h-3.5 w-3.5" /> Summary
          </button>
        </div>
      </header>

      {/* Main Studio Area */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Video Player Stage */}
        <div className="flex flex-1 flex-col items-center justify-center bg-slate-950 p-6">
          <div className="relative aspect-video w-full max-w-5xl overflow-hidden rounded-2xl border border-slate-800 bg-black shadow-2xl">
            {selectedComposition === 'full-lesson' && (
              <Player
                ref={playerRef}
                component={MagnesiumRibbonLesson}
                durationInFrames={2640}
                fps={30}
                compositionWidth={1920}
                compositionHeight={1080}
                style={{ width: '100%', height: '100%' }}
                controls
                autoPlay={false}
                loop
              />
            )}

            {selectedComposition === 'intro' && (
              <Player
                component={IntroTitleCard}
                durationInFrames={240}
                fps={30}
                compositionWidth={1920}
                compositionHeight={1080}
                style={{ width: '100%', height: '100%' }}
                controls
                loop
                inputProps={{
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
            )}

            {selectedComposition === 'molecular' && (
              <Player
                component={MolecularDiagramCard}
                durationInFrames={540}
                fps={30}
                compositionWidth={1920}
                compositionHeight={1080}
                style={{ width: '100%', height: '100%' }}
                controls
                loop
              />
            )}

            {selectedComposition === 'equation' && (
              <Player
                component={AnimatedEquation}
                durationInFrames={360}
                fps={30}
                compositionWidth={1920}
                compositionHeight={1080}
                style={{ width: '100%', height: '100%' }}
                controls
                loop
              />
            )}

            {selectedComposition === 'summary' && (
              <Player
                component={OutroSummaryCard}
                durationInFrames={180}
                fps={30}
                compositionWidth={1920}
                compositionHeight={1080}
                style={{ width: '100%', height: '100%' }}
                controls
                loop
              />
            )}
          </div>
        </div>

        {/* Right Sidebar: Timeline Markers & Metadata */}
        <aside className="w-80 border-l border-slate-800 bg-slate-900/70 p-5 flex flex-col justify-between overflow-y-auto">
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-1.5">
              <Clock className="h-3.5 w-3.5 text-cyan-400" /> Scene Timeline Navigation
            </h3>
            <div className="space-y-2">
              {sceneMarkers.map((marker, idx) => (
                <button
                  key={idx}
                  onClick={() => {
                    setSelectedComposition('full-lesson');
                    handleJumpTo(marker.frame);
                  }}
                  className="w-full flex items-center justify-between rounded-xl bg-slate-950/60 p-2.5 text-left border border-slate-800/80 hover:border-cyan-500/50 hover:bg-slate-800/50 transition-all text-xs"
                >
                  <span className="font-medium text-slate-200">{marker.name}</span>
                  <span className="font-mono text-[11px] text-cyan-400 bg-slate-900 px-2 py-0.5 rounded border border-slate-700">
                    {marker.time}
                  </span>
                </button>
              ))}
            </div>

            {/* Video Specs Card */}
            <div className="mt-6 rounded-2xl bg-slate-950/80 p-4 border border-slate-800 text-xs space-y-2">
              <div className="flex items-center justify-between text-slate-400">
                <span>Resolution</span>
                <span className="font-mono text-white font-bold">1920 × 1080 (1080p)</span>
              </div>
              <div className="flex items-center justify-between text-slate-400">
                <span>Frame Rate</span>
                <span className="font-mono text-white font-bold">30 FPS</span>
              </div>
              <div className="flex items-center justify-between text-slate-400">
                <span>Total Duration</span>
                <span className="font-mono text-white font-bold">88.0s (2640 frames)</span>
              </div>
              <div className="flex items-center justify-between text-slate-400">
                <span>Layers</span>
                <span className="text-cyan-300 font-semibold">3D Video + 2D Motion</span>
              </div>
            </div>
          </div>

          {/* Export / Render Action */}
          <div className="pt-4 border-t border-slate-800">
            <div className="rounded-xl bg-indigo-500/10 p-3 border border-indigo-500/30 text-xs text-indigo-200 mb-3">
              💡 To render the full production MP4 file, run:
              <code className="block mt-1 font-mono text-[11px] bg-slate-950 p-1.5 rounded text-cyan-300">
                npm run video:render
              </code>
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <VideoComposerStudio />
  </React.StrictMode>
);
