/**
 * 📚 NARRATIVE ENGINE EXAMPLES
 * =============================
 * 
 * Complete examples showing the 5-beat narrative system
 */

import React from 'react';
import { NarrativePlayer, useNarrativeEngine } from './NarrativeEngineReact';
import { NOTEBOOK_THEME } from '../sketch/SketchPrimitives';
import UniversalSketchRenderer from '../core/UniversalSketchRenderer';

// ============================================
// EXAMPLE 1: Simple Narrative Flow
// ============================================

export const Example1_SimpleNarrative = () => {
  const blueprint = {
    mode: 'SCENE',
    concept: 'Force and Motion',
    
    items: [
      { id: 'ball', type: 'circle', label: 'Ball', radius: 30, position: { x: 100, y: 150 } },
      { id: 'force', type: 'circle', label: 'Force', radius: 25, position: { x: 250, y: 150 } },
    ],
    
    arrows: [
      { from: 'ball', to: 'force', label: 'F = ma' },
    ],
    
    beats: [
      {
        beat: 1,
        text: "Let me show you how force works!",
        duration: 2,
      },
      {
        beat: 2,
        text: "When you apply force to an object...",
        drawItems: ['ball'],
        duration: 2,
      },
      {
        beat: 3,
        text: "...it causes acceleration!",
        drawItems: ['force'],
        duration: 2,
      },
      {
        beat: 4,
        text: "The key formula is F = ma",
        highlightItems: ['ball', 'force'],
        pause: true,
        duration: 2,
      },
      {
        beat: 5,
        text: "Now you'll never forget! 💪",
        duration: 2,
      },
    ],
  };
  
  return (
    <div style={{ padding: '20px' }}>
      <h2 style={{ fontFamily: NOTEBOOK_THEME.handwriting }}>
        Example 1: Simple Narrative Flow
      </h2>
      
      <div style={{
        position: 'relative',
        height: '400px',
        background: NOTEBOOK_THEME.paperBg,
        borderRadius: '12px',
        marginTop: '20px',
        overflow: 'hidden',
      }}>
        {/* Renderer */}
        <div style={{ position: 'absolute', inset: 0 }}>
          <UniversalSketchRenderer
            blueprint={blueprint}
            height={400}
          />
        </div>
        
        {/* Narrative Player Overlay */}
        <NarrativePlayer
          blueprint={blueprint}
          options={{
            enableHand: true,
            enableBubbles: true,
            speed: 1.0,
          }}
          showControls={true}
        />
      </div>
    </div>
  );
};

// ============================================
// EXAMPLE 2: Custom Hook Usage
// ============================================

export const Example2_CustomHook = () => {
  const blueprint = {
    mode: 'PROCESS',
    concept: 'Photosynthesis',
    
    items: [
      { id: 'sun', type: 'circle', label: '☀️ Sun', radius: 35, position: { x: 80, y: 100 } },
      { id: 'leaf', type: 'circle', label: '🌿 Leaf', radius: 35, position: { x: 200, y: 100 } },
      { id: 'sugar', type: 'circle', label: '🍬 Sugar', radius: 35, position: { x: 320, y: 100 } },
    ],
    
    arrows: [
      { from: 'sun', to: 'leaf' },
      { from: 'leaf', to: 'sugar' },
    ],
    
    beats: [
      {
        beat: 1,
        text: "Let's understand photosynthesis!",
        duration: 2,
      },
      {
        beat: 2,
        text: "Sunlight hits the leaf...",
        drawItems: ['sun', 'leaf'],
        duration: 2,
      },
      {
        beat: 3,
        text: "...and creates sugar!",
        drawItems: ['sugar'],
        duration: 2,
      },
      {
        beat: 4,
        text: "This is how plants make food!",
        highlightItems: ['sugar'],
        duration: 2,
      },
      {
        beat: 5,
        text: "Amazing, right? 🌱",
        duration: 2,
      },
    ],
  };
  
  const { state, play, pause, stop, nextBeat, previousBeat } = useNarrativeEngine(blueprint, {
    enableHand: true,
    enableBubbles: true,
  });
  
  if (!state) return <div>Loading...</div>;
  
  return (
    <div style={{ padding: '20px' }}>
      <h2 style={{ fontFamily: NOTEBOOK_THEME.handwriting }}>
        Example 2: Custom Hook Usage
      </h2>
      
      <div style={{
        marginTop: '20px',
        padding: '20px',
        background: NOTEBOOK_THEME.highlightBlue,
        borderRadius: '8px',
        fontFamily: NOTEBOOK_THEME.handwriting,
      }}>
        <h3>Narrative State:</h3>
        <ul style={{ marginTop: '10px' }}>
          <li><strong>Current Beat:</strong> {state.currentBeat} / {blueprint.beats.length}</li>
          <li><strong>Phase:</strong> {state.phase}</li>
          <li><strong>Progress:</strong> {Math.round(state.progress * 100)}%</li>
          <li><strong>Hand Pose:</strong> {state.hand.pose}</li>
          <li><strong>Bubble Visible:</strong> {state.bubble.visible ? 'Yes' : 'No'}</li>
          <li><strong>Playing:</strong> {state.isPlaying ? 'Yes' : 'No'}</li>
        </ul>
        
        <div style={{ marginTop: '16px', display: 'flex', gap: '8px' }}>
          <button onClick={previousBeat}>Previous</button>
          {state.isPlaying ? (
            <button onClick={pause}>Pause</button>
          ) : (
            <button onClick={play}>Play</button>
          )}
          <button onClick={stop}>Stop</button>
          <button onClick={nextBeat}>Next</button>
        </div>
      </div>
    </div>
  );
};

// ============================================
// EXAMPLE 3: Physics with Indian Metaphor
// ============================================

export const Example3_CricketMetaphor = () => {
  const blueprint = {
    mode: 'SCENE',
    concept: 'Centripetal Force',
    metaphor: 'cricket',
    
    items: [
      { id: 'ball', type: 'circle', label: '🏏 Cricket Ball', radius: 25, position: { x: 200, y: 150 } },
    ],
    
    figures: [
      { x: 100, y: 180, pose: 'pushing', expression: 'happy' },
    ],
    
    arrows: [
      { from: 'figure', to: 'ball', label: 'Force', style: 'energy', curved: true },
    ],
    
    beats: [
      {
        beat: 1,
        text: "Think of a cricket bowler! 🏏",
        duration: 2,
      },
      {
        beat: 2,
        text: "The bowler applies force to the ball...",
        drawItems: ['ball'],
        duration: 2,
      },
      {
        beat: 3,
        text: "...making it spin through the air!",
        highlightItems: ['ball'],
        duration: 2,
      },
      {
        beat: 4,
        text: "This spinning motion is centripetal force!",
        pause: true,
        duration: 2,
      },
      {
        beat: 5,
        text: "Now you'll remember this in every match! 🎾",
        duration: 2,
      },
    ],
  };
  
  return (
    <div style={{ padding: '20px' }}>
      <h2 style={{ fontFamily: NOTEBOOK_THEME.handwriting }}>
        Example 3: Cricket Metaphor (India-First)
      </h2>
      
      <div style={{
        position: 'relative',
        height: '400px',
        background: NOTEBOOK_THEME.paperBg,
        borderRadius: '12px',
        marginTop: '20px',
        overflow: 'hidden',
      }}>
        <div style={{ position: 'absolute', inset: 0 }}>
          <UniversalSketchRenderer
            blueprint={blueprint}
            height={400}
          />
        </div>
        
        <NarrativePlayer
          blueprint={blueprint}
          options={{
            enableHand: true,
            enableBubbles: true,
            speed: 1.0,
          }}
          showControls={true}
          onComplete={() => console.log('Narrative complete!')}
        />
      </div>
    </div>
  );
};

// ============================================
// ALL EXAMPLES
// ============================================

export const AllNarrativeExamples = () => {
  return (
    <div style={{ maxWidth: '900px', margin: '0 auto', padding: '40px 20px' }}>
      <h1 style={{ fontFamily: NOTEBOOK_THEME.handwriting }}>
        🎬 Narrative Engine Examples
      </h1>
      <p>5-beat teaching system in action!</p>
      
      <hr style={{ margin: '40px 0' }} />
      
      <Example1_SimpleNarrative />
      <hr style={{ margin: '40px 0' }} />
      
      <Example2_CustomHook />
      <hr style={{ margin: '40px 0' }} />
      
      <Example3_CricketMetaphor />
    </div>
  );
};

export default AllNarrativeExamples;

