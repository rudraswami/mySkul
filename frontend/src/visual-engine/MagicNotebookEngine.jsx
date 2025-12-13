/**
 * ✨ MAGIC NOTEBOOK ENGINE V6
 * ============================
 * 
 * Complete intelligent visual teaching system
 * 
 * Combines all 10 phases:
 * 1. Core Renderer (primitives, RoughJS, Framer Motion)
 * 2. Sketchy Controls (no HTML)
 * 3. Drawing Hand (3 poses, path following)
 * 4. Narrative Engine (5-beat teaching)
 * 5. SceneComposer (5 layout algorithms)
 * 6. ConceptBreaker (LLM + rules)
 * 7. Validators (4 subjects, 30+ rules)
 * 8. Metaphors (14 Indian contexts)
 * 9. 8 Master Modes (complete implementations)
 * 10. Integration (THIS FILE!)
 */

import React, { useState, useEffect } from 'react';
import { useBreakConceptMutation } from '../hooks/useConceptBreaker';
import { composeScene } from './intelligence/SceneComposer';
import { applyMetaphor } from './metaphors/MetaphorMapper';
import UniversalSketchRenderer from './core/UniversalSketchRenderer';
import { NarrativePlayer } from './narrative';
import { ModeRouter } from './modes';
import { useValidationFeedback } from './feedback';

// ============================================
// MAGIC NOTEBOOK ENGINE
// ============================================

/**
 * Main Magic Notebook Engine Component
 * The complete teaching visual system
 */
export const MagicNotebookEngine = ({
  // Input
  question,
  context = {},
  
  // Options
  options = {},
  
  // Callbacks
  onBlueprintGenerated,
  onNarrativeComplete,
  onError,
  
  // Override
  preGeneratedBlueprint,
  
  // UI
  showControls = true,
  showNarrative = true,
  showValidation = true,
  height = 400,
  width = 400,
  className = '',
}) => {
  const [blueprint, setBlueprint] = useState(preGeneratedBlueprint || null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Concept breaking
  const { mutate: breakConcept, isLoading: isBreaking } = useBreakConceptMutation();
  
  // Validation
  const { validate, validation } = useValidationFeedback(context.subject);
  
  /**
   * Generate blueprint from question
   */
  useEffect(() => {
    if (preGeneratedBlueprint) {
      setBlueprint(preGeneratedBlueprint);
      return;
    }
    
    if (!question) return;
    
    setLoading(true);
    setError(null);
    
    // Step 1: Break concept (ConceptBreaker)
    breakConcept(
      { question, context },
      {
        onSuccess: (conceptBlueprint) => {
          // Step 2: Compose scene (SceneComposer)
          let positionedBlueprint = composeScene(conceptBlueprint, {
            canvasWidth: width,
            canvasHeight: height,
          });
          
          // Step 3: Apply metaphor (MetaphorMapper)
          if (positionedBlueprint.metaphor || options.preferMetaphor) {
            positionedBlueprint = applyMetaphor(
              positionedBlueprint,
              options.preferMetaphor || positionedBlueprint.metaphor
            );
          }
          
          // Step 4: Set blueprint
          setBlueprint(positionedBlueprint);
          setLoading(false);
          onBlueprintGenerated?.(positionedBlueprint);
        },
        onError: (err) => {
          setError(err.message || 'Failed to generate visual');
          setLoading(false);
          onError?.(err);
        },
      }
    );
  }, [question, context, preGeneratedBlueprint, width, height]);
  
  /**
   * Render states
   */
  if (loading || isBreaking) {
    return (
      <div className={`magic-notebook-engine loading ${className}`} style={{ height }}>
        <LoadingState />
      </div>
    );
  }
  
  if (error) {
    return (
      <div className={`magic-notebook-engine error ${className}`} style={{ height }}>
        <ErrorState error={error} onRetry={() => window.location.reload()} />
      </div>
    );
  }
  
  if (!blueprint) {
    return (
      <div className={`magic-notebook-engine empty ${className}`} style={{ height }}>
        <EmptyState />
      </div>
    );
  }
  
  /**
   * Main render
   */
  return (
    <div
      className={`magic-notebook-engine ${className}`}
      style={{
        position: 'relative',
        width,
        height,
        background: blueprint.background?.color || '#FFFEF7',
        borderRadius: '12px',
        overflow: 'hidden',
        boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
      }}
    >
      {/* Main Renderer */}
      <UniversalSketchRenderer
        blueprint={blueprint}
        width={width}
        height={height}
      />
      
      {/* Narrative Overlay (5-beat teaching) */}
      {showNarrative && blueprint.beats && (
        <NarrativePlayer
          blueprint={blueprint}
          options={{
            enableHand: true,
            enableBubbles: true,
            speed: options.narrativeSpeed || 1.0,
          }}
          showControls={showControls}
          onComplete={onNarrativeComplete}
        />
      )}
      
      {/* Mode-specific rendering */}
      <svg
        width={width}
        height={height}
        style={{ position: 'absolute', top: 0, left: 0, pointerEvents: 'none' }}
      >
        <ModeRouter blueprint={blueprint} />
      </svg>
      
      {/* Metadata Badge */}
      {options.showMetadata !== false && (
        <MetadataBadge blueprint={blueprint} />
      )}
    </div>
  );
};

// ============================================
// LOADING STATE
// ============================================

const LoadingState = () => {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      height: '100%',
      gap: '16px',
    }}>
      <div style={{ fontSize: '48px' }}>🧠</div>
      <div style={{
        fontFamily: '"Kalam", "Comic Sans MS", cursive',
        fontSize: '18px',
        color: '#666',
      }}>
        Breaking down concept...
      </div>
      <div style={{
        width: '200px',
        height: '4px',
        background: '#E5E7EB',
        borderRadius: '2px',
        overflow: 'hidden',
      }}>
        <div
          style={{
            height: '100%',
            background: '#3B82F6',
            animation: 'loading 1.5s ease-in-out infinite',
          }}
        />
      </div>
      <style>{`
        @keyframes loading {
          0% { width: 0%; margin-left: 0%; }
          50% { width: 75%; margin-left: 12.5%; }
          100% { width: 0%; margin-left: 100%; }
        }
      `}</style>
    </div>
  );
};

// ============================================
// ERROR STATE
// ============================================

const ErrorState = ({ error, onRetry }) => {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      height: '100%',
      gap: '16px',
      padding: '40px',
    }}>
      <div style={{ fontSize: '48px' }}>😕</div>
      <div style={{
        fontFamily: '"Kalam", "Comic Sans MS", cursive',
        fontSize: '16px',
        color: '#EF4444',
        textAlign: 'center',
      }}>
        {error}
      </div>
      <button
        onClick={onRetry}
        style={{
          padding: '8px 16px',
          fontSize: '14px',
          fontFamily: '"Kalam", "Comic Sans MS", cursive',
          background: '#3B82F6',
          color: 'white',
          border: 'none',
          borderRadius: '8px',
          cursor: 'pointer',
        }}
      >
        Try Again
      </button>
    </div>
  );
};

// ============================================
// EMPTY STATE
// ============================================

const EmptyState = () => {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      height: '100%',
      gap: '16px',
    }}>
      <div style={{ fontSize: '48px' }}>📓</div>
      <div style={{
        fontFamily: '"Kalam", "Comic Sans MS", cursive',
        fontSize: '16px',
        color: '#999',
      }}>
        Ask a question to see magic happen!
      </div>
    </div>
  );
};

// ============================================
// METADATA BADGE
// ============================================

const MetadataBadge = ({ blueprint }) => {
  return (
    <div
      style={{
        position: 'absolute',
        top: '12px',
        right: '12px',
        background: 'rgba(255,255,255,0.9)',
        padding: '6px 12px',
        borderRadius: '12px',
        fontSize: '11px',
        fontWeight: 600,
        color: '#666',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        display: 'flex',
        alignItems: 'center',
        gap: '6px',
      }}
    >
      {blueprint.mode && <span>{getModeIcon(blueprint.mode)}</span>}
      <span>{blueprint.mode || 'SCENE'}</span>
      {blueprint.metaphor && <span>• 🇮🇳 {blueprint.metaphor}</span>}
    </div>
  );
};

// Helper: Get mode icon
const getModeIcon = (mode) => {
  const icons = {
    SCENE: '🎬',
    COMPARISON: '⚖️',
    PROCESS: '🔄',
    CYCLE: '♻️',
    STRUCTURE: '🏗️',
    GRAPH: '📊',
    TIMELINE: '⏰',
    HIERARCHY: '🌳',
  };
  return icons[mode] || '✨';
};

export default MagicNotebookEngine;

