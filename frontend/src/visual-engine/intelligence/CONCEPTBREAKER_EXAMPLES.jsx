/**
 * 📚 CONCEPT BREAKER EXAMPLES
 * ============================
 * 
 * Shows how ConceptBreaker turns questions into visual blueprints
 */

import React from 'react';
import { useBreakConcept, useBreakConceptMutation } from '../../hooks/useConceptBreaker';
import { ConceptBreaker, createConceptBreaker } from './ConceptBreaker';
import { composeScene } from './SceneComposer';
import UniversalSketchRenderer from '../core/UniversalSketchRenderer';
import { NarrativePlayer } from '../narrative';
import { NOTEBOOK_THEME } from '../sketch/SketchPrimitives';

// ============================================
// EXAMPLE 1: Using React Query Hook
// ============================================

export const Example1_ReactQueryHook = () => {
  const question = "Explain Newton's second law with force and acceleration";
  const context = {
    subject: 'physics',
    level: 'high_school',
  };
  
  const { data: blueprint, isLoading, error } = useBreakConcept(question, context);
  
  if (isLoading) return <div>🧠 Breaking down concept...</div>;
  if (error) return <div>❌ Error: {error.message}</div>;
  if (!blueprint) return <div>No blueprint generated</div>;
  
  // Compose scene from blueprint
  const positionedBlueprint = composeScene(blueprint);
  
  return (
    <div style={{ padding: '20px' }}>
      <h2 style={{ fontFamily: NOTEBOOK_THEME.handwriting }}>
        Example 1: React Query Hook
      </h2>
      
      <div style={{
        padding: '12px',
        background: NOTEBOOK_THEME.highlightBlue,
        borderRadius: '8px',
        marginBottom: '16px',
      }}>
        <strong>Question:</strong> {question}
      </div>
      
      <div style={{
        padding: '12px',
        background: '#f0f0f0',
        borderRadius: '8px',
        marginBottom: '16px',
        fontFamily: 'monospace',
        fontSize: '12px',
      }}>
        <strong>Blueprint:</strong>
        <pre>{JSON.stringify(blueprint, null, 2)}</pre>
      </div>
      
      <div style={{
        position: 'relative',
        height: '400px',
        background: NOTEBOOK_THEME.paperBg,
        borderRadius: '12px',
        overflow: 'hidden',
      }}>
        <UniversalSketchRenderer
          blueprint={positionedBlueprint}
          height={400}
        />
        
        <NarrativePlayer
          blueprint={positionedBlueprint}
          showControls={true}
        />
      </div>
    </div>
  );
};

// ============================================
// EXAMPLE 2: Using Mutation Hook (Imperative)
// ============================================

export const Example2_MutationHook = () => {
  const { mutate, data: blueprint, isLoading } = useBreakConceptMutation();
  const [question, setQuestion] = React.useState('');
  
  const handleSubmit = (e) => {
    e.preventDefault();
    mutate({
      question,
      context: {
        subject: 'chemistry',
        level: 'high_school',
      },
    });
  };
  
  const positionedBlueprint = blueprint ? composeScene(blueprint) : null;
  
  return (
    <div style={{ padding: '20px' }}>
      <h2 style={{ fontFamily: NOTEBOOK_THEME.handwriting }}>
        Example 2: Interactive Question Breaking
      </h2>
      
      <form onSubmit={handleSubmit} style={{ marginBottom: '20px' }}>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a chemistry question..."
          style={{
            width: '100%',
            padding: '12px',
            fontSize: '16px',
            borderRadius: '8px',
            border: '2px solid #ddd',
            fontFamily: NOTEBOOK_THEME.handwriting,
          }}
        />
        <button
          type="submit"
          disabled={!question || isLoading}
          style={{
            marginTop: '8px',
            padding: '12px 24px',
            fontSize: '16px',
            borderRadius: '8px',
            border: 'none',
            background: '#3B82F6',
            color: 'white',
            cursor: 'pointer',
            fontFamily: NOTEBOOK_THEME.handwriting,
          }}
        >
          {isLoading ? '🧠 Breaking...' : '✨ Break Concept'}
        </button>
      </form>
      
      {positionedBlueprint && (
        <div style={{
          position: 'relative',
          height: '400px',
          background: NOTEBOOK_THEME.paperBg,
          borderRadius: '12px',
          overflow: 'hidden',
        }}>
          <UniversalSketchRenderer
            blueprint={positionedBlueprint}
            height={400}
          />
          
          <NarrativePlayer
            blueprint={positionedBlueprint}
            showControls={true}
          />
        </div>
      )}
    </div>
  );
};

// ============================================
// EXAMPLE 3: Direct Class Usage (No React Query)
// ============================================

export const Example3_DirectClass = () => {
  const [blueprint, setBlueprint] = React.useState(null);
  const [isLoading, setIsLoading] = React.useState(false);
  
  React.useEffect(() => {
    const breakConcept = async () => {
      setIsLoading(true);
      
      // Create ConceptBreaker instance
      const breaker = createConceptBreaker({
        useLLM: false, // Use rule-based fallback only (for demo)
        useFallback: true,
      });
      
      // Break concept
      const result = await breaker.break(
        'Explain photosynthesis with sunlight and plants',
        {
          subject: 'biology',
          level: 'middle_school',
        }
      );
      
      setBlueprint(result);
      setIsLoading(false);
    };
    
    breakConcept();
  }, []);
  
  if (isLoading) return <div>🧠 Breaking concept...</div>;
  if (!blueprint) return <div>No blueprint</div>;
  
  const positionedBlueprint = composeScene(blueprint);
  
  return (
    <div style={{ padding: '20px' }}>
      <h2 style={{ fontFamily: NOTEBOOK_THEME.handwriting }}>
        Example 3: Direct Class Usage (Rule-Based Fallback)
      </h2>
      
      <div style={{
        padding: '12px',
        background: NOTEBOOK_THEME.highlightYellow,
        borderRadius: '8px',
        marginBottom: '16px',
      }}>
        <strong>Mode:</strong> {blueprint.method === 'rules' ? '📜 Rule-Based' : '🤖 LLM'}
        <br />
        <strong>Confidence:</strong> {(blueprint.confidence * 100).toFixed(0)}%
        <br />
        <strong>Mode Detected:</strong> {blueprint.mode}
      </div>
      
      <div style={{
        position: 'relative',
        height: '400px',
        background: NOTEBOOK_THEME.paperBg,
        borderRadius: '12px',
        overflow: 'hidden',
      }}>
        <UniversalSketchRenderer
          blueprint={positionedBlueprint}
          height={400}
        />
        
        <NarrativePlayer
          blueprint={positionedBlueprint}
          showControls={true}
        />
      </div>
    </div>
  );
};

// ============================================
// EXAMPLE 4: Cricket Metaphor Detection
// ============================================

export const Example4_MetaphorDetection = () => {
  const [blueprint, setBlueprint] = React.useState(null);
  
  React.useEffect(() => {
    const breakConcept = async () => {
      const breaker = createConceptBreaker({ useLLM: false, useFallback: true });
      
      const result = await breaker.break(
        'Explain centripetal force using a cricket ball',
        {
          subject: 'physics',
          level: 'high_school',
        }
      );
      
      setBlueprint(result);
    };
    
    breakConcept();
  }, []);
  
  if (!blueprint) return <div>Loading...</div>;
  
  const positionedBlueprint = composeScene(blueprint);
  
  return (
    <div style={{ padding: '20px' }}>
      <h2 style={{ fontFamily: NOTEBOOK_THEME.handwriting }}>
        Example 4: Indian Metaphor Detection 🏏
      </h2>
      
      <div style={{
        padding: '12px',
        background: '#FFF4E6',
        borderRadius: '8px',
        marginBottom: '16px',
      }}>
        <strong>Metaphor Detected:</strong> {blueprint.metaphor || 'None'} 
        {blueprint.metaphor === 'cricket' && ' 🏏'}
      </div>
      
      <div style={{
        position: 'relative',
        height: '400px',
        background: NOTEBOOK_THEME.paperBg,
        borderRadius: '12px',
        overflow: 'hidden',
      }}>
        <UniversalSketchRenderer
          blueprint={positionedBlueprint}
          height={400}
        />
        
        <NarrativePlayer
          blueprint={positionedBlueprint}
          showControls={true}
        />
      </div>
    </div>
  );
};

// ============================================
// ALL EXAMPLES
// ============================================

export const AllConceptBreakerExamples = () => {
  return (
    <div style={{ maxWidth: '900px', margin: '0 auto', padding: '40px 20px' }}>
      <h1 style={{ fontFamily: NOTEBOOK_THEME.handwriting }}>
        🧠 ConceptBreaker Examples
      </h1>
      <p>Turning questions into visual blueprints!</p>
      
      <hr style={{ margin: '40px 0' }} />
      
      <Example1_ReactQueryHook />
      <hr style={{ margin: '40px 0' }} />
      
      <Example2_MutationHook />
      <hr style={{ margin: '40px 0' }} />
      
      <Example3_DirectClass />
      <hr style={{ margin: '40px 0' }} />
      
      <Example4_MetaphorDetection />
    </div>
  );
};

export default AllConceptBreakerExamples;

