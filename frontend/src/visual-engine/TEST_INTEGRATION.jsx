/**
 * 🧪 INTEGRATION TEST SUITE
 * ==========================
 * 
 * Live testing interface for Magic Notebook Engine V6
 * Tests all critical integrations
 */

import React, { useState } from 'react';
import MagicNotebookEngine from './MagicNotebookEngine';
import { SketchSliderWithValidation } from './controls/SketchSliderWithValidation';
import { PhysicsValidator, ChemistryValidator, MathValidator } from './validators';
import { NOTEBOOK_THEME } from './sketch/SketchPrimitives';

// ============================================
// TEST 1: VALIDATOR INTEGRATION
// ============================================

export const Test1_ValidatorIntegration = () => {
  const [friction, setFriction] = useState(0.5);
  const [mass, setMass] = useState(10);
  const [testResults, setTestResults] = useState([]);
  
  const addTestResult = (test, passed, message) => {
    setTestResults(prev => [...prev, { test, passed, message, timestamp: Date.now() }]);
  };
  
  return (
    <div style={{ padding: '40px', maxWidth: '800px', margin: '0 auto' }}>
      <h1 style={{ fontFamily: NOTEBOOK_THEME.handwriting }}>
        🧪 Test 1: Validator Integration
      </h1>
      
      <div style={{ marginTop: '30px', padding: '20px', background: '#F3F4F6', borderRadius: '12px' }}>
        <h3>Instructions:</h3>
        <ol>
          <li>Drag friction slider below 0 or above 1 → Should see shake + error</li>
          <li>Drag mass slider to 0 or negative → Should see shake + error</li>
          <li>Valid ranges: Friction (0-1), Mass (&gt;0)</li>
        </ol>
      </div>
      
      {/* Friction Slider */}
      <div style={{ marginTop: '40px' }}>
        <h3>Friction Coefficient (Valid: 0-1)</h3>
        <SketchSliderWithValidation
          value={friction}
          onChange={(val) => {
            setFriction(val);
            addTestResult('Friction', val >= 0 && val <= 1, `Value: ${val}`);
          }}
          min={-1}
          max={2}
          step={0.1}
          label="Friction"
          subject="physics"
          property="friction"
          enableValidation={true}
          width={300}
          onValidationError={(result) => {
            console.log('❌ Validation Error:', result);
          }}
        />
      </div>
      
      {/* Mass Slider */}
      <div style={{ marginTop: '40px' }}>
        <h3>Mass (Valid: &gt; 0)</h3>
        <SketchSliderWithValidation
          value={mass}
          onChange={(val) => {
            setMass(val);
            addTestResult('Mass', val > 0, `Value: ${val} kg`);
          }}
          min={-5}
          max={50}
          step={1}
          label="Mass"
          unit=" kg"
          subject="physics"
          property="mass"
          enableValidation={true}
          width={300}
        />
      </div>
      
      {/* Test Results Log */}
      <div style={{ marginTop: '40px', padding: '20px', background: '#1F2937', color: '#fff', borderRadius: '8px', fontFamily: 'monospace', fontSize: '12px' }}>
        <div style={{ marginBottom: '10px', fontWeight: 'bold' }}>📊 Test Results Log:</div>
        {testResults.slice(-10).reverse().map((result, i) => (
          <div key={i} style={{ padding: '4px 0', borderBottom: '1px solid #374151' }}>
            <span style={{ color: result.passed ? '#22C55E' : '#EF4444' }}>
              {result.passed ? '✅' : '❌'}
            </span>
            {' '}
            <span style={{ color: '#60A5FA' }}>{result.test}:</span>
            {' '}
            <span>{result.message}</span>
          </div>
        ))}
        {testResults.length === 0 && (
          <div style={{ color: '#9CA3AF' }}>No tests run yet...</div>
        )}
      </div>
    </div>
  );
};

// ============================================
// TEST 2: EIGHT MODES
// ============================================

export const Test2_EightModes = () => {
  const [selectedMode, setSelectedMode] = useState(null);
  
  const testCases = [
    {
      mode: 'SCENE',
      question: 'Explain Newton\'s second law',
      subject: 'physics',
      expected: 'Flow layout, force arrows, ball/force objects',
    },
    {
      mode: 'COMPARISON',
      question: 'Compare AC vs DC current',
      subject: 'physics',
      expected: 'Split view with center divider, VS label',
    },
    {
      mode: 'CYCLE',
      question: 'Explain water cycle',
      subject: 'biology',
      expected: 'Circular layout, curved arrows, loop indicator',
    },
    {
      mode: 'PROCESS',
      question: 'Explain photosynthesis process',
      subject: 'biology',
      expected: 'Step numbers, flow arrows, sequential',
    },
    {
      mode: 'STRUCTURE',
      question: 'Show heart structure',
      subject: 'biology',
      expected: 'Callout labels, leader lines, anatomical',
    },
    {
      mode: 'GRAPH',
      question: 'Plot y = x²',
      subject: 'math',
      expected: 'X/Y axes, grid, function curve',
    },
    {
      mode: 'TIMELINE',
      question: 'Timeline of evolution',
      subject: 'biology',
      expected: 'Horizontal line, event markers, dates',
    },
    {
      mode: 'HIERARCHY',
      question: 'Show animal classification',
      subject: 'biology',
      expected: 'Tree structure, parent-child connections',
    },
  ];
  
  return (
    <div style={{ padding: '40px' }}>
      <h1 style={{ fontFamily: NOTEBOOK_THEME.handwriting }}>
        🧪 Test 2: Eight Modes
      </h1>
      
      <div style={{ marginTop: '20px', display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px' }}>
        {testCases.map((test, i) => (
          <button
            key={i}
            onClick={() => setSelectedMode(test)}
            style={{
              padding: '12px',
              background: selectedMode?.mode === test.mode ? '#3B82F6' : '#F3F4F6',
              color: selectedMode?.mode === test.mode ? '#fff' : '#333',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontFamily: NOTEBOOK_THEME.handwriting,
              fontSize: '14px',
            }}
          >
            {test.mode}
          </button>
        ))}
      </div>
      
      {selectedMode && (
        <div style={{ marginTop: '30px' }}>
          <div style={{ padding: '20px', background: '#FEF3C7', borderRadius: '8px', marginBottom: '20px' }}>
            <h3>Testing: {selectedMode.mode}</h3>
            <p><strong>Question:</strong> {selectedMode.question}</p>
            <p><strong>Expected:</strong> {selectedMode.expected}</p>
          </div>
          
          <div style={{ border: '3px solid #3B82F6', borderRadius: '12px', padding: '10px', background: '#fff' }}>
            <MagicNotebookEngine
              question={selectedMode.question}
              context={{
                subject: selectedMode.subject,
                level: 'high_school',
              }}
              showControls={true}
              showNarrative={true}
              height={500}
              width={700}
              options={{
                showMetadata: true,
              }}
            />
          </div>
          
          <div style={{ marginTop: '20px', padding: '15px', background: '#1F2937', color: '#fff', borderRadius: '8px', fontFamily: 'monospace', fontSize: '12px' }}>
            <div style={{ color: '#60A5FA', marginBottom: '8px' }}>Console Logs (check browser console):</div>
            <div>✨ Magic Notebook blueprint generated</div>
            <div>📐 Mode detected: {selectedMode.mode}</div>
            <div>🎬 Narrative: 5 beats playing</div>
            <div>✋ Drawing hand: Active</div>
          </div>
        </div>
      )}
    </div>
  );
};

// ============================================
// TEST 3: METAPHOR ENGINE
// ============================================

export const Test3_MetaphorEngine = () => {
  const [selectedMetaphor, setSelectedMetaphor] = useState(null);
  
  const metaphorTests = [
    {
      metaphor: 'cricket',
      emoji: '🏏',
      question: 'Explain momentum using cricket',
      expected: 'Cricket ball, bat, bowler, green field background',
    },
    {
      metaphor: 'auto_rickshaw',
      emoji: '🛺',
      question: 'Explain friction using auto-rickshaw',
      expected: 'Auto SVG, road background, driver',
    },
    {
      metaphor: 'chai',
      emoji: '☕',
      question: 'Explain heat transfer with chai',
      expected: 'Chai cup, steam, temperature labels',
    },
    {
      metaphor: 'diwali',
      emoji: '🪔',
      question: 'Explain light energy using Diwali',
      expected: 'Diya lamp, golden background, festive',
    },
  ];
  
  return (
    <div style={{ padding: '40px' }}>
      <h1 style={{ fontFamily: NOTEBOOK_THEME.handwriting }}>
        🧪 Test 3: Metaphor Engine (India-First 🇮🇳)
      </h1>
      
      <div style={{ marginTop: '20px', display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
        {metaphorTests.map((test, i) => (
          <button
            key={i}
            onClick={() => setSelectedMetaphor(test)}
            style={{
              padding: '12px 20px',
              background: selectedMetaphor?.metaphor === test.metaphor ? '#F59E0B' : '#FEF3C7',
              color: '#92400E',
              border: 'none',
              borderRadius: '12px',
              cursor: 'pointer',
              fontFamily: NOTEBOOK_THEME.handwriting,
              fontSize: '16px',
            }}
          >
            {test.emoji} {test.metaphor}
          </button>
        ))}
      </div>
      
      {selectedMetaphor && (
        <div style={{ marginTop: '30px' }}>
          <div style={{ padding: '20px', background: '#FFFBEB', borderRadius: '8px', marginBottom: '20px' }}>
            <h3>Testing: {selectedMetaphor.emoji} {selectedMetaphor.metaphor}</h3>
            <p><strong>Question:</strong> {selectedMetaphor.question}</p>
            <p><strong>Expected:</strong> {selectedMetaphor.expected}</p>
          </div>
          
          <div style={{ border: '3px solid #F59E0B', borderRadius: '12px', padding: '10px', background: '#fff' }}>
            <MagicNotebookEngine
              question={selectedMetaphor.question}
              context={{
                subject: 'physics',
                level: 'high_school',
              }}
              showControls={true}
              showNarrative={true}
              height={500}
              width={700}
            />
          </div>
          
          <div style={{ marginTop: '20px', padding: '15px', background: '#78350F', color: '#fff', borderRadius: '8px', fontFamily: 'monospace', fontSize: '12px' }}>
            <div style={{ color: '#FCD34D', marginBottom: '8px' }}>Check for:</div>
            <div>✅ Metaphor detected: {selectedMetaphor.metaphor}</div>
            <div>✅ Cultural SVG assets loaded</div>
            <div>✅ Background theme applied</div>
            <div>✅ Indian context in narrative</div>
          </div>
        </div>
      )}
    </div>
  );
};

// ============================================
// TEST 4: NARRATIVE + HAND SYNCHRONIZATION
// ============================================

export const Test4_NarrativeSync = () => {
  const [playState, setPlayState] = useState('idle');
  const [currentBeat, setCurrentBeat] = useState(0);
  const [handVisible, setHandVisible] = useState(false);
  
  return (
    <div style={{ padding: '40px' }}>
      <h1 style={{ fontFamily: NOTEBOOK_THEME.handwriting }}>
        🧪 Test 4: Narrative + Hand Synchronization
      </h1>
      
      <div style={{ marginTop: '20px', padding: '20px', background: '#DBEAFE', borderRadius: '8px' }}>
        <h3>What to Check:</h3>
        <ul>
          <li>✅ Hand appears when drawing starts (Beat 2)</li>
          <li>✅ Hand follows stroke paths smoothly</li>
          <li>✅ Hand rotates with drawing direction</li>
          <li>✅ Hand switches poses (idle → drawing → pointing)</li>
          <li>✅ Text bubbles appear with typewriter effect</li>
          <li>✅ Beats play in sequence (1 → 2 → 3 → 4 → 5)</li>
          <li>✅ Pause works on Beat 4</li>
        </ul>
      </div>
      
      <div style={{ marginTop: '30px', border: '3px solid #3B82F6', borderRadius: '12px', padding: '10px', background: '#fff' }}>
        <MagicNotebookEngine
          question="Explain circular motion"
          context={{
            subject: 'physics',
            level: 'high_school',
          }}
          showControls={true}
          showNarrative={true}
          height={500}
          width={700}
          onBlueprintGenerated={(blueprint) => {
            console.log('✨ Blueprint generated:', blueprint);
          }}
          onNarrativeComplete={() => {
            console.log('🎬 Narrative complete!');
            setPlayState('complete');
          }}
        />
      </div>
      
      {/* Real-time status */}
      <div style={{ marginTop: '20px', padding: '15px', background: '#1F2937', color: '#fff', borderRadius: '8px' }}>
        <div style={{ fontFamily: 'monospace', fontSize: '12px' }}>
          <div>State: {playState}</div>
          <div>Current Beat: {currentBeat} / 5</div>
          <div>Hand Visible: {handVisible ? 'Yes ✅' : 'No'}</div>
          <div style={{ marginTop: '10px', color: '#9CA3AF' }}>
            (Check browser console for detailed logs)
          </div>
        </div>
      </div>
    </div>
  );
};

// ============================================
// TEST 5: FULL PIPELINE
// ============================================

export const Test5_FullPipeline = () => {
  const [question, setQuestion] = useState('');
  const [subject, setSubject] = useState('physics');
  const [submitted, setSubmitted] = useState(false);
  const [pipelineSteps, setPipelineSteps] = useState([]);
  
  const addStep = (step, status, data) => {
    setPipelineSteps(prev => [...prev, { step, status, data, timestamp: Date.now() }]);
  };
  
  const handleSubmit = (e) => {
    e.preventDefault();
    if (question.trim()) {
      setPipelineSteps([]);
      addStep('Question Received', 'pending', question);
      setSubmitted(true);
    }
  };
  
  return (
    <div style={{ padding: '40px' }}>
      <h1 style={{ fontFamily: NOTEBOOK_THEME.handwriting }}>
        🧪 Test 5: Full Pipeline (End-to-End)
      </h1>
      
      <div style={{ marginTop: '20px', padding: '20px', background: '#F0FDF4', borderRadius: '8px' }}>
        <h3>Pipeline Flow:</h3>
        <div style={{ fontFamily: 'monospace', fontSize: '12px', marginTop: '10px' }}>
          Question → ConceptBreaker → GPT-4o-mini → Blueprint → SceneComposer → 
          MetaphorMapper → ModeRouter → Renderer → Narrative → Drawing Hand
        </div>
      </div>
      
      {!submitted ? (
        <form onSubmit={handleSubmit} style={{ marginTop: '30px' }}>
          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
              Ask a Question:
            </label>
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="e.g., Explain centripetal force using cricket"
              style={{
                width: '100%',
                padding: '12px',
                fontSize: '16px',
                borderRadius: '8px',
                border: '2px solid #ddd',
                fontFamily: NOTEBOOK_THEME.handwriting,
              }}
            />
          </div>
          
          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
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
              fontFamily: NOTEBOOK_THEME.handwriting,
              background: '#10B981',
              color: 'white',
              border: 'none',
              borderRadius: '12px',
              cursor: question.trim() ? 'pointer' : 'not-allowed',
            }}
          >
            ✨ Test Full Pipeline
          </button>
        </form>
      ) : (
        <div style={{ marginTop: '30px' }}>
          <button
            onClick={() => { setSubmitted(false); setQuestion(''); }}
            style={{
              padding: '8px 16px',
              marginBottom: '20px',
              background: '#6B7280',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
            }}
          >
            ← Test Another
          </button>
          
          <div style={{ border: '3px solid #10B981', borderRadius: '12px', padding: '10px', background: '#fff' }}>
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
                addStep('ConceptBreaker', 'success', `Mode: ${blueprint.mode}, Metaphor: ${blueprint.metaphor}`);
                addStep('SceneComposer', 'success', `Items: ${blueprint.items?.length}`);
                addStep('MetaphorMapper', 'success', `Applied: ${blueprint.metaphor || 'none'}`);
              }}
              onNarrativeComplete={() => {
                addStep('Narrative', 'complete', '5 beats played');
              }}
              onError={(error) => {
                addStep('Error', 'failed', error.message);
              }}
            />
          </div>
          
          {/* Pipeline Status */}
          <div style={{ marginTop: '20px', padding: '20px', background: '#1F2937', color: '#fff', borderRadius: '8px' }}>
            <h3 style={{ color: '#10B981', marginBottom: '15px' }}>Pipeline Status:</h3>
            {pipelineSteps.map((step, i) => (
              <div key={i} style={{ 
                padding: '8px 12px', 
                marginBottom: '8px',
                background: '#374151',
                borderRadius: '6px',
                fontFamily: 'monospace',
                fontSize: '12px',
                borderLeft: `4px solid ${
                  step.status === 'success' ? '#10B981' : 
                  step.status === 'failed' ? '#EF4444' : 
                  step.status === 'complete' ? '#3B82F6' : 
                  '#F59E0B'
                }`
              }}>
                <div style={{ color: '#60A5FA' }}>{step.step}</div>
                <div style={{ color: '#D1D5DB', fontSize: '11px' }}>{step.data}</div>
              </div>
            ))}
            {pipelineSteps.length === 0 && (
              <div style={{ color: '#9CA3AF' }}>Waiting for pipeline execution...</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

// ============================================
// MASTER TEST SUITE
// ============================================

export const MasterTestSuite = () => {
  const [activeTest, setActiveTest] = useState(0);
  
  const tests = [
    { label: 'Validator Integration', component: <Test1_ValidatorIntegration /> },
    { label: 'Eight Modes', component: <Test2_EightModes /> },
    { label: 'Metaphor Engine', component: <Test3_MetaphorEngine /> },
    { label: 'Narrative + Hand Sync', component: <Test4_NarrativeSync /> },
    { label: 'Full Pipeline', component: <Test5_FullPipeline /> },
  ];
  
  return (
    <div>
      <div style={{
        display: 'flex',
        gap: '12px',
        padding: '20px',
        background: '#F9FAFB',
        borderBottom: '3px solid #E5E7EB',
        overflowX: 'auto',
      }}>
        {tests.map((test, i) => (
          <button
            key={i}
            onClick={() => setActiveTest(i)}
            style={{
              padding: '10px 20px',
              fontSize: '14px',
              fontWeight: activeTest === i ? 'bold' : 'normal',
              background: activeTest === i ? '#3B82F6' : 'white',
              color: activeTest === i ? 'white' : '#666',
              border: activeTest === i ? 'none' : '2px solid #E5E7EB',
              borderRadius: '8px',
              cursor: 'pointer',
              whiteSpace: 'nowrap',
            }}
          >
            {test.label}
          </button>
        ))}
      </div>
      
      <div>{tests[activeTest].component}</div>
    </div>
  );
};

export default MasterTestSuite;











































