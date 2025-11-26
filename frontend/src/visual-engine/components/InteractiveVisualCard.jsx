/**
 * Interactive Visual Card
 * Universal visual loader for ALL subjects and concepts
 */

import React, { useState, useMemo, Suspense, lazy } from 'react';
import { motion } from 'framer-motion';
import { getConceptConfig } from '../config/conceptRegistry';

// Lazy load ALL scene components
const CompactPhysicsScene = lazy(() => import('./CompactPhysicsScene'));
const MotionVisualScene = lazy(() => import('./MotionVisualScene'));
const GravityVisualScene = lazy(() => import('./GravityVisualScene'));
const ChemistryAtomScene = lazy(() => import('./subjects/ChemistryAtomScene'));
const BiologyCellScene = lazy(() => import('./subjects/BiologyCellScene'));
const MathPythagorasScene = lazy(() => import('./subjects/MathPythagorasScene'));

// Scene component mapping
const SCENE_COMPONENTS = {
  // Physics
  CompactPhysicsScene,
  MotionScene: MotionVisualScene,
  GravityScene: GravityVisualScene,
  FrictionScene: CompactPhysicsScene,
  MomentumScene: CompactPhysicsScene,
  EnergyScene: CompactPhysicsScene,
  WaveScene: CompactPhysicsScene,
  LightScene: CompactPhysicsScene,
  ElectricityScene: CompactPhysicsScene,
  
  // Chemistry
  AtomScene: ChemistryAtomScene,
  MoleculeScene: ChemistryAtomScene,
  BondingScene: ChemistryAtomScene,
  ReactionScene: ChemistryAtomScene,
  AcidBaseScene: ChemistryAtomScene,
  PeriodicScene: ChemistryAtomScene,
  
  // Biology
  CellScene: BiologyCellScene,
  DNAScene: BiologyCellScene,
  PhotosynthesisScene: BiologyCellScene,
  RespirationScene: BiologyCellScene,
  HeartScene: BiologyCellScene,
  CirculatoryScene: BiologyCellScene,
  DigestiveScene: BiologyCellScene,
  EvolutionScene: BiologyCellScene,
  
  // Mathematics
  EquationScene: MathPythagorasScene,
  QuadraticScene: MathPythagorasScene,
  PolynomialScene: MathPythagorasScene,
  TriangleScene: MathPythagorasScene,
  CircleScene: MathPythagorasScene,
  PythagorasScene: MathPythagorasScene,
  TrigScene: MathPythagorasScene,
  DerivativeScene: MathPythagorasScene,
  IntegralScene: MathPythagorasScene,
  LimitScene: MathPythagorasScene,
  ProbabilityScene: MathPythagorasScene,
  StatisticsScene: MathPythagorasScene,
};

const InteractiveVisualCard = ({
  question,
  subject = null,
  studentProfile,
  fallbackSvg,
  embedded = true,
  onInteraction,
  onClose,
}) => {
  const [hasError, setHasError] = useState(false);

  // Get concept configuration from registry
  const conceptConfig = useMemo(() => {
    if (!question) return null;
    return getConceptConfig(question, subject);
  }, [question, subject]);

  // Get the appropriate scene component
  const SceneComponent = useMemo(() => {
    if (!conceptConfig) return null;
    return SCENE_COMPONENTS[conceptConfig.scene] || CompactPhysicsScene;
  }, [conceptConfig]);

  // Handle errors gracefully
  if (hasError || !SceneComponent) {
    if (fallbackSvg) {
      return (
        <motion.div
          className="my-4 rounded-xl overflow-hidden border border-purple-200 shadow-lg"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <div 
            className="bg-white p-4"
            dangerouslySetInnerHTML={{ __html: fallbackSvg }}
          />
        </motion.div>
      );
    }
    return null;
  }

  return (
    <motion.div
      className="my-4"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Suspense fallback={<LoadingState subject={conceptConfig?.subject} />}>
        <SceneComponent
          embedded={embedded}
          concept={conceptConfig?.keyword}
          formula={conceptConfig?.formula}
          onClose={onClose}
        />
      </Suspense>
    </motion.div>
  );
};

// Loading state with subject-specific styling
const LoadingState = ({ subject }) => {
  const colors = {
    physics: 'from-orange-50 to-yellow-50 border-orange-200',
    chemistry: 'from-purple-50 to-indigo-50 border-purple-200',
    biology: 'from-green-50 to-teal-50 border-green-200',
    mathematics: 'from-blue-50 to-cyan-50 border-blue-200',
  };

  const icons = {
    physics: '⚡',
    chemistry: '⚛️',
    biology: '🧬',
    mathematics: '📐',
  };

  const colorClass = colors[subject] || colors.physics;
  const icon = icons[subject] || '📊';

  return (
    <motion.div 
      className={`rounded-xl overflow-hidden bg-gradient-to-br ${colorClass} border`}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      <div className="flex flex-col items-center justify-center h-48 space-y-3">
        <motion.div 
          className="text-4xl"
          animate={{ scale: [1, 1.2, 1] }}
          transition={{ repeat: Infinity, duration: 1.5 }}
        >
          {icon}
        </motion.div>
        <p className="text-gray-600 font-medium">Loading visual...</p>
      </div>
    </motion.div>
  );
};

export default InteractiveVisualCard;
