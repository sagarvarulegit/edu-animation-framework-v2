import { useState, Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Stage } from '@react-three/drei';
import { HeartModel } from './components/HeartModel';
import { ANATOMY_KNOWLEDGE } from './data/anatomy';
import { Activity, BookOpen, Layers, Heart, Info } from 'lucide-react';

export function App() {
  const [activeCircuit, setActiveCircuit] = useState<'all' | 'pulmonary' | 'systemic'>('all');
  const [selectedPart, setSelectedPart] = useState<string | null>('human-heart-left-ventricle');

  const currentInfo = selectedPart && ANATOMY_KNOWLEDGE[selectedPart] 
    ? ANATOMY_KNOWLEDGE[selectedPart] 
    : {
        name: selectedPart ? selectedPart.replace('human-heart-', '').replace(/-/g, ' ') : 'Select an Anatomical Structure',
        circuit: 'systemic' as const,
        bloodType: 'Oxygenated / Deoxygenated' as const,
        function: 'Click on any chamber or vessel in the 3D heart to inspect its physiological role in human circulation.',
        cbseKeyPoint: 'Mammalian double circulation prevents the mixing of oxygenated and deoxygenated blood, allowing highly efficient metabolic energy production.'
      };

  return (
    <div className="w-screen h-screen flex flex-col bg-slate-950 text-slate-100 select-none overflow-hidden font-sans">
      {/* Header */}
      <header className="h-14 px-6 bg-slate-900/80 backdrop-blur border-b border-slate-800 flex items-center justify-between z-10">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-rose-500/20 text-rose-400 rounded-lg border border-rose-500/30">
            <Heart className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <h1 className="text-base font-semibold tracking-tight">Interactive 3D Heart & Double Circulation</h1>
            <p className="text-xs text-slate-400">CBSE Class 10 Biology — Transportation in Humans</p>
          </div>
        </div>

        {/* Circuit Mode Selectors */}
        <div className="flex items-center bg-slate-800/80 p-1 rounded-xl border border-slate-700/60">
          <button
            onClick={() => setActiveCircuit('all')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              activeCircuit === 'all' ? 'bg-slate-700 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Complete Heart (All)
          </button>
          <button
            onClick={() => setActiveCircuit('pulmonary')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5 ${
              activeCircuit === 'pulmonary' ? 'bg-blue-600 text-white shadow-sm' : 'text-blue-400 hover:text-blue-300'
            }`}
          >
            <span className="w-2 h-2 rounded-full bg-blue-400" />
            Pulmonary Circuit (Deoxygenated)
          </button>
          <button
            onClick={() => setActiveCircuit('systemic')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5 ${
              activeCircuit === 'systemic' ? 'bg-rose-600 text-white shadow-sm' : 'text-rose-400 hover:text-rose-300'
            }`}
          >
            <span className="w-2 h-2 rounded-full bg-rose-400" />
            Systemic Circuit (Oxygenated)
          </button>
        </div>
      </header>

      {/* Main 3D Canvas & Info Overlay */}
      <div className="flex-1 relative flex">
        {/* 3D Viewport */}
        <div className="flex-1 h-full cursor-grab active:cursor-grabbing">
          <Canvas camera={{ position: [0, 0, 0.4], fov: 45 }}>
            <color attach="background" args={['#090d16']} />
            <Suspense fallback={null}>
              <Stage environment="city" intensity={0.6} adjustCamera={1.2}>
                <HeartModel
                  activeCircuit={activeCircuit}
                  selectedPart={selectedPart}
                  onSelectPart={(name) => setSelectedPart(name)}
                />
              </Stage>
              <OrbitControls makeDefault autoRotate={false} minDistance={0.15} maxDistance={0.8} />
            </Suspense>
          </Canvas>

          {/* Viewport Floating Quick Select Bar */}
          <div className="absolute bottom-4 left-6 flex items-center gap-2 bg-slate-900/90 backdrop-blur p-2 rounded-2xl border border-slate-800 shadow-2xl">
            <span className="text-xs font-medium text-slate-400 px-2 flex items-center gap-1">
              <Layers className="w-3.5 h-3.5" /> Quick Focus:
            </span>
            <button
              onClick={() => setSelectedPart('human-heart-right-atrium')}
              className="px-2.5 py-1 text-xs rounded-lg bg-blue-950/60 text-blue-300 border border-blue-800/60 hover:bg-blue-900/50"
            >
              Right Atrium
            </button>
            <button
              onClick={() => setSelectedPart('human-heart-right-ventricle')}
              className="px-2.5 py-1 text-xs rounded-lg bg-blue-950/60 text-blue-300 border border-blue-800/60 hover:bg-blue-900/50"
            >
              Right Ventricle
            </button>
            <button
              onClick={() => setSelectedPart('human-heart-left-atrium')}
              className="px-2.5 py-1 text-xs rounded-lg bg-rose-950/60 text-rose-300 border border-rose-800/60 hover:bg-rose-900/50"
            >
              Left Atrium
            </button>
            <button
              onClick={() => setSelectedPart('human-heart-left-ventricle')}
              className="px-2.5 py-1 text-xs rounded-lg bg-rose-950/60 text-rose-300 border border-rose-800/60 hover:bg-rose-900/50"
            >
              Left Ventricle
            </button>
            <button
              onClick={() => setSelectedPart('human-heart-aortic-arch')}
              className="px-2.5 py-1 text-xs rounded-lg bg-amber-950/60 text-amber-300 border border-amber-800/60 hover:bg-amber-900/50"
            >
              Aorta Arch
            </button>
          </div>
        </div>

        {/* Right Pedagogical Sidebar */}
        <aside className="w-96 h-full bg-slate-900/90 backdrop-blur border-l border-slate-800 p-6 flex flex-col justify-between overflow-y-auto z-10 shadow-2xl">
          <div className="space-y-5">
            <div className="flex items-center gap-2 text-xs font-semibold text-rose-400 tracking-wider uppercase">
              <Activity className="w-4 h-4" />
              <span>Anatomical Inspector</span>
            </div>

            <div>
              <h2 className="text-xl font-bold text-slate-100 capitalize">{currentInfo.name}</h2>
              <div className="mt-2 inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-slate-800 text-slate-300 border border-slate-700">
                <span
                  className={`w-2 h-2 rounded-full ${
                    currentInfo.circuit === 'pulmonary'
                      ? 'bg-blue-400'
                      : currentInfo.circuit === 'systemic'
                      ? 'bg-rose-400'
                      : 'bg-emerald-400'
                  }`}
                />
                {currentInfo.bloodType}
              </div>
            </div>

            <div className="space-y-2">
              <h3 className="text-xs font-medium text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                <Info className="w-3.5 h-3.5" /> Physiological Function
              </h3>
              <p className="text-sm text-slate-300 leading-relaxed bg-slate-950/50 p-3.5 rounded-xl border border-slate-800/80">
                {currentInfo.function}
              </p>
            </div>

            <div className="space-y-2">
              <h3 className="text-xs font-medium text-amber-400 uppercase tracking-wider flex items-center gap-1.5">
                <BookOpen className="w-3.5 h-3.5" /> CBSE Key Takeaway
              </h3>
              <p className="text-sm text-amber-200/90 leading-relaxed bg-amber-950/30 p-3.5 rounded-xl border border-amber-900/50">
                {currentInfo.cbseKeyPoint}
              </p>
            </div>
          </div>

          <div className="pt-4 border-t border-slate-800 text-xs text-slate-500 flex items-center justify-between">
            <span>Click & Drag to Orbit • Scroll to Zoom</span>
            <span className="font-mono text-[10px] text-slate-600">v0.1.0-R3F</span>
          </div>
        </aside>
      </div>
    </div>
  );
}

export default App;
