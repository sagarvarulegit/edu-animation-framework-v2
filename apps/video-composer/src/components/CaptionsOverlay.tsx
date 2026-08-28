import React from 'react';
import { useCurrentFrame, useVideoConfig } from 'remotion';
import { Sparkles } from 'lucide-react';

export interface NarrationCueWord {
  word: string;
  start: number;
  end: number;
}

export interface NarrationCue {
  start: number;
  end: number;
  speaker: string;
  concept?: string;
  text: string;
  words?: NarrationCueWord[];
}

interface CaptionsOverlayProps {
  cues: NarrationCue[];
  timeOffsetSeconds?: number;
}

export const CaptionsOverlay: React.FC<CaptionsOverlayProps> = ({
  cues,
  timeOffsetSeconds = 0
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const currentTime = frame / fps + timeOffsetSeconds;

  // Find active cue
  const activeCue = cues.find(
    (c) => currentTime >= c.start && currentTime <= c.end
  );

  if (!activeCue) return null;

  return (
    <div className="absolute bottom-8 inset-x-0 z-40 flex flex-col items-center justify-center px-12 pointer-events-none">
      <div className="flex flex-col items-center max-w-4xl rounded-2xl border border-slate-700/80 bg-slate-950/85 px-8 py-4 shadow-2xl backdrop-blur-xl transition-all">
        {/* Concept / Speaker Tag */}
        <div className="flex items-center gap-2 mb-2">
          {activeCue.concept && (
            <span className="flex items-center gap-1 text-[11px] font-bold uppercase tracking-wider text-cyan-400 bg-cyan-500/10 px-2.5 py-0.5 rounded-full border border-cyan-500/30">
              <Sparkles className="h-3 w-3 text-cyan-400" />
              {activeCue.concept}
            </span>
          )}
        </div>

        {/* Word-by-word Subtitle Text */}
        <p className="text-center text-xl font-medium tracking-wide text-slate-200 leading-relaxed font-sans">
          {activeCue.words && activeCue.words.length > 0 ? (
            activeCue.words.map((w, idx) => {
              const isWordActive = currentTime >= w.start && currentTime <= w.end;
              const hasWordPassed = currentTime > w.end;

              return (
                <span
                  key={idx}
                  className={`inline-block mr-1.5 transition-all duration-100 ${
                    isWordActive
                      ? 'text-cyan-300 font-bold scale-105 drop-shadow-[0_0_8px_rgba(6,182,212,0.8)]'
                      : hasWordPassed
                      ? 'text-slate-100'
                      : 'text-slate-400/80'
                  }`}
                >
                  {w.word}
                </span>
              );
            })
          ) : (
            <span>{activeCue.text}</span>
          )}
        </p>
      </div>
    </div>
  );
};
