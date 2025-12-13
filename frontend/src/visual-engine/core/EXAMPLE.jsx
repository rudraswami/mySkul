/**
 * 📚 EXAMPLE USAGE - UniversalSketchRenderer
 * ===========================================
 * 
 * Complete examples showing how to use the new renderer
 */

import React from 'react';
import UniversalSketchRenderer from './UniversalSketchRenderer';
import { EngineProvider } from './EngineContext';

// ============================================
// EXAMPLE 1: Simple Force Diagram
// ============================================

export const Example1_SimpleForce = () => {
  const blueprint = {
    mode: 'SCENE',
    concept: 'Force and Motion',
    subject: 'physics',
    
    items: [
      {
        id: 'block',
        type: 'rect',
        label: 'Object',
        width: 80,
        height: 50,
        position: { x: 250, y: 150 },
      },
    ],
    
    figures: [
      {
        x: 100,
        y: 150,
        pose: 'pushing',
        expression: 'happy',
      },
    ],
    
    arrows: [
      {
        from: 'figure',
        to: 'block',
        label: 'F = ma',
        style: 'energy',
      },
    ],
    
    highlights: ['block'],
    
    doodles: [
      {
        type: 'burst',
        x: 330,
        y: 130,
      },
    ],
    
    labels: [
      {
        text: 'Force & Motion',
        x: 200,
        y: 40,
        fontSize: 22,
        underline: true,
      },
    ],
  };
  
  return (
    <div style={{ padding: '20px' }}>
      <h2>Example 1: Simple Force Diagram</h2>
      <UniversalSketchRenderer
        blueprint={blueprint}
        height={300}
      />
    </div>
  );
};

// ============================================
// EXAMPLE 2: Process Flow
// ============================================

export const Example2_ProcessFlow = () => {
  const blueprint = {
    mode: 'PROCESS',
    concept: 'Photosynthesis',
    subject: 'biology',
    
    items: [
      {
        id: 'step1',
        type: 'circle',
        label: 'Sunlight',
        radius: 40,
      },
      {
        id: 'step2',
        type: 'circle',
        label: 'Chlorophyll',
        radius: 40,
      },
      {
        id: 'step3',
        type: 'circle',
        label: 'Glucose',
        radius: 40,
      },
    ],
    
    arrows: [
      { from: 'step1', to: 'step2' },
      { from: 'step2', to: 'step3' },
    ],
    
    labels: [
      {
        text: 'Photosynthesis Process',
        x: 200,
        y: 40,
        fontSize: 20,
        typewriter: true,
      },
    ],
  };
  
  return (
    <div style={{ padding: '20px' }}>
      <h2>Example 2: Process Flow</h2>
      <UniversalSketchRenderer
        blueprint={blueprint}
        height={300}
        useTypewriter={true}
      />
    </div>
  );
};

// ============================================
// EXAMPLE 3: With Engine Context
// ============================================

export const Example3_WithContext = () => {
  const blueprint = {
    mode: 'SCENE',
    
    items: [
      {
        id: 'ball',
        type: 'circle',
        label: 'Ball',
        radius: 30,
        position: { x: 200, y: 150 },
      },
    ],
    
    arrows: [
      {
        from: 'ball',
        to: 'ground',
        label: 'g = 9.8 m/s²',
      },
    ],
    
    labels: [
      {
        text: 'Gravity Demo',
        x: 200,
        y: 40,
        fontSize: 22,
      },
    ],
  };
  
  return (
    <div style={{ padding: '20px' }}>
      <h2>Example 3: With Engine Context</h2>
      <EngineProvider initialBlueprint={blueprint}>
        <UniversalSketchRenderer
          blueprint={blueprint}
          height={300}
          onRenderComplete={(data) => {
            console.log('Render complete:', data);
          }}
        />
      </EngineProvider>
    </div>
  );
};

// ============================================
// EXAMPLE 4: Auto-Layout (No Positions)
// ============================================

export const Example4_AutoLayout = () => {
  const blueprint = {
    mode: 'COMPARISON',
    
    // Items without explicit positions - will be auto-laid out
    items: [
      {
        id: 'a',
        type: 'rect',
        label: 'Option A',
        width: 80,
        height: 60,
        fill: '#93C5FD',
      },
      {
        id: 'b',
        type: 'rect',
        label: 'Option B',
        width: 80,
        height: 60,
        fill: '#FDBA74',
      },
    ],
    
    labels: [
      {
        text: 'Comparison',
        x: 200,
        y: 40,
        fontSize: 20,
      },
    ],
  };
  
  return (
    <div style={{ padding: '20px' }}>
      <h2>Example 4: Auto-Layout</h2>
      <p>Items without positions are automatically laid out horizontally</p>
      <UniversalSketchRenderer
        blueprint={blueprint}
        height={300}
      />
    </div>
  );
};

// ============================================
// EXAMPLE 5: Custom Path
// ============================================

export const Example5_CustomPath = () => {
  const blueprint = {
    mode: 'GRAPH',
    
    items: [
      {
        id: 'curve',
        type: 'path',
        d: 'M 50 250 Q 100 50 200 150 T 350 250',
        stroke: '#3B82F6',
      },
    ],
    
    labels: [
      {
        text: 'Quadratic Curve',
        x: 200,
        y: 40,
        fontSize: 20,
      },
    ],
    
    doodles: [
      {
        type: 'star',
        x: 200,
        y: 150,
        size: 20,
      },
    ],
  };
  
  return (
    <div style={{ padding: '20px' }}>
      <h2>Example 5: Custom Path</h2>
      <UniversalSketchRenderer
        blueprint={blueprint}
        height={300}
      />
    </div>
  );
};

// ============================================
// ALL EXAMPLES COMPONENT
// ============================================

export const AllExamples = () => {
  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '40px 20px' }}>
      <h1 style={{ fontFamily: "'Patrick Hand', cursive" }}>
        🎨 UniversalSketchRenderer Examples
      </h1>
      <p>Complete examples showing the new Magic Notebook Engine V6 renderer</p>
      
      <hr style={{ margin: '40px 0' }} />
      
      <Example1_SimpleForce />
      <hr style={{ margin: '40px 0' }} />
      
      <Example2_ProcessFlow />
      <hr style={{ margin: '40px 0' }} />
      
      <Example3_WithContext />
      <hr style={{ margin: '40px 0' }} />
      
      <Example4_AutoLayout />
      <hr style={{ margin: '40px 0' }} />
      
      <Example5_CustomPath />
    </div>
  );
};

export default AllExamples;

