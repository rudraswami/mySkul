/**
 * 📚 COMPLETE MAGIC NOTEBOOK ENGINE EXAMPLE
 * ===========================================
 * 
 * Demonstrates the full pipeline:
 * Question → ConceptBreaker → SceneComposer → Metaphors → Renderer → Narrative
 */

import React, { useState } from 'react';
import MagicNotebookEngine from './MagicNotebookEngine';

// ============================================
// EXAMPLE 1: Simple Question
// ============================================

export const Example1_SimpleQuestion = () => {
  return (
    <div style={{ padding: '40px', maxWidth: '900px', margin: '0 auto' }}>
      <h1 style={{ fontFamily: '"Kalam", cursive' }}>
        ✨ Magic Notebook Engine - Complete Example
      </h1>
      
      <p>Ask a question and watch the magic happen!</p>
      
      <div style={{ marginTop: '40px' }}>
        <MagicNotebookEngine
          question="Explain Newton's second law using cricket"
          context={{
            subject: 'physics',
            level: 'high_school',
          }}
          showControls={true}
          showNarrative={true}
          height={500}
          width={600}
        />
      </div>
      
      <div style={{ marginTop: '20px', padding: '20px', background: '#F3F4F6', borderRadius: '8px' }}>
        <h3>What just happened?</h3>
        <ol>
          <li><strong>ConceptBreaker</strong> detected mode: SCENE, metaphor: cricket</li>
          <li><strong>SceneComposer</strong> positioned elements using flow layout</li>
          <li><strong>MetaphorMapper</strong> substituted ball → cricket ball 🏏</li>
          <li><strong>UniversalRenderer</strong> drew with RoughJS + Framer Motion</li>
          <li><strong>DrawingHand</strong> animated along paths</li>
          <li><strong>NarrativeEngine</strong> orchestrated 5-beat teaching</li>
        </ol>
      </div>
    </div>
  );
};

// ============================================
// EXAMPLE 2: Interactive Demo
// ============================================

export const Example2_InteractiveDemo = () => {
  const [question, setQuestion] = useState('');
  const [subject, setSubject] = useState('physics');
  const [submitted, setSubmitted] = useState(false);
  
  const handleSubmit = (e) => {
    e.preventDefault();
    if (question.trim()) {
      setSubmitted(true);
    }
  };
  
  const reset = () => {
    setQuestion('');
    setSubmitted(false);
  };
  
  return (
    <div style={{ padding: '40px', maxWidth: '900px', margin: '0 auto' }}>
      <h1 style={{ fontFamily: '"Kalam", cursive' }}>
        🧠 Ask Me Anything!
      </h1>
      
      {!submitted ? (
        <form onSubmit={handleSubmit} style={{ marginTop: '40px' }}>
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 600 }}>
              Your Question:
            </label>
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="e.g., Explain photosynthesis with a dosa"
              style={{
                width: '100%',
                padding: '12px',
                fontSize: '16px',
                borderRadius: '8px',
                border: '2px solid #ddd',
                fontFamily: '"Kalam", cursive',
              }}
            />
          </div>
          
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 600 }}>
              Subject:
            </label>
            <select
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              style={{
                padding: '12px',
                fontSize: '16px',
                borderRadius: '8px',
                border: '2px solid #ddd',
              }}
            >
              <option value="physics">Physics</option>
              <option value="chemistry">Chemistry</option>
              <option value="biology">Biology</option>
              <option value="math">Mathematics</option>
            </select>
          </div>
          
          <button
            type="submit"
            disabled={!question.trim()}
            style={{
              padding: '12px 32px',
              fontSize: '18px',
              fontFamily: '"Kalam", cursive',
              background: '#3B82F6',
              color: 'white',
              border: 'none',
              borderRadius: '12px',
              cursor: question.trim() ? 'pointer' : 'not-allowed',
              opacity: question.trim() ? 1 : 0.5,
            }}
          >
            ✨ Create Visual
          </button>
        </form>
      ) : (
        <div style={{ marginTop: '40px' }}>
          <button
            onClick={reset}
            style={{
              padding: '8px 16px',
              fontSize: '14px',
              marginBottom: '20px',
              background: '#6B7280',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
            }}
          >
            ← Ask Another Question
          </button>
          
          <MagicNotebookEngine
            question={question}
            context={{
              subject,
              level: 'high_school',
            }}
            showControls={true}
            showNarrative={true}
            height={500}
            width={700}
            onBlueprintGenerated={(blueprint) => {
              console.log('Blueprint generated:', blueprint);
            }}
            onNarrativeComplete={() => {
              console.log('Narrative complete!');
            }}
          />
        </div>
      )}
    </div>
  );
};

// ============================================
// EXAMPLE 3: Multiple Modes
// ============================================

export const Example3_AllModes = () => {
  const examples = [
    {
      mode: 'SCENE',
      question: 'Explain force and motion',
      subject: 'physics',
    },
    {
      mode: 'COMPARISON',
      question: 'Compare AC vs DC current',
      subject: 'physics',
    },
    {
      mode: 'CYCLE',
      question: 'Explain water cycle',
      subject: 'biology',
    },
    {
      mode: 'GRAPH',
      question: 'Plot y = x²',
      subject: 'math',
    },
  ];
  
  return (
    <div style={{ padding: '40px', maxWidth: '1200px', margin: '0 auto' }}>
      <h1 style={{ fontFamily: '"Kalam", cursive' }}>
        🎨 All 8 Modes in Action
      </h1>
      
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))',
        gap: '32px',
        marginTop: '40px',
      }}>
        {examples.map((example, i) => (
          <div
            key={i}
            style={{
              border: '2px solid #E5E7EB',
              borderRadius: '12px',
              padding: '20px',
              background: '#fff',
            }}
          >
            <h3 style={{ marginBottom: '16px' }}>
              {getModeIcon(example.mode)} {example.mode}
            </h3>
            <p style={{ fontSize: '14px', color: '#666', marginBottom: '16px' }}>
              "{example.question}"
            </p>
            <MagicNotebookEngine
              question={example.question}
              context={{
                subject: example.subject,
                level: 'high_school',
              }}
              showControls={false}
              showNarrative={false}
              height={300}
              width={350}
              options={{ showMetadata: true }}
            />
          </div>
        ))}
      </div>
    </div>
  );
};

// Helper
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

// ============================================
// ALL EXAMPLES
// ============================================

export const AllExamples = () => {
  const [activeTab, setActiveTab] = useState(0);
  
  const tabs = [
    { label: 'Simple Example', component: <Example1_SimpleQuestion /> },
    { label: 'Interactive Demo', component: <Example2_InteractiveDemo /> },
    { label: 'All Modes', component: <Example3_AllModes /> },
  ];
  
  return (
    <div>
      <div style={{
        display: 'flex',
        gap: '16px',
        padding: '20px 40px',
        borderBottom: '2px solid #E5E7EB',
        background: '#F9FAFB',
      }}>
        {tabs.map((tab, i) => (
          <button
            key={i}
            onClick={() => setActiveTab(i)}
            style={{
              padding: '8px 16px',
              fontSize: '16px',
              fontWeight: activeTab === i ? 'bold' : 'normal',
              background: activeTab === i ? '#3B82F6' : 'transparent',
              color: activeTab === i ? 'white' : '#666',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>
      
      <div>{tabs[activeTab].component}</div>
    </div>
  );
};

export default AllExamples;

