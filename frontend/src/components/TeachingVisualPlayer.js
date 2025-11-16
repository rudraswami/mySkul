/**
 * Teaching Visual Player Component (Simplified)
 * Renders animated, interactive teaching visuals with stage-by-stage content
 * Uses Framer Motion for smooth transitions without complex canvas rendering
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { RotateCcw, ChevronRight, ChevronLeft, Lightbulb, BookOpen } from 'lucide-react';
import Lottie from 'lottie-react';
import InteractionLayer from './InteractionLayer';
// NEW: Complete Visual Professor Engine Components
import AnimatedScene from './visuals/AnimatedScene';
import RobustAnimationEngine from './visuals/RobustAnimationEngine';
import SimpleAnimationEngine from './visuals/SimpleAnimationEngine';
import ProfessorAvatar from './visuals/ProfessorAvatar';
import InteractiveControls from './visuals/InteractiveControls';
import SceneRenderer from './visuals/SceneRenderer';
// Block renderers (universal visual contract)
import TitleCard from './teaching/blocks/TitleCard';
import ConceptNodes from './teaching/blocks/ConceptNodes';
import RelationArrows from './teaching/blocks/RelationArrows';
import EquationBlock from './teaching/blocks/EquationBlock';
import CompareGrid from './teaching/blocks/CompareGrid';
import WorkedExample from './teaching/blocks/WorkedExample';
import TipCard from './teaching/blocks/TipCard';
import DefinitionCard from './teaching/blocks/DefinitionCard';
import LawList from './teaching/blocks/LawList';
import FlowMap from './teaching/blocks/FlowMap';
import DerivationSteps from './teaching/blocks/DerivationSteps';
import MCQQuiz from './teaching/blocks/MCQQuiz';
import EvidenceCallout from './teaching/blocks/EvidenceCallout';
import ControlPanel from './teaching/blocks/ControlPanel';
import MeterPanel from './teaching/blocks/MeterPanel';
import LivePlot from './teaching/blocks/LivePlot';
import SceneMotion1D from './teaching/blocks/SceneMotion1D';
import SceneCircuitOhm from './teaching/blocks/SceneCircuitOhm';
import BuddyBar from './teaching/blocks/BuddyBar';
import PredictCard from './teaching/blocks/PredictCard';

export default function TeachingVisualPlayer({ visualData, onComplete, onInteraction }) {
  // State management
  const [currentStage, setCurrentStage] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [progress, setProgress] = useState(0);
  const [showInteraction, setShowInteraction] = useState(false);
  const [userResponses, setUserResponses] = useState({});
  const [animationSpeed, setAnimationSpeed] = useState(1);
  const [stageParams, setStageParams] = useState({});
  const [lottieDataMap, setLottieDataMap] = useState({}); // Lottie animation data cache
  // NEW: Interactive values for sliders/toggles
  const [interactiveValues, setInteractiveValues] = useState({});
  const [sceneTime, setSceneTime] = useState(0); // Track animation timeline

  // Refs
  const progressInterval = useRef(null);
  const startTimeRef = useRef(null);
  const stageTimeoutRef = useRef(null);

  // Load Lottie animations for all stages
  useEffect(() => {
    if (!visualData || !visualData.stages) return;
    
    let cancelled = false;
    const loadLottieAssets = async () => {
      const allLottieUrls = new Set();
      
      // Collect all Lottie URLs from all stages
      visualData.stages.forEach(stage => {
        const lottieAssets = stage.lottie_assets || [];
        lottieAssets.forEach(asset => {
          if (asset.url && !lottieDataMap[asset.url]) {
            allLottieUrls.add(asset.url);
          }
        });
      });
      
      // Load each Lottie animation
      for (const url of allLottieUrls) {
        if (cancelled) break;
        try {
          const response = await fetch(url, { cache: 'force-cache' });
          if (!response.ok) continue;
          const data = await response.json();
          if (!cancelled) {
            setLottieDataMap(prev => ({ ...prev, [url]: data }));
          }
        } catch (error) {
          console.warn(`Failed to load Lottie animation from ${url}:`, error);
        }
      }
    };
    
    loadLottieAssets();
    
    return () => {
      cancelled = true;
    };
  }, [visualData, lottieDataMap]);

  // Calculate progress based on current stage
  useEffect(() => {
    if (!visualData || !Array.isArray(visualData.stages) || visualData.stages.length === 0) {
      setProgress(0);
      return;
    }
    const clampedIndex = Math.min(Math.max(currentStage, 0), visualData.stages.length - 1);
    const stageProgress = ((clampedIndex + 1) / visualData.stages.length) * 100;
    setProgress(stageProgress);
    // Initialize practical params from control_panel defaults
    try {
      const st = (visualData.stages || [])[clampedIndex] || {};
      const ctrl = (st.blocks || []).find(b => b.type === 'control_panel');
      if (ctrl && ctrl.sliders) {
        const defaults = {};
        ctrl.sliders.forEach(s => { defaults[s.id] = s.default; });
        if (ctrl.toggles) {
          ctrl.toggles.forEach(t => { defaults[t.id] = t.default; });
        }
        setStageParams(defaults);
      } else {
        setStageParams({});
      }
    } catch {}
  }, [currentStage, visualData]);

  // Auto-play stages
  useEffect(() => {
    if (!isPlaying || !visualData || showInteraction) return;

    const stages = Array.isArray(visualData.stages) ? visualData.stages : [];
    if (stages.length === 0) return;

    const clampedIndex = Math.min(Math.max(currentStage, 0), stages.length - 1);
    const currentStageData = stages[clampedIndex];
    const duration = currentStageData.duration_ms / animationSpeed;

    // Clear previous timeout
    if (stageTimeoutRef.current) {
      clearTimeout(stageTimeoutRef.current);
    }

    // Check if stage has interactions
    if (currentStageData.interactions && currentStageData.interactions.length > 0) {
      // Wait for stage to complete, then show interaction
      stageTimeoutRef.current = setTimeout(() => {
        setShowInteraction(true);
        setIsPlaying(false);
      }, duration);
    } else {
      // Auto-advance to next stage
      stageTimeoutRef.current = setTimeout(() => {
        if (clampedIndex < stages.length - 1) {
          setCurrentStage(prev => prev + 1);
        } else {
          // Reached the end
          setIsPlaying(false);
          handleComplete();
        }
      }, duration);
    }

    return () => {
      if (stageTimeoutRef.current) {
        clearTimeout(stageTimeoutRef.current);
      }
    };
  }, [isPlaying, currentStage, visualData, animationSpeed, showInteraction]);

  // Handle completion
  const handleComplete = useCallback(() => {
    if (onComplete) {
      onComplete({
        completed: true,
        userResponses: userResponses,
        totalDuration: visualData.total_duration_ms
      });
    }
  }, [onComplete, userResponses, visualData]);

  // Play/Pause control
  const togglePlayPause = useCallback(() => {
    setIsPlaying(!isPlaying);
  }, [isPlaying]);

  // Restart animation
  const restart = useCallback(() => {
    setCurrentStage(0);
    setProgress(0);
    setUserResponses({});
    setShowInteraction(false);
    setIsPlaying(false);
  }, []);

  // Skip to next stage
  const skipToNext = useCallback(() => {
    if (currentStage < visualData.stages.length - 1) {
      setCurrentStage(prev => prev + 1);
      setShowInteraction(false);
    }
  }, [currentStage, visualData]);

  // Previous stage
  const prevStage = useCallback(() => {
    if (currentStage > 0) {
      setCurrentStage(prev => Math.max(0, prev - 1));
      setShowInteraction(false);
    }
  }, [currentStage]);

  // Keyboard navigation
  useEffect(() => {
    const handler = (e) => {
      if (e.key === 'ArrowRight') skipToNext();
      if (e.key === 'ArrowLeft') prevStage();
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [skipToNext, prevStage]);

  // Handle interaction response
  const handleInteractionResponse = useCallback((response) => {
    setUserResponses(prev => ({
      ...prev,
      [`stage_${currentStage}`]: response
    }));

    setShowInteraction(false);

    // Continue to next stage
    if (currentStage < visualData.stages.length - 1) {
      setCurrentStage(prev => prev + 1);
      setIsPlaying(true);
    } else {
      // Last stage
      setIsPlaying(false);
      handleComplete();
    }

    if (onInteraction) {
      onInteraction({
        stage: currentStage,
        response: response
      });
    }
  }, [currentStage, visualData, onInteraction, handleComplete]);

  // Debug logging
  useEffect(() => {
    if (visualData) {
      console.log('[TeachingVisualPlayer] Visual Data:', visualData);
      console.log('[TeachingVisualPlayer] Current Stage:', currentStage);
      console.log('[TeachingVisualPlayer] Stages:', visualData.stages);
      if (visualData.stages && visualData.stages[currentStage]) {
        console.log('[TeachingVisualPlayer] Current Stage Data:', visualData.stages[currentStage]);
        console.log('[TeachingVisualPlayer] Animations:', visualData.stages[currentStage].animations);
      }
    }
  }, [visualData, currentStage]);

  // Render loading state
  if (!visualData) {
    return (
      <div className="flex items-center justify-center h-96 bg-gradient-to-br from-purple-50 to-blue-50 rounded-2xl">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Preparing your visual lesson...</p>
        </div>
      </div>
    );
  }

  // If stages are missing or empty, render a safe fallback instead of crashing
  const stages = Array.isArray(visualData.stages) ? visualData.stages : [];
  if (stages.length === 0) {
    return (
      <div className="w-full bg-yellow-50 border-2 border-yellow-300 text-yellow-900 rounded-2xl p-6">
        <p className="font-semibold">No stages available for this teaching visual.</p>
        <p className="text-sm mt-2">Ask again or try a different question.</p>
        <pre className="text-xs mt-4 bg-yellow-100 p-3 rounded overflow-auto">{JSON.stringify(visualData, null, 2)}</pre>
      </div>
    );
  }
  const clampedStage = Math.min(Math.max(currentStage, 0), stages.length - 1);
  const currentStageData = stages[clampedStage] || {};
  const metadata = visualData.metadata || {};

  // Render stage content visually
  const renderStageContent = (stageData) => {
    if (!stageData) {
      return (
        <div className="w-full max-w-2xl bg-yellow-100 border-2 border-yellow-400 rounded-xl p-6 text-center">
          <p className="text-yellow-900 font-medium">Stage data missing</p>
        </div>
      );
    }

    // Prefer block-based universal visuals; fallback to legacy animation types
    const blocks = stageData.blocks || [];
    const animations = stageData.animations || [];
    const lottieAssets = stageData.lottie_assets || []; // Lottie animations from universal template

    // Compute subject accent color
    const subject = (metadata.subject || 'general').toLowerCase();
    const SUBJECT_ACCENT = {
      physics: '#7c3aed',
      chemistry: '#059669',
      biology: '#15803d',
      mathematics: '#2563eb',
      math: '#2563eb',
      english: '#1f2937',
      general: '#4f46e5'
    };
    const accent = SUBJECT_ACCENT[subject] || SUBJECT_ACCENT.general;

    return (
      <motion.div
        key={`stage-${currentStage}`}
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        transition={{ duration: 0.4 }}
        className="w-full h-full flex flex-col items-center justify-center p-4 sm:p-8 space-y-4 sm:space-y-6"
        style={{
          borderTop: `3px solid ${accent}`,
          backgroundImage: 'radial-gradient(rgba(0,0,0,0.03) 1px, transparent 1px)',
          backgroundSize: '12px 12px',
          wordBreak: 'break-word'
        }}
      >
        {/* Topic Badge */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white/90 backdrop-blur-sm rounded-full px-6 py-2 shadow-md"
        >
          <span className="text-sm font-semibold text-purple-700 flex items-center gap-2">
            <BookOpen className="w-4 h-4" />
            {metadata.topic || 'Teaching Visual'}
          </span>
        </motion.div>

        {/* PRIORITY 1: Lottie animations from universal template */}
        {lottieAssets && lottieAssets.length > 0 && (
          <div className="w-full max-w-2xl relative">
            {lottieAssets.map((asset, index) => {
              const lottieData = lottieDataMap[asset.url];
              if (!lottieData) return null;
              return (
                <motion.div
                  key={`lottie-${index}`}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.2 + (index * 0.1) }}
                  className="w-full h-64 sm:h-80 flex items-center justify-center"
                >
                  <Lottie
                    animationData={lottieData}
                    loop={asset.loop !== false}
                    autoplay={asset.autoplay !== false && isPlaying}
                    speed={asset.speed || 1.0}
                    style={{ width: '100%', height: '100%' }}
                  />
                </motion.div>
              );
            })}
          </div>
        )}

        {/* PRIORITY 2: Block-based visual contract */}
        {blocks && blocks.length > 0 && (
          blocks.map((block, index) => (
            <motion.div
              key={`block-${index}`}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 + (index * 0.06) }}
              className="w-full max-w-2xl overflow-hidden"
            >
              {renderBlock(block)}
            </motion.div>
          ))
        )}

        {/* PRIORITY 3: Legacy animations */}
        {(!lottieAssets || lottieAssets.length === 0) && (!blocks || blocks.length === 0) && animations && animations.length > 0 && (
          animations.map((animation, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 + (index * 0.1) }}
              className="w-full max-w-2xl"
            >
              {renderAnimation(animation)}
            </motion.div>
          ))
        )}

        {/* FALLBACK: No visual content */}
        {(!lottieAssets || lottieAssets.length === 0) && (!blocks || blocks.length === 0) && (!animations || animations.length === 0) && (
          <div className="w-full max-w-2xl bg-yellow-100 border-2 border-yellow-400 rounded-xl p-6 text-center">
            <p className="text-yellow-900 font-medium">No visual content found for this stage</p>
            <p className="text-sm text-yellow-700 mt-2">Stage: {currentStage + 1}</p>
          </div>
        )}

        {/* Professor Avatar Overlay */}
        {visualData.professor_avatar && visualData.professor_avatar.visible && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            className="absolute top-4 left-4 flex items-center gap-2 bg-white/90 backdrop-blur-sm rounded-full px-3 py-2 shadow-md"
          >
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-400 to-pink-400 flex items-center justify-center">
              <span className="text-white text-sm font-semibold">👨‍🏫</span>
            </div>
            <span className="text-sm font-medium text-gray-700">Professor</span>
          </motion.div>
        )}

        {/* Friendly buddy narration (short); fallback to Hinglish microcopy for practical stages */}
        {(() => {
          const hasPractical = (stageData.blocks || []).some(b => b.type === 'control_panel' || b.type === 'predict_card');
          let text = (stageData.narration || stageData.emphasis || '').trim();
          const micro = {
            physics: [
              'Socho bhai: force badhaoge to a kya hoga?',
              'Bowler pace badhaye to ball kaise react karegi?',
              'Action kiya to reaction turant milta hai!'
            ],
            chemistry: [
              'Socho: R badhaoge, current kaisa hoga?',
              'Ionic = transfer; Covalent = sharing — yaad rakho!',
              'Concentration badhe to pH girega, samjha?'
            ],
            biology: [
              'Light badhe to bubbles badhenge — leaf factory ON!',
              'Socho: CO₂ kam ho to rate kaisa hoga?',
              'Plant chakra — input → process → output.'
            ],
            mathematics: [
              'Angle set karo — range kaise badlegi?',
              'Speed double to KE four times — yaad rakho!',
              'Pehle guess, phir compute.'
            ],
            general: [
              'Pehle guess, fir slider ghumao — dekhte hain!',
              'Chhota experiment, badi samajh.',
              'Board pe live demo, 1 minute me!'
            ]
          };
          if (hasPractical && (!text || text.length < 8)) {
            const subj = (metadata.subject || 'general').toLowerCase();
            const arr = micro[subj] || micro.general;
            text = arr[currentStage % arr.length];
          }
          if (!text || text.length > 90) return null;
          const hasTitle = (stageData.blocks || []).some(b => b.type === 'title_card' && text.toLowerCase().includes((b.title || '').toLowerCase()));
          if (hasTitle) return null;
          return <BuddyBar text={text} subject={metadata.subject} />;
        })()}

        {/* Cultural Metaphor Indicator */}
        {metadata.cultural_metaphor && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6 }}
            className="text-sm text-purple-600 font-medium bg-white/70 px-4 py-2 rounded-lg"
          >
            Using {metadata.cultural_metaphor} metaphor 🌟
          </motion.div>
        )}
      </motion.div>
    );
  };

  // Render a universal visual block
  const renderBlock = (block) => {
    switch (block.type) {
      case 'title_card':
        return <TitleCard title={block.title} subtitle={block.subtitle} />;
      case 'concept_nodes':
        return <ConceptNodes nodes={block.nodes} layout={block.layout} />;
      case 'relation_arrows':
        return <RelationArrows relations={block.relations} />;
      case 'equation':
        return <EquationBlock tex={block.tex} highlight={block.highlight} />;
      case 'compare_grid':
        return <CompareGrid left={block.left} right={block.right} />;
      case 'worked_example':
        return <WorkedExample steps={block.steps} icon={block.icon} />;
      case 'tip_card':
        return <TipCard text={block.text} tip_type={block.tip_type} />;
      case 'definition_card':
        return <DefinitionCard term={block.term} definition={block.definition} />;
      case 'law_list':
        return <LawList laws={block.laws} />;
      case 'flow_map':
        return <FlowMap nodes={block.nodes} edges={block.edges} />;
      case 'derivation_steps':
        return <DerivationSteps steps={block.steps} />;
      case 'mcq_quiz':
        return <MCQQuiz question={block.question} options={block.options} correct={block.correct} explanation={block.explanation} />;
      case 'evidence_callout':
        return <EvidenceCallout text={block.text} source={block.source} />;
      case 'control_panel':
        return (
          <ControlPanel
            sliders={block.sliders}
            toggles={block.toggles}
            params={stageParams}
            onChange={(id, v) => setStageParams(prev => ({ ...prev, [id]: v }))}
          />
        );
      case 'meter_panel':
        return <MeterPanel meters={block.meters} params={stageParams} />;
      case 'live_plot':
        return (
          <LivePlot
            x_label={block.x_label}
            y_label={block.y_label}
            expr={block.expr}
            series={block.series}
            x_min={block.x_min}
            x_max={block.x_max}
            samples={block.samples}
            params={stageParams}
          />
        );
      case 'scene_motion_1d':
        return <SceneMotion1D params={stageParams} tMax={block.t_max || 2} style={block.style || 'cart'} />;
      case 'scene_circuit_ohm':
        return <SceneCircuitOhm params={stageParams} />;
      case 'predict_card':
        return <PredictCard question={block.question} expected={block.expected} />;
      case 'animated_scene':
        // SCENE RENDERER - uses real SVG entities with Framer Motion
        console.log('[TeachingVisualPlayer] Using SceneRenderer');
        console.log('[TeachingVisualPlayer] Scene:', block.scene);
        console.log('[TeachingVisualPlayer] Animation sequence:', block.animation_sequence);
        
        return (
          <div className="w-full max-w-4xl space-y-4">
            {/* Main scene with animated entities */}
            <SceneRenderer
              sceneSpec={block.scene}
              animationSequence={block.animation_sequence || []}
              currentStageIndex={currentStage}
              isPlaying={isPlaying}
            />
            
            {/* Interactive Controls for this scene */}
            {block.scene?.interactivity && (
              <div className="bg-white/90 backdrop-blur-sm rounded-xl p-4 shadow-md">
                <InteractiveControls
                  controls={block.scene.interactivity}
                  values={interactiveValues}
                  onChange={(id, value) => {
                    setInteractiveValues(prev => ({ ...prev, [id]: value }));
                  }}
                  showHinglish={true}
                />
              </div>
            )}
            
            {/* Professor Avatar - Always visible */}
            <div className="absolute bottom-4 right-4 z-50">
              <div className="relative">
                <div className="w-32 h-32 rounded-full bg-gradient-to-br from-purple-400 to-pink-400 flex items-center justify-center text-6xl border-4 border-white shadow-2xl">
                  👨‍🏫
                </div>
                <div className="absolute -top-2 left-1/2 transform -translate-x-1/2 bg-gradient-to-r from-purple-600 to-pink-600 text-white px-3 py-1 rounded-full text-xs font-bold shadow-lg">
                  Professor
                </div>
              </div>
            </div>
          </div>
        );
      case 'entity':
        // Legacy entity block (kept for backward compatibility, but animated_scene preferred)
        return (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ 
              opacity: block.visible ? 1 : 0.3, 
              scale: block.highlight ? 1.05 : 1 
            }}
            transition={{ duration: 0.3 }}
            className={`inline-flex items-center gap-2 px-4 py-2 rounded-full ${
              block.highlight 
                ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg' 
                : 'bg-gradient-to-r from-blue-50 to-purple-50 text-purple-700'
            }`}
          >
            <span className="text-2xl">
              {block.entity_id.includes('metro') && '🚇'}
              {block.entity_id.includes('train') && '🚊'}
              {block.entity_id.includes('car') && '🚗'}
              {block.entity_id.includes('ball') && '🏏'}
              {block.entity_id.includes('cricket') && '🏏'}
              {block.entity_id.includes('atom') && '⚛️'}
              {block.entity_id.includes('electron') && '⚡'}
              {block.entity_id.includes('nucleus') && '🔵'}
              {block.entity_id.includes('chloroplast') && '🌱'}
              {block.entity_id.includes('mitochondria') && '🔴'}
              {block.entity_id.includes('arrow') && '➡️'}
              {block.entity_id.includes('speedometer') && '⏱️'}
              {block.entity_id.includes('landmark') && '📍'}
              {!block.entity_id.match(/(metro|train|car|ball|cricket|atom|electron|nucleus|chloroplast|mitochondria|arrow|speedometer|landmark)/) && '🔷'}
            </span>
            <span className="text-sm font-medium capitalize">
              {block.entity_id.replace(/_/g, ' ')}
            </span>
          </motion.div>
        );
      case 'concept_detail':
        // Concept detail block from expanded stages
        return (
          <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-2xl p-6 border-2 border-indigo-200">
            <h3 className="text-lg font-bold text-indigo-900 mb-2">{block.title}</h3>
            {block.description && (
              <p className="text-indigo-700 text-sm">{block.description}</p>
            )}
          </div>
        );
      default:
        return (
          <div className="bg-yellow-50 border-2 border-yellow-300 rounded-xl p-3">
            <p className="text-yellow-900 text-sm font-medium">Unsupported block type</p>
            <pre className="text-xs mt-2 overflow-auto">{JSON.stringify(block, null, 2)}</pre>
          </div>
        );
    }
  };

  // Render individual animation based on type
  const renderAnimation = (animation) => {
    const type = animation.type;

    switch (type) {
      case 'scene_setup':
        return (
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg text-center">
            <div className="text-6xl mb-4">
              {animation.elements?.includes('kitchen') && '🏠'}
              {animation.elements?.includes('person') && '👨‍🍳'}
              {animation.elements?.includes('chai_cup') && '☕'}
              {animation.elements?.includes('cricket_field') && '🏏'}
              {animation.elements?.includes('train') && '🚂'}
            </div>
            <p className="text-gray-700 font-medium">Scene Setup</p>
          </div>
        );

      case 'split_screen_enter':
        return (
          <div className="grid grid-cols-2 gap-4">
            <div className={`bg-green-100 rounded-xl p-6 text-center border-2 ${animation.side === 'left' ? 'border-green-500 shadow-lg' : 'border-green-200'}`}>
              <h3 className="font-bold text-green-800 mb-2">{animation.label}</h3>
              <div className="text-4xl">📝</div>
            </div>
            <div className={`bg-blue-100 rounded-xl p-6 text-center border-2 ${animation.side === 'right' ? 'border-blue-500 shadow-lg' : 'border-blue-200'}`}>
              <h3 className="font-bold text-blue-800 mb-2">Compare</h3>
              <div className="text-4xl">🔍</div>
            </div>
          </div>
        );

      case 'sentence_build':
        return (
          <div className="bg-white rounded-xl p-6 shadow-lg">
            <div className="flex flex-wrap gap-3 justify-center">
              {animation.words?.map((word, idx) => {
                const highlightKey = Object.keys(animation.highlights || {}).find(key => key === word);
                const colorKey = highlightKey ? animation.highlights[highlightKey] : null;
                const color = colorKey ? animation.colors?.[colorKey] : '#6b7280';

                return (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.2 }}
                    className="px-4 py-2 rounded-lg font-bold text-white shadow-md"
                    style={{ backgroundColor: color }}
                  >
                    {word}
                  </motion.div>
                );
              })}
            </div>
          </div>
        );

      case 'character_spotlight':
      case 'object_spotlight':
        return (
          <div className="bg-gradient-to-br from-yellow-100 to-orange-100 rounded-xl p-8 text-center shadow-lg border-4 border-yellow-400">
            <div className="text-7xl mb-4">⭐</div>
            <h3 className="text-2xl font-bold text-orange-800 mb-2">
              {animation.character || animation.object}
            </h3>
            <p className="text-orange-700">In the spotlight!</p>
          </div>
        );

      case 'action_arrow':
      case 'action_arrow_reverse':
        return (
          <div className="bg-white rounded-xl p-6 shadow-lg">
            <div className="flex items-center justify-center gap-4">
              <div className="text-4xl bg-green-100 p-4 rounded-xl">{animation.from || '📍'}</div>
              <div className="flex flex-col items-center">
                <div className="text-2xl">{type === 'action_arrow_reverse' ? '⬅️' : '➡️'}</div>
                <p className="text-sm font-medium text-gray-700 mt-1">{animation.action}</p>
              </div>
              <div className="text-4xl bg-blue-100 p-4 rounded-xl">{animation.to || '🎯'}</div>
            </div>
          </div>
        );

      case 'comparison_arrows':
        return (
          <div className="bg-white rounded-xl p-6 shadow-lg space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-green-50 p-4 rounded-lg border-2 border-green-300">
                <p className="font-bold text-green-800">{animation.left_sentence}</p>
              </div>
              <div className="bg-blue-50 p-4 rounded-lg border-2 border-blue-300">
                <p className="font-bold text-blue-800">{animation.right_sentence}</p>
              </div>
            </div>
            <div className="text-center text-4xl">↔️</div>
          </div>
        );

      case 'summary_card':
        return (
          <div className="bg-gradient-to-br from-purple-100 to-blue-100 rounded-xl p-6 shadow-lg">
            <h3 className="text-xl font-bold text-purple-900 mb-4 text-center">{animation.title}</h3>
            <div className="space-y-3">
              {animation.points?.map((point, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.15 }}
                  className="flex items-start gap-3 bg-white/70 p-3 rounded-lg"
                >
                  <span className="text-xl" style={{ color: point.color }}>{point.icon}</span>
                  <p className="text-gray-800 font-medium">{point.text}</p>
                </motion.div>
              ))}
            </div>
          </div>
        );

      case 'celebration':
        return (
          <div className="text-center">
            <motion.div
              animate={{ scale: [1, 1.2, 1], rotate: [0, 360, 720] }}
              transition={{ duration: 1, repeat: Infinity }}
              className="text-6xl mb-4"
            >
              🎉
            </motion.div>
            <p className="text-2xl font-bold text-purple-700">Great Job!</p>
          </div>
        );

      case 'fade_in':
      case 'dual_sentence_build':
      case 'decision_tree':
      case 'cricket_scene':
      case 'train_timeline':
      case 'train_move_to_station':
      case 'train_at_station':
      case 'train_heading_to_station':
      case 'transformation_morph':
      case 'split_comparison':
        // Fallback for animation types without specific rendering
        return (
          <div className="bg-white/70 backdrop-blur-sm rounded-xl p-6 shadow-md text-center">
            <div className="text-5xl mb-3">🎬</div>
            <p className="text-sm text-gray-600 font-medium">
              {type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
            </p>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="teaching-visual-player bg-white rounded-2xl shadow-xl overflow-hidden border-2 border-purple-200">
      {/* Main Visual Area */}
      <div className="relative bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-50 min-h-[400px]">
        <AnimatePresence mode="wait">
          {renderStageContent(currentStageData)}
        </AnimatePresence>

        {/* Interaction Overlay */}
        <AnimatePresence>
          {showInteraction && currentStageData.interactions && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-10 p-8"
            >
              <InteractionLayer
                interaction={currentStageData.interactions[0]}
                onResponse={handleInteractionResponse}
                stage={currentStage}
              />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Stage Indicator */}
        <div className="absolute top-4 left-4 bg-white/90 backdrop-blur-sm rounded-lg px-3 py-1.5 shadow-md">
          <span className="text-xs font-medium text-gray-600">
            Stage {clampedStage + 1} of {stages.length}
          </span>
        </div>

        {/* Emphasis Indicator */}
        {currentStageData.emphasis && (
          <motion.div
            key={`emphasis-${currentStage}`}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="absolute bottom-4 left-4 right-4 bg-yellow-100/95 backdrop-blur-sm border-2 border-yellow-400 rounded-xl p-4 shadow-lg"
          >
            <div className="flex items-start gap-3">
              <Lightbulb className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
              <p className="text-sm font-semibold text-yellow-900">
                {currentStageData.emphasis}
              </p>
            </div>
          </motion.div>
        )}
      </div>

      {/* Narration Bar */}
      <div className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white p-4">
        <div className="flex items-center gap-3">
          <div className="flex-shrink-0">
            <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center">
              <span className="text-xl">👨‍🏫</span>
            </div>
          </div>
          <div className="flex-1">
            <motion.p
              key={`narration-${currentStage}`}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              className="text-sm font-medium leading-relaxed"
            >
              {currentStageData.narration}
            </motion.p>
          </div>
          {/* Volume control removed for cleaner UI */}
        </div>
      </div>

      {/* Progress Bar */}
      <div className="bg-gray-100 h-1.5 relative">
        <motion.div
          className="absolute inset-y-0 left-0 bg-gradient-to-r from-purple-600 to-indigo-600"
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.5 }}
        />
        {/* Stage markers */}
        {stages.map((_, index) => {
          const denom = Math.max(stages.length - 1, 1);
          const position = (index / denom) * 100;
          return (
            <div
              key={index}
              className={`absolute top-1/2 -translate-y-1/2 w-3 h-3 rounded-full bg-white border-2 transition-all ${
                index <= clampedStage ? 'border-purple-600 scale-110' : 'border-gray-300'
              }`}
              style={{ left: `${position}%`, transform: 'translateX(-50%) translateY(-50%)' }}
            />
          );
        })}
      </div>

      {/* Controls */}
      <div className="flex items-center justify-between p-4 bg-gray-50 border-t border-gray-200">
        <div className="flex items-center gap-2">
          {/* Prev */}
          <button
            onClick={prevStage}
            disabled={clampedStage === 0 || showInteraction}
            className="px-3 py-2 bg-white text-gray-700 rounded-lg hover:bg-gray-100 transition-colors border border-gray-300 flex items-center gap-1 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ChevronLeft className="w-4 h-4" />
            <span className="text-sm font-medium">Prev</span>
          </button>

          {/* Restart */}
          <button
            onClick={restart}
            className="px-3 py-2 bg-white text-gray-700 rounded-lg hover:bg-gray-100 transition-colors border border-gray-300 flex items-center gap-1"
          >
            <RotateCcw className="w-4 h-4" />
            <span className="text-sm font-medium">Restart</span>
          </button>

          {/* Next */}
          <button
            onClick={skipToNext}
            disabled={clampedStage >= stages.length - 1 || showInteraction}
            className="px-3 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center gap-1 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span className="text-sm font-medium">Next</span>
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Metadata Footer */}
      <div className="bg-gray-100 px-4 py-2 border-t border-gray-200">
        <div className="flex items-center justify-between text-xs text-gray-600">
          <div className="flex items-center gap-4">
            <span>📚 {metadata.subject || 'General'}</span>
            <span>🎯 {metadata.concept_type || 'Concept'}</span>
            {metadata.grade_level && <span>🎓 Grade {metadata.grade_level}</span>}
          </div>
          <div>
            Duration: {Math.round(visualData.total_duration_ms / 1000)}s
          </div>
        </div>
      </div>
    </div>
  );
}
