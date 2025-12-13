/**
 * 📚 SKETCHY CONTROLS EXAMPLES
 * =============================
 * 
 * Complete examples showing all sketchy controls
 */

import React, { useState } from 'react';
import SketchSlider from './SketchSlider';
import SketchToggle from './SketchToggle';
import SketchButton from './SketchButton';
import SketchKnob from './SketchKnob';
import { NOTEBOOK_THEME } from '../sketch/SketchPrimitives';

// ============================================
// EXAMPLE 1: SketchSlider Demo
// ============================================

export const Example1_Slider = () => {
  const [force, setForce] = useState(50);
  const [mass, setMass] = useState(10);
  
  const acceleration = (force / mass).toFixed(1);
  
  return (
    <div style={{ padding: '20px', maxWidth: '400px' }}>
      <h2 style={{ fontFamily: NOTEBOOK_THEME.handwriting }}>
        Example 1: Sketch Sliders
      </h2>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', marginTop: '20px' }}>
        <SketchSlider
          label="Force"
          value={force}
          min={0}
          max={100}
          unit=" N"
          color={NOTEBOOK_THEME.markerBlue}
          onChange={setForce}
        />
        
        <SketchSlider
          label="Mass"
          value={mass}
          min={1}
          max={20}
          unit=" kg"
          color={NOTEBOOK_THEME.markerGreen}
          onChange={setMass}
        />
        
        <div
          style={{
            padding: '16px',
            background: NOTEBOOK_THEME.highlightYellow,
            borderRadius: '8px',
            fontFamily: NOTEBOOK_THEME.handwriting,
            fontSize: '18px',
            textAlign: 'center',
          }}
        >
          <strong>a = F/m = {acceleration} m/s²</strong>
        </div>
      </div>
    </div>
  );
};

// ============================================
// EXAMPLE 2: SketchToggle Demo
// ============================================

export const Example2_Toggle = () => {
  const [friction, setFriction] = useState(true);
  const [gravity, setGravity] = useState(true);
  const [airResistance, setAirResistance] = useState(false);
  
  return (
    <div style={{ padding: '20px', maxWidth: '400px' }}>
      <h2 style={{ fontFamily: NOTEBOOK_THEME.handwriting }}>
        Example 2: Sketch Toggles
      </h2>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginTop: '20px' }}>
        <SketchToggle
          label="Friction"
          checked={friction}
          onChange={setFriction}
          colorOn={NOTEBOOK_THEME.markerGreen}
        />
        
        <SketchToggle
          label="Gravity"
          checked={gravity}
          onChange={setGravity}
          colorOn={NOTEBOOK_THEME.markerBlue}
        />
        
        <SketchToggle
          label="Air Resistance"
          checked={airResistance}
          onChange={setAirResistance}
          colorOn={NOTEBOOK_THEME.markerRed}
        />
        
        <div
          style={{
            marginTop: '16px',
            padding: '12px',
            background: NOTEBOOK_THEME.paperWarm,
            borderRadius: '8px',
            fontFamily: NOTEBOOK_THEME.handwriting,
          }}
        >
          <strong>Active Forces:</strong>
          <ul style={{ marginTop: '8px', marginLeft: '20px' }}>
            {friction && <li>Friction</li>}
            {gravity && <li>Gravity</li>}
            {airResistance && <li>Air Resistance</li>}
            {!friction && !gravity && !airResistance && <li>None</li>}
          </ul>
        </div>
      </div>
    </div>
  );
};

// ============================================
// EXAMPLE 3: SketchButton Demo
// ============================================

export const Example3_Button = () => {
  const [count, setCount] = useState(0);
  
  return (
    <div style={{ padding: '20px', maxWidth: '400px' }}>
      <h2 style={{ fontFamily: NOTEBOOK_THEME.handwriting }}>
        Example 3: Sketch Buttons
      </h2>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginTop: '20px', alignItems: 'flex-start' }}>
        <SketchButton
          variant="primary"
          onClick={() => setCount(count + 1)}
        >
          Click Me!
        </SketchButton>
        
        <SketchButton
          variant="secondary"
          onClick={() => alert('Secondary button!')}
        >
          Secondary
        </SketchButton>
        
        <SketchButton
          variant="outline"
          onClick={() => console.log('Outline clicked')}
        >
          Outline Style
        </SketchButton>
        
        <SketchButton
          variant="primary"
          icon="🎨"
          onClick={() => alert('With icon!')}
        >
          With Icon
        </SketchButton>
        
        <SketchButton
          disabled
          onClick={() => {}}
        >
          Disabled
        </SketchButton>
        
        <div
          style={{
            marginTop: '16px',
            padding: '12px',
            background: NOTEBOOK_THEME.highlightBlue,
            borderRadius: '8px',
            fontFamily: NOTEBOOK_THEME.handwriting,
            fontSize: '18px',
          }}
        >
          Clicked: <strong>{count}</strong> times
        </div>
      </div>
    </div>
  );
};

// ============================================
// EXAMPLE 4: SketchKnob Demo
// ============================================

export const Example4_Knob = () => {
  const [volume, setVolume] = useState(50);
  const [brightness, setBrightness] = useState(75);
  
  return (
    <div style={{ padding: '20px', maxWidth: '400px' }}>
      <h2 style={{ fontFamily: NOTEBOOK_THEME.handwriting }}>
        Example 4: Sketch Knobs
      </h2>
      
      <div style={{ display: 'flex', gap: '40px', marginTop: '20px', justifyContent: 'center', flexWrap: 'wrap' }}>
        <SketchKnob
          label="Volume"
          value={volume}
          min={0}
          max={100}
          unit="%"
          color={NOTEBOOK_THEME.markerBlue}
          onChange={setVolume}
        />
        
        <SketchKnob
          label="Brightness"
          value={brightness}
          min={0}
          max={100}
          unit="%"
          color={NOTEBOOK_THEME.markerGreen}
          size={100}
          onChange={setBrightness}
        />
      </div>
    </div>
  );
};

// ============================================
// EXAMPLE 5: Complete Interactive Scene
// ============================================

export const Example5_Complete = () => {
  const [force, setForce] = useState(50);
  const [showVectors, setShowVectors] = useState(true);
  const [playAnimation, setPlayAnimation] = useState(false);
  const [angle, setAngle] = useState(45);
  
  return (
    <div style={{ padding: '20px', maxWidth: '600px' }}>
      <h2 style={{ fontFamily: NOTEBOOK_THEME.handwriting }}>
        Example 5: Complete Interactive Scene
      </h2>
      
      <div
        style={{
          marginTop: '20px',
          padding: '24px',
          background: NOTEBOOK_THEME.paperBg,
          borderRadius: '12px',
          border: `2px solid ${NOTEBOOK_THEME.lineColor}`,
        }}
      >
        {/* Simulation Area */}
        <div
          style={{
            height: '200px',
            background: NOTEBOOK_THEME.paperWarm,
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontFamily: NOTEBOOK_THEME.handwriting,
            fontSize: '18px',
            marginBottom: '24px',
          }}
        >
          <div style={{ textAlign: 'center' }}>
            <div>Force: {force}N</div>
            <div>Angle: {angle}°</div>
            <div>{playAnimation ? '▶️ Playing' : '⏸️ Paused'}</div>
            {showVectors && <div>↗️ Vectors Visible</div>}
          </div>
        </div>
        
        {/* Controls */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <SketchSlider
            label="Force"
            value={force}
            min={0}
            max={100}
            unit=" N"
            onChange={setForce}
          />
          
          <div style={{ display: 'flex', gap: '24px', alignItems: 'center', flexWrap: 'wrap' }}>
            <SketchToggle
              label="Show Vectors"
              checked={showVectors}
              onChange={setShowVectors}
            />
            
            <SketchButton
              variant={playAnimation ? 'secondary' : 'primary'}
              icon={playAnimation ? '⏸️' : '▶️'}
              onClick={() => setPlayAnimation(!playAnimation)}
            >
              {playAnimation ? 'Pause' : 'Play'}
            </SketchButton>
            
            <SketchButton
              variant="outline"
              onClick={() => {
                setForce(50);
                setAngle(45);
                setShowVectors(true);
                setPlayAnimation(false);
              }}
            >
              Reset
            </SketchButton>
          </div>
          
          <div style={{ display: 'flex', justifyContent: 'center' }}>
            <SketchKnob
              label="Launch Angle"
              value={angle}
              min={0}
              max={90}
              unit="°"
              color={NOTEBOOK_THEME.markerPurple}
              size={80}
              onChange={setAngle}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

// ============================================
// ALL EXAMPLES
// ============================================

export const AllControlExamples = () => {
  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '40px 20px' }}>
      <h1 style={{ fontFamily: NOTEBOOK_THEME.handwriting }}>
        🎛️ Sketchy Interactive Controls
      </h1>
      <p>Hand-drawn controls with ZERO HTML inputs - Pure SVG + RoughJS!</p>
      
      <hr style={{ margin: '40px 0' }} />
      
      <div style={{ display: 'grid', gap: '40px', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))' }}>
        <Example1_Slider />
        <Example2_Toggle />
        <Example3_Button />
        <Example4_Knob />
      </div>
      
      <hr style={{ margin: '40px 0' }} />
      
      <Example5_Complete />
    </div>
  );
};

export default AllControlExamples;

