import { useState, useRef, Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, ContactShadows } from '@react-three/drei';
import type { OrbitControls as OrbitControlsImpl } from 'three-stdlib';
import { ASSET_REGISTRY } from './data/assetRegistry';
import { AssetStudioInspector } from './components/AssetStudioInspector';
import { LabGameWorld, type LabStationId } from './components/LabGameWorld';
import { FPSController } from './components/FPSController';
import {
  Layers,
  Search,
  Box,
  Compass,
  RotateCcw,
  Gamepad2,
  Sparkles,
  Download,
  Copy,
  Check,
  Maximize2,
  ShieldCheck,
  BookOpen,
  Atom,
  AlertTriangle
} from 'lucide-react';
import { getOkfConceptsForAsset } from './data/scienceKnowledge';

export default function App() {
  // Navigation Mode: 'studio' (3D Asset Studio Inspector) vs 'game' (Virtual Science Lab World)
  const [appMode, setAppMode] = useState<'studio' | 'game'>('studio');

  // =========================================================================
  // STUDIO INSPECTOR STATE
  // =========================================================================
  const [selectedAssetId, setSelectedAssetId] = useState<string>('glass-prism-refraction');
  const [categoryFilter, setCategoryFilter] = useState<'all' | 'physics' | 'chemistry' | 'biology' | 'electricity'>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [activeTab, setActiveTab] = useState<'specs' | 'sockets' | 'cbse' | 'okf' | 'json'>('specs');
  const [activeStateIndex, setActiveStateIndex] = useState<number>(0);
  const [showSockets, setShowSockets] = useState<boolean>(true);
  const [showWireframe, setShowWireframe] = useState<boolean>(false);
  const [showDimensions, setShowDimensions] = useState<boolean>(true);
  const [lightingMode] = useState<'daylight' | 'studio' | 'darkroom'>('daylight');
  const [copiedJson, setCopiedJson] = useState<boolean>(false);

  // =========================================================================
  // GAME WORLD / FPS STATE
  // =========================================================================
  const [isFPSMode] = useState<boolean>(true);
  const [activeStation, setActiveStation] = useState<LabStationId>('optics');
  const [playerPosition, setPlayerPosition] = useState<[number, number]>([0.0, -0.60]);
  const [aimedApparatus, setAimedApparatus] = useState<string | null>(null);
  const [prismStep, setPrismStep] = useState<1 | 2 | 3 | 4>(1);
  const [burnStage, setBurnStage] = useState<'unheated' | 'heating' | 'burning' | 'collected'>('heating');
  const [selectedPart, setSelectedPart] = useState<string | null>('prism-glass-body');

  const studioControlsRef = useRef<OrbitControlsImpl>(null);

  // Filtered Assets for Sidebar
  const filteredAssets = ASSET_REGISTRY.filter((asset) => {
    const matchesCategory = categoryFilter === 'all' || asset.category === categoryFilter;
    const matchesSearch =
      asset.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      asset.tags.some((t) => t.toLowerCase().includes(searchQuery.toLowerCase())) ||
      asset.id.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const selectedAsset = ASSET_REGISTRY.find((a) => a.id === selectedAssetId) || ASSET_REGISTRY[0];

  // Copy JSON handler
  const handleCopyJson = () => {
    navigator.clipboard.writeText(JSON.stringify(selectedAsset, null, 2));
    setCopiedJson(true);
    setTimeout(() => setCopiedJson(false), 2000);
  };

  // Reset Studio Camera
  const handleResetStudioCamera = () => {
    if (studioControlsRef.current) {
      studioControlsRef.current.object.position.set(0.0, -0.38, 0.20);
      studioControlsRef.current.target.set(0, 0, 0.02);
      studioControlsRef.current.update();
    }
  };

  // Distance to Prism in Game Mode
  const distToPrism = Math.hypot(playerPosition[0] - (-0.15), playerPosition[1] - 0.0);
  const isNearPrism = distToPrism < 0.75;

  // Game Mode Interaction Handler
  const handleInteractCurrentStation = () => {
    if (isNearPrism || (aimedApparatus && (aimedApparatus.includes('prism') || aimedApparatus.includes('torch')))) {
      setActiveStation('optics');
      setPrismStep((prev) => (prev < 4 ? ((prev + 1) as any) : 1));
      setSelectedPart('prism-glass-body');
    } else if (Math.hypot(playerPosition[0] - 0.45, playerPosition[1] - 0.0) < 0.65 || (aimedApparatus && aimedApparatus.includes('burn'))) {
      setActiveStation('chemistry');
      setBurnStage((prev) => {
        if (prev === 'unheated') return 'heating';
        if (prev === 'heating') return 'burning';
        if (prev === 'burning') return 'collected';
        return 'unheated';
      });
      setSelectedPart('chem-magnesium-ribbon');
    } else if (Math.hypot(playerPosition[0] - 0.0, playerPosition[1] - 0.55) < 0.65) {
      setActiveStation('biology');
      setSelectedPart('human-heart-left-ventricle');
    }
  };

  return (
    <div className="flex flex-col h-screen w-screen bg-slate-950 text-slate-100 font-sans select-none overflow-hidden">
      {/* ===================================================================== */}
      {/* TOP APPLICATION HEADER                                                */}
      {/* ===================================================================== */}
      <header className="h-14 border-b border-slate-800/80 bg-slate-900/90 backdrop-blur-md px-6 flex items-center justify-between shrink-0 z-30">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-cyan-600 to-blue-500 flex items-center justify-center shadow-lg shadow-cyan-500/20">
            <Box className="w-4 h-4 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-sm tracking-tight text-white">Edu3D Asset Studio</span>
              <span className="text-[10px] font-bold px-1.5 py-0.5 rounded-full bg-cyan-950 text-cyan-400 border border-cyan-800/60 font-mono">
                v2.0 CBSE
              </span>
            </div>
            <p className="text-[11px] text-slate-400">3D Science Apparatus & Experiment Asset Library</p>
          </div>
        </div>

        {/* Global Mode Switcher: Studio Inspector vs Virtual Lab World */}
        <div className="flex items-center gap-1.5 bg-slate-950/80 p-1 rounded-xl border border-slate-800 shadow-inner">
          <button
            onClick={() => setAppMode('studio')}
            className={`px-3.5 py-1.5 text-xs font-bold rounded-lg flex items-center gap-2 transition-all ${
              appMode === 'studio'
                ? 'bg-cyan-600 text-white shadow-md shadow-cyan-600/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            3D Studio Inspector
          </button>
          <button
            onClick={() => setAppMode('game')}
            className={`px-3.5 py-1.5 text-xs font-bold rounded-lg flex items-center gap-2 transition-all ${
              appMode === 'game'
                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <Gamepad2 className="w-3.5 h-3.5" />
            Virtual Lab Game World
          </button>
        </div>

        {/* Header Stats */}
        <div className="flex items-center gap-3 text-xs text-slate-400 font-medium">
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            30 Standardized Assets
          </span>
          <span className="text-slate-700">|</span>
          <span>CBSE Class 10 STEM</span>
        </div>
      </header>

      {/* ===================================================================== */}
      {/* MODE 1: 3D ASSET STUDIO INSPECTOR                                     */}
      {/* ===================================================================== */}
      {appMode === 'studio' && (
        <div className="flex-1 flex overflow-hidden">
          {/* --- LEFT SIDEBAR: CATEGORIZED ASSET BROWSER --- */}
          <aside className="w-72 border-r border-slate-800/80 bg-slate-900/60 backdrop-blur-sm flex flex-col shrink-0">
            {/* Domain Filter Tabs */}
            <div className="p-3 border-b border-slate-800/80 space-y-2">
              <div className="relative">
                <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5" />
                <input
                  type="text"
                  placeholder="Search 3D apparatus, formulas, tags..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full bg-slate-950/80 border border-slate-800 rounded-xl pl-8 pr-3 py-1.5 text-xs text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-cyan-500 transition-colors"
                />
              </div>

              {/* Category Pills */}
              <div className="flex items-center gap-1 overflow-x-auto pb-1 text-[11px] font-semibold">
                {(['all', 'physics', 'chemistry', 'biology', 'electricity'] as const).map((cat) => (
                  <button
                    key={cat}
                    onClick={() => setCategoryFilter(cat)}
                    className={`px-2.5 py-1 rounded-lg capitalize shrink-0 transition-all ${
                      categoryFilter === cat
                        ? 'bg-cyan-950 text-cyan-300 border border-cyan-700/60'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                    }`}
                  >
                    {cat}
                  </button>
                ))}
              </div>
            </div>

            {/* Asset List Cards */}
            <div className="flex-1 overflow-y-auto p-2 space-y-1.5">
              {filteredAssets.map((asset) => {
                const isSelected = asset.id === selectedAsset.id;
                return (
                  <div
                    key={asset.id}
                    onClick={() => {
                      setSelectedAssetId(asset.id);
                      setActiveStateIndex(0);
                    }}
                    className={`p-2.5 rounded-xl cursor-pointer transition-all border ${
                      isSelected
                        ? 'bg-cyan-950/40 border-cyan-500/70 shadow-lg shadow-cyan-950/40'
                        : 'bg-slate-900/40 border-slate-800/60 hover:bg-slate-800/50 hover:border-slate-700'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-slate-100 truncate pr-1">
                        {asset.name}
                      </span>
                      <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded capitalize ${
                        asset.category === 'physics' ? 'bg-amber-950 text-amber-400' :
                        asset.category === 'chemistry' ? 'bg-emerald-950 text-emerald-400' :
                        asset.category === 'biology' ? 'bg-pink-950 text-pink-400' :
                        'bg-blue-950 text-blue-400'
                      }`}>
                        {asset.category}
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-400 mt-1 line-clamp-2 leading-snug">
                      {asset.semanticDescription}
                    </p>
                    <div className="flex items-center justify-between mt-2 pt-1.5 border-t border-slate-800/50 text-[10px] text-slate-500 font-mono">
                      <span>{asset.dimensions.width_mm}×{asset.dimensions.height_mm}mm</span>
                      <span>{Object.keys(asset.anchorPoints || {}).length} sockets</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </aside>

          {/* --- CENTER VIEWPORT: 3D STUDIO CANVAS & TOOLBAR --- */}
          <main className="flex-1 relative flex flex-col bg-slate-950">
            {/* Floating Top Inspection Controls Toolbar */}
            <div className="absolute top-4 left-6 right-6 flex items-center justify-between pointer-events-none z-20">
              <div className="pointer-events-auto flex items-center gap-1.5 bg-slate-900/90 backdrop-blur-md p-1.5 rounded-2xl border border-slate-800 shadow-2xl">
                <button
                  onClick={() => setShowDimensions(!showDimensions)}
                  className={`px-2.5 py-1 text-xs font-semibold rounded-lg flex items-center gap-1.5 transition-all ${
                    showDimensions
                      ? 'bg-cyan-950 text-cyan-300 border border-cyan-700/60'
                      : 'text-slate-400 hover:text-white hover:bg-slate-800'
                  }`}
                  title="Toggle 3D Bounding Box and Dimension Rulers"
                >
                  <Maximize2 className="w-3.5 h-3.5" />
                  Dimensions
                </button>
                <button
                  onClick={() => setShowSockets(!showSockets)}
                  className={`px-2.5 py-1 text-xs font-semibold rounded-lg flex items-center gap-1.5 transition-all ${
                    showSockets
                      ? 'bg-cyan-950 text-cyan-300 border border-cyan-700/60'
                      : 'text-slate-400 hover:text-white hover:bg-slate-800'
                  }`}
                  title="Toggle Snap / Connection Anchor Points"
                >
                  <Compass className="w-3.5 h-3.5" />
                  Sockets ({Object.keys(selectedAsset.anchorPoints || {}).length})
                </button>
                <button
                  onClick={() => setShowWireframe(!showWireframe)}
                  className={`px-2.5 py-1 text-xs font-semibold rounded-lg flex items-center gap-1.5 transition-all ${
                    showWireframe
                      ? 'bg-cyan-950 text-cyan-300 border border-cyan-700/60'
                      : 'text-slate-400 hover:text-white hover:bg-slate-800'
                  }`}
                  title="Toggle Wireframe Mesh Geometry"
                >
                  <Layers className="w-3.5 h-3.5" />
                  Wireframe
                </button>
              </div>

              {/* Lighting & Reset */}
              <div className="pointer-events-auto flex items-center gap-1.5 bg-slate-900/90 backdrop-blur-md p-1.5 rounded-2xl border border-slate-800 shadow-2xl">
                <button
                  onClick={handleResetStudioCamera}
                  className="px-2.5 py-1 text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-800 rounded-lg flex items-center gap-1.5 transition-all"
                  title="Reset 3D Camera View"
                >
                  <RotateCcw className="w-3.5 h-3.5 text-cyan-400" />
                  Reset View
                </button>
              </div>
            </div>

            {/* 3D Canvas */}
            <div className="flex-1 w-full h-full cursor-grab active:cursor-grabbing">
              <Canvas
                shadows
                camera={{ position: [0.0, -0.38, 0.20], up: [0, 0, 1], fov: 45 }}
                gl={{ antialias: true, alpha: false }}
              >
                <color attach="background" args={['#090d16']} />

                {/* 3-Point Studio Lighting Rig */}
                <ambientLight intensity={0.90} color="#f8fafc" />
                <directionalLight
                  castShadow
                  position={[0.5, -0.8, 1.2]}
                  intensity={2.4}
                  color="#fffdfa"
                  shadow-mapSize-width={2048}
                  shadow-mapSize-height={2048}
                  shadow-camera-near={0.05}
                  shadow-camera-far={2.5}
                />
                <directionalLight position={[-0.6, 0.6, 0.8]} intensity={1.0} color="#38bdf8" />
                <pointLight position={[0, 0, 0.4]} intensity={0.6} color="#e0f2fe" />

                <Suspense fallback={null}>
                  <AssetStudioInspector
                    asset={selectedAsset}
                    stateIndex={activeStateIndex}
                    showSockets={showSockets}
                    showWireframe={showWireframe}
                    showDimensions={showDimensions}
                    lightingMode={lightingMode}
                  />

                  <ContactShadows
                    position={[0, 0, -0.024]}
                    opacity={0.65}
                    scale={0.9}
                    blur={1.8}
                    far={0.5}
                  />

                  {/* Strictly Clamped OrbitControls - CANNOT turn upside down or go below floor */}
                  <OrbitControls
                    ref={studioControlsRef}
                    makeDefault
                    autoRotate={false}
                    minDistance={0.12}
                    maxDistance={1.4}
                    maxPolarAngle={Math.PI / 2 - 0.05}
                    minPolarAngle={Math.PI * 0.06}
                    dampingFactor={0.08}
                    enableDamping={true}
                  />
                </Suspense>
              </Canvas>
            </div>

            {/* Bottom Interactive State Transition Stepper */}
            {selectedAsset.interactiveStates && selectedAsset.interactiveStates.length > 0 && (
              <div className="absolute bottom-4 left-6 right-6 flex items-center justify-center pointer-events-none z-20">
                <div className="pointer-events-auto bg-slate-900/95 backdrop-blur-md p-3 rounded-2xl border border-slate-800 shadow-2xl max-w-xl w-full flex flex-col gap-2">
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-extrabold text-cyan-400 uppercase tracking-wider flex items-center gap-1.5">
                      <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                      Interactive State Simulation
                    </span>
                    <span className="text-[10px] font-mono text-slate-400">
                      Step {activeStateIndex + 1} of {selectedAsset.interactiveStates.length}
                    </span>
                  </div>

                  <div className="flex items-center gap-1.5">
                    {selectedAsset.interactiveStates.map((st, idx) => (
                      <button
                        key={st.state}
                        onClick={() => setActiveStateIndex(idx)}
                        className={`flex-1 py-1.5 px-2 rounded-xl text-xs font-bold transition-all text-center truncate ${
                          activeStateIndex === idx
                            ? 'bg-cyan-600 text-white shadow-md shadow-cyan-600/30 ring-2 ring-cyan-400/40'
                            : 'bg-slate-950/80 text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                        }`}
                      >
                        {st.label}
                      </button>
                    ))}
                  </div>

                  <p className="text-xs text-slate-300 font-medium leading-relaxed bg-slate-950/70 p-2 rounded-xl border border-slate-800/80">
                    {selectedAsset.interactiveStates[activeStateIndex]?.description}
                  </p>
                </div>
              </div>
            )}
          </main>

          {/* --- RIGHT SIDEBAR: METADATA & CBSE INSPECTOR --- */}
          <aside className="w-80 border-l border-slate-800/80 bg-slate-900/70 backdrop-blur-md flex flex-col shrink-0">
            {/* Header info */}
            <div className="p-4 border-b border-slate-800/80">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-mono font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                  {selectedAsset.id}
                </span>
                <span className="text-[10px] font-mono text-slate-400">Class {selectedAsset.cbse.class}</span>
              </div>
              <h2 className="text-sm font-extrabold text-white mt-1.5">{selectedAsset.name}</h2>
              <p className="text-xs text-slate-400 mt-1 leading-snug">{selectedAsset.semanticDescription}</p>
            </div>

            {/* Inspector Navigation Tabs */}
            <div className="flex items-center border-b border-slate-800/80 bg-slate-950/50 p-1 text-xs font-semibold">
              <button
                onClick={() => setActiveTab('specs')}
                className={`flex-1 py-1.5 rounded-lg text-center transition-all ${
                  activeTab === 'specs' ? 'bg-slate-800 text-white font-bold' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Specs
              </button>
              <button
                onClick={() => setActiveTab('sockets')}
                className={`flex-1 py-1.5 rounded-lg text-center transition-all ${
                  activeTab === 'sockets' ? 'bg-slate-800 text-white font-bold' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Sockets
              </button>
              <button
                onClick={() => setActiveTab('cbse')}
                className={`flex-1 py-1.5 rounded-lg text-center transition-all ${
                  activeTab === 'cbse' ? 'bg-slate-800 text-white font-bold' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                CBSE
              </button>
              <button
                onClick={() => setActiveTab('okf')}
                className={`flex-1 py-1.5 rounded-lg text-center transition-all flex items-center justify-center gap-1 ${
                  activeTab === 'okf' ? 'bg-cyan-950 text-cyan-300 font-bold border border-cyan-700/60' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <ShieldCheck className="w-3 h-3 text-cyan-400" />
                OKF
              </button>
              <button
                onClick={() => setActiveTab('json')}
                className={`flex-1 py-1.5 rounded-lg text-center transition-all ${
                  activeTab === 'json' ? 'bg-slate-800 text-white font-bold' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                JSON
              </button>
            </div>

            {/* Tab Contents */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {/* TAB 1: PHYSICAL SPECS & MATERIALS */}
              {activeTab === 'specs' && (
                <div className="space-y-4">
                  <div>
                    <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">Physical Dimensions</h3>
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div className="bg-slate-950/80 p-2.5 rounded-xl border border-slate-800/80">
                        <span className="text-slate-500 block text-[10px]">Width</span>
                        <span className="font-mono font-bold text-cyan-300">{selectedAsset.dimensions.width_mm} mm</span>
                      </div>
                      <div className="bg-slate-950/80 p-2.5 rounded-xl border border-slate-800/80">
                        <span className="text-slate-500 block text-[10px]">Height</span>
                        <span className="font-mono font-bold text-cyan-300">{selectedAsset.dimensions.height_mm} mm</span>
                      </div>
                      <div className="bg-slate-950/80 p-2.5 rounded-xl border border-slate-800/80">
                        <span className="text-slate-500 block text-[10px]">Depth</span>
                        <span className="font-mono font-bold text-cyan-300">{selectedAsset.dimensions.depth_mm} mm</span>
                      </div>
                      <div className="bg-slate-950/80 p-2.5 rounded-xl border border-slate-800/80">
                        <span className="text-slate-500 block text-[10px]">Weight</span>
                        <span className="font-mono font-bold text-cyan-300">{selectedAsset.dimensions.weight_g || 250} g</span>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">PBR Material Properties</h3>
                    <div className="bg-slate-950/80 p-3 rounded-xl border border-slate-800/80 space-y-2 text-xs">
                      <p className="text-slate-300 font-medium">{selectedAsset.materials.description}</p>
                      <div className="grid grid-cols-2 gap-2 pt-2 border-t border-slate-800/80 font-mono text-[11px]">
                        {selectedAsset.materials.ior && (
                          <div>
                            <span className="text-slate-500">IOR: </span>
                            <span className="text-amber-400 font-bold">{selectedAsset.materials.ior}</span>
                          </div>
                        )}
                        {selectedAsset.materials.transmission !== undefined && (
                          <div>
                            <span className="text-slate-500">Transmission: </span>
                            <span className="text-emerald-400 font-bold">{selectedAsset.materials.transmission}</span>
                          </div>
                        )}
                        <div>
                          <span className="text-slate-500">Roughness: </span>
                          <span className="text-slate-300">{selectedAsset.materials.roughness}</span>
                        </div>
                        <div>
                          <span className="text-slate-500">Metalness: </span>
                          <span className="text-slate-300">{selectedAsset.materials.metalness}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 2: ANCHOR & SNAP SOCKETS */}
              {activeTab === 'sockets' && (
                <div className="space-y-3">
                  <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">3D Connection Sockets</h3>
                  {Object.entries(selectedAsset.anchorPoints || {}).map(([socketName, [sx, sy, sz]]) => (
                    <div key={socketName} className="bg-slate-950/80 p-2.5 rounded-xl border border-slate-800/80 space-y-1">
                      <span className="text-xs font-bold text-cyan-300 flex items-center gap-1.5">
                        📍 {socketName}
                      </span>
                      <div className="font-mono text-[10px] text-slate-400 flex items-center justify-between">
                        <span>X: {sx.toFixed(3)}</span>
                        <span>Y: {sy.toFixed(3)}</span>
                        <span>Z: {sz.toFixed(3)}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* TAB 3: CBSE SYLLABUS & BOARD NOTES */}
              {activeTab === 'cbse' && (
                <div className="space-y-4 text-xs">
                  <div>
                    <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Chapter & Activity</span>
                    <h4 className="font-bold text-slate-100 text-sm mt-0.5">{selectedAsset.cbse.chapter}</h4>
                    <p className="text-cyan-400 font-semibold mt-0.5">{selectedAsset.cbse.ncertActivity}</p>
                  </div>

                  <div>
                    <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Key Physics Formulas</span>
                    <div className="mt-1.5 space-y-1.5">
                      {selectedAsset.cbse.formulas.map((form, idx) => (
                        <div key={idx} className="bg-slate-950 p-2 rounded-lg font-mono text-[11px] text-amber-300 border border-slate-800">
                          {form}
                        </div>
                      ))}
                    </div>
                  </div>

                  <div>
                    <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Board Exam Takeaway</span>
                    <p className="bg-emerald-950/40 p-2.5 rounded-xl text-emerald-200 border border-emerald-800/40 mt-1 leading-relaxed">
                      {selectedAsset.cbse.examTakeaway}
                    </p>
                  </div>
                </div>
              )}

              {/* TAB 4: OPEN KNOWLEDGE FORMAT (OKF v0.2) */}
              {activeTab === 'okf' && (
                <div className="space-y-4 text-xs">
                  {(() => {
                    const relatedConcepts = getOkfConceptsForAsset(selectedAsset.id);
                    if (relatedConcepts.length === 0) {
                      return (
                        <div className="bg-slate-950/80 p-3.5 rounded-xl border border-slate-800 text-slate-400 space-y-2">
                          <div className="flex items-center gap-1.5 text-cyan-400 font-bold">
                            <BookOpen className="w-4 h-4" />
                            <span>OKF Knowledge Profile</span>
                          </div>
                          <p className="text-[11px] leading-relaxed">
                            No direct concept is explicitly mapped to <code className="text-cyan-300">{selectedAsset.id}</code> in <code className="text-slate-300">knowledge/</code>.
                          </p>
                          <p className="text-[10px] text-slate-500 font-mono">
                            Add a Markdown file under <code className="text-slate-400">knowledge/</code> with <code className="text-cyan-400">related_assets: [{selectedAsset.id}]</code> to link this apparatus.
                          </p>
                        </div>
                      );
                    }

                    return (
                      <div className="space-y-4">
                        {relatedConcepts.map((concept) => (
                          <div
                            key={concept.id}
                            className="bg-slate-950/90 p-3.5 rounded-2xl border border-slate-800/90 shadow-lg space-y-3"
                          >
                            {/* Header: Title, Type & Trust Badge */}
                            <div className="space-y-1.5">
                              <div className="flex items-center justify-between gap-1.5 flex-wrap">
                                <span className="text-[9px] font-extrabold uppercase px-1.5 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800/60 font-mono">
                                  {concept.type}
                                </span>
                                <span className={`text-[9px] font-bold px-2 py-0.5 rounded-full flex items-center gap-1 border ${
                                  concept.verified === 'human-reviewed'
                                    ? 'bg-emerald-950 text-emerald-300 border-emerald-700/60'
                                    : concept.verified === 'machine-confirmed'
                                    ? 'bg-blue-950 text-blue-300 border-blue-700/60'
                                    : 'bg-amber-950 text-amber-300 border-amber-700/60'
                                }`}>
                                  <ShieldCheck className="w-2.5 h-2.5" />
                                  {concept.verified}
                                </span>
                              </div>
                              <h4 className="font-extrabold text-white text-xs leading-snug">
                                {concept.title}
                              </h4>
                              <p className="text-[11px] text-slate-400 leading-relaxed">
                                {concept.description}
                              </p>
                            </div>

                            {/* Provenance Citations */}
                            {concept.sources && concept.sources.length > 0 && (
                              <div className="pt-2 border-t border-slate-800/80">
                                <span className="text-[9px] font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1">
                                  <BookOpen className="w-2.5 h-2.5 text-cyan-400" />
                                  Provenance & Sources
                                </span>
                                <div className="mt-1 space-y-1">
                                  {concept.sources.map((src, sIdx) => (
                                    <div key={sIdx} className="text-[10px] text-slate-300 font-medium bg-slate-900/80 px-2 py-1 rounded-lg border border-slate-800/60">
                                      <span className="font-bold text-cyan-300">{src.name}</span>
                                      {src.chapter && <span className="text-slate-400"> — {src.chapter}</span>}
                                      {src.activity && <span className="text-amber-400"> ({src.activity})</span>}
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}

                            {/* Verified Equations / Formulas */}
                            {concept.equations && concept.equations.length > 0 && (
                              <div className="pt-2 border-t border-slate-800/80 space-y-1.5">
                                <span className="text-[9px] font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1">
                                  <Atom className="w-2.5 h-2.5 text-amber-400" />
                                  Scientific Equations
                                </span>
                                {concept.equations.map((eq, eIdx) => (
                                  <div key={eIdx} className="bg-slate-900/90 p-2 rounded-xl border border-slate-800/80 space-y-1">
                                    <div className="font-mono text-[11px] text-amber-300 font-bold overflow-x-auto">
                                      {eq.latex}
                                    </div>
                                    <p className="text-[9px] text-slate-400 leading-tight">
                                      {eq.meaning}
                                    </p>
                                  </div>
                                ))}
                              </div>
                            )}

                            {/* Misconception Alerts */}
                            {concept.misconceptions && concept.misconceptions.length > 0 && (
                              <div className="pt-2 border-t border-slate-800/80 space-y-1.5">
                                <span className="text-[9px] font-bold text-rose-400 uppercase tracking-wider flex items-center gap-1">
                                  <AlertTriangle className="w-2.5 h-2.5 text-rose-400" />
                                  Board Exam Pitfall
                                </span>
                                {concept.misconceptions.map((misc, mIdx) => (
                                  <div key={mIdx} className="bg-rose-950/20 p-2 rounded-xl border border-rose-900/40 space-y-1 text-[10px]">
                                    <div className="text-rose-300 font-medium">
                                      <span className="font-bold text-rose-400">Trap: </span>
                                      "{misc.claim}"
                                    </div>
                                    <div className="text-emerald-300 font-medium">
                                      <span className="font-bold text-emerald-400">Fact: </span>
                                      {misc.correction}
                                    </div>
                                  </div>
                                ))}
                              </div>
                            )}

                            {/* Related Concepts Graph Links */}
                            {concept.related_concepts && concept.related_concepts.length > 0 && (
                              <div className="pt-2 border-t border-slate-800/80 flex items-center gap-1 flex-wrap">
                                <span className="text-[9px] font-bold text-slate-500 uppercase tracking-wider block w-full">
                                  Graph Connections:
                                </span>
                                {concept.related_concepts.map((rc) => (
                                  <span key={rc} className="text-[9px] font-mono font-semibold px-1.5 py-0.5 rounded bg-slate-900 text-slate-400 border border-slate-800">
                                    #{rc}
                                  </span>
                                ))}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    );
                  })()}
                </div>
              )}

              {/* TAB 5: RAW JSON METADATA & EXPORT */}
              {activeTab === 'json' && (
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-400">metadata.json</span>
                    <button
                      onClick={handleCopyJson}
                      className="px-2 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 text-[11px] font-semibold rounded-lg flex items-center gap-1 transition-all"
                    >
                      {copiedJson ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                      {copiedJson ? 'Copied!' : 'Copy JSON'}
                    </button>
                  </div>
                  <pre className="bg-slate-950 p-3 rounded-xl border border-slate-800 text-[10px] font-mono text-cyan-300 overflow-x-auto max-h-96">
                    {JSON.stringify(selectedAsset, null, 2)}
                  </pre>
                </div>
              )}
            </div>

            {/* Bottom Actions */}
            <div className="p-4 border-t border-slate-800/80 bg-slate-950/80">
              <button
                onClick={handleCopyJson}
                className="w-full py-2 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-bold text-xs rounded-xl shadow-lg shadow-cyan-600/30 flex items-center justify-center gap-2 transition-all"
              >
                <Download className="w-3.5 h-3.5" />
                Export Asset Metadata Package
              </button>
            </div>
          </aside>
        </div>
      )}

      {/* ===================================================================== */}
      {/* MODE 2: VIRTUAL SCIENCE LAB GAME WORLD (FPS EXPLORATION)              */}
      {/* ===================================================================== */}
      {appMode === 'game' && (
        <div className="flex-1 relative flex">
          <div
            className="flex-1 h-full cursor-crosshair relative"
            onClick={handleInteractCurrentStation}
          >
            <Canvas
              shadows
              camera={{ position: [playerPosition[0], playerPosition[1], 0.08], fov: 60 }}
              gl={{ antialias: true, alpha: false }}
            >
              <color attach="background" args={['#eef2f6']} />
              <fog attach="fog" args={['#eef2f6', 1.2, 4.2]} />

              <ambientLight intensity={0.95} color="#f0fdf4" />
              <directionalLight
                castShadow
                position={[1.2, -1.5, 2.0]}
                intensity={2.2}
                color="#fffdfa"
                shadow-mapSize-width={2048}
                shadow-mapSize-height={2048}
                shadow-camera-near={0.1}
                shadow-camera-far={6.0}
              />
              <directionalLight position={[-1.2, 1.2, 1.2]} intensity={0.9} color="#dbeafe" />

              <Suspense fallback={null}>
                <LabGameWorld
                  activeStation={activeStation}
                  onSelectStation={(st) => setActiveStation(st)}
                  prismStep={prismStep}
                  burnStage={burnStage}
                  selectedPart={selectedPart}
                  onSelectPart={(name) => setSelectedPart(name)}
                  playerPosition={playerPosition}
                  onMovePlayer={(x, y) => setPlayerPosition([x, y])}
                  isFPSMode={isFPSMode}
                />

                <FPSController
                  playerPosition={playerPosition}
                  onMovePlayer={(x, y) => setPlayerPosition([x, y])}
                  isFPSMode={isFPSMode}
                  onInteract={handleInteractCurrentStation}
                  onAimApparatus={setAimedApparatus}
                />

                <ContactShadows
                  position={[0, -0.219, 0]}
                  opacity={0.4}
                  scale={3.0}
                  blur={2.0}
                  far={1.2}
                />
              </Suspense>
            </Canvas>

            {/* Reticle */}
            {isFPSMode && (
              <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
                <div className="relative flex flex-col items-center">
                  <div className="w-7 h-7 relative flex items-center justify-center">
                    <div className={`w-1.5 h-1.5 rounded-full shadow-[0_0_8px] transition-all duration-300 ${
                      isNearPrism ? 'bg-amber-400 shadow-amber-400 scale-125' : 'bg-cyan-400 shadow-cyan-400 animate-pulse'
                    }`} />
                    <div className="absolute top-0 w-0.5 h-2 bg-cyan-400/80 rounded" />
                    <div className="absolute bottom-0 w-0.5 h-2 bg-cyan-400/80 rounded" />
                    <div className="absolute left-0 h-0.5 w-2 bg-cyan-400/80 rounded" />
                    <div className="absolute right-0 h-0.5 w-2 bg-cyan-400/80 rounded" />
                  </div>

                  <div className={`mt-4 px-3.5 py-1.5 bg-slate-900/95 backdrop-blur-md rounded-xl border shadow-2xl flex items-center gap-2 text-xs font-extrabold transition-all ${
                    isNearPrism
                      ? 'border-amber-400/70 text-amber-300 ring-2 ring-amber-400/30 animate-bounce'
                      : 'border-cyan-500/40 text-cyan-300'
                  }`}>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-black uppercase ${
                      isNearPrism ? 'bg-amber-400 text-slate-950 shadow-md' : 'bg-cyan-500 text-slate-950'
                    }`}>
                      {isNearPrism ? 'E / CLICK1' : 'WASD'}
                    </span>
                    <span>
                      {isNearPrism ? (
                        prismStep === 1 ? '🎯 Take Action: Turn ON Torch' :
                        prismStep === 2 ? '🔦 Take Action: Trace Refraction' :
                        prismStep === 3 ? '📐 Take Action: Disperse 7 Rainbow Colors' :
                        '✨ Complete! Press [E] to Restart'
                      ) : (
                        `Walk to Prism Table (${distToPrism.toFixed(1)}m away)`
                      )}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}