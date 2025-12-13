/**
 * 📚 DRAWING HAND EXAMPLES
 * =========================
 * 
 * Complete examples showing the drawing hand system
 */

import React, { useState, useEffect } from 'react';
import DrawingHand from './DrawingHand';
import TextBubble, { HintBubble, InsightBubble } from './TextBubble';
import { generateWaypointsFromBlueprint, generateHandTimeline, getHandStateAtTime } from './HandMotionPath';
import { NOTEBOOK_THEME } from '../sketch/SketchPrimitives';

// ============================================
// EXAMPLE 1: Basic Hand Poses
// ============================================

export const Example1_Poses = () => {
  const [pose, setPose] = useState('idle');
  
  return (
    <div style={{ padding: '20px' }}>
      <h2 style={{ fontFamily: NOTEBOOK_THEME.handwriting }}>
        Example 1: Hand Poses
      </h2>
      
      <div style={{ position: 'relative', height: '200px', background: NOTEBOOK_THEME.paperBg, borderRadius: '8px', marginTop: '20px' }}>
        <DrawingHand
          x={100}
          y={100}
          pose={pose}
          size={80}
        />
      </div>
      
      <div style={{ marginTop: '20px', display: 'flex', gap: '12px' }}>
        <button onClick={() => setPose('idle')} style={{ padding: '8px 16px', fontFamily: NOTEBOOK_THEME.handwriting }}>
          Idle
        </button>
        <button onClick={() => setPose('drawing')} style={{ padding: '8px 16px', fontFamily: NOTEBOOK_THEME.handwriting }}>
          Drawing
        </button>
        <button onClick={() => setPose('pointing')} style={{ padding: '8px 16px', fontFamily: NOTEBOOK_THEME.handwriting }}>
          Pointing
        </button>
      </div>
    </div>
  );
};

// ============================================
// EXAMPLE 2: Hand Following Path
// ============================================

export const Example2_FollowPath = () => {
  const [progress, setProgress] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  
  const waypoints = [
    { x: 50, y: 150 },
    { x: 200, y: 100 },
    { x: 350, y: 150 },
  ];
  
  useEffect(() => {
    if (!isPlaying) return;
    
    const interval = setInterval(() => {
      setProgress(p => {
        if (p >= 1) {
          setIsPlaying(false);
          return 0;
        }
        return p + 0.01;
      });
    }, 50);
    
    return () => clearInterval(interval);
  }, [isPlaying]);
  
  const currentWaypoint = Math.floor(progress * (waypoints.length - 1));
  const localProgress = (progress * (waypoints.length - 1)) % 1;
  const start = waypoints[currentWaypoint] || waypoints[0];
  const end = waypoints[currentWaypoint + 1] || waypoints[waypoints.length - 1];
  
  const x = start.x + (end.x - start.x) * localProgress;
  const y = start.y + (end.y - start.y) * localProgress;
  const angle = Math.atan2(end.y - start.y, end.x - start.x) * (180 / Math.PI);
  
  return (
    <div style={{ padding: '20px' }}>
      <h2 style={{ fontFamily: NOTEBOOK_THEME.handwriting }}>
        Example 2: Hand Following Path
      </h2>
      
      <div style={{ position: 'relative', height: '200px', background: NOTEBOOK_THEME.paperBg, borderRadius: '8px', marginTop: '20px' }}>
        {/* Path dots */}
        {waypoints.map((wp, i) => (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: wp.x - 5,
              top: wp.y - 5,
              width: 10,
              height: 10,
              borderRadius: '50%',
              background: NOTEBOOK_THEME.markerBlue,
              opacity: 0.5,
            }}
          />
        ))}
        
        <DrawingHand
          x={x}
          y={y}
          rotation={angle}
          pose={isPlaying ? 'drawing' : 'idle'}
          size={60}
        />
      </div>
      
      <div style={{ marginTop: '20px', display: 'flex', gap: '12px', alignItems: 'center' }}>
        <button
          onClick={() => setIsPlaying(!isPlaying)}
          style={{ padding: '8px 16px', fontFamily: NOTEBOOK_THEME.handwriting }}
        >
          {isPlaying ? 'Pause' : 'Play'}
        </button>
        <button
          onClick={() => { setProgress(0); setIsPlaying(false); }}
          style={{ padding: '8px 16px', fontFamily: NOTEBOOK_THEME.handwriting }}
        >
          Reset
        </button>
        <span style={{ fontFamily: NOTEBOOK_THEME.handwriting }}>
          Progress: {Math.round(progress * 100)}%
        </span>
      </div>
    </div>
  );
};

// ============================================
// EXAMPLE 3: Hand with Text Bubble
// ============================================

export const Example3_WithBubble = () => {
  const [showBubble, setShowBubble] = useState(true);
  
  return (
    <div style={{ padding: '20px' }}>
      <h2 style={{ fontFamily: NOTEBOOK_THEME.handwriting }}>
        Example 3: Hand with Text Bubble
      </h2>
      
      <div style={{ position: 'relative', height: '250px', background: NOTEBOOK_THEME.paperBg, borderRadius: '8px', marginTop: '20px' }}>
        <DrawingHand
          x={150}
          y={180}
          pose="pointing"
          size={70}
        />
        
        <HintBubble
          text="Let me show you how force works! 💪"
          x={50}
          y={20}
          anchorX={150}
          anchorY={180}
          visible={showBubble}
          typewriter={true}
        />
      </div>
      
      <button
        onClick={() => setShowBubble(!showBubble)}
        style={{ marginTop: '20px', padding: '8px 16px', fontFamily: NOTEBOOK_THEME.handwriting }}
      >
        Toggle Bubble
      </button>
    </div>
  );
};

// ============================================
// EXAMPLE 4: Complete Animation Sequence
// ============================================

export const Example4_CompleteSequence = () => {
  const [time, setTime] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  
  const blueprint = {
    items: [
      { id: 'start', position: { x: 80, y: 150 } },
      { id: 'mid', position: { x: 200, y: 100 } },
      { id: 'end', position: { x: 320, y: 150 } },
    ],
  };
  
  const waypoints = generateWaypointsFromBlueprint(blueprint.items);
  const timeline = generateHandTimeline(waypoints, 1.5);
  const handState = getHandStateAtTime(timeline, time);
  
  const maxTime = timeline[timeline.length - 1]?.time || 5;
  
  useEffect(() => {
    if (!isPlaying) return;
    
    const interval = setInterval(() => {
      setTime(t => {
        if (t >= maxTime) {
          setIsPlaying(false);
          return 0;
        }
        return t + 0.05;
      });
    }, 50);
    
    return () => clearInterval(interval);
  }, [isPlaying, maxTime]);
  
  return (
    <div style={{ padding: '20px' }}>
      <h2 style={{ fontFamily: NOTEBOOK_THEME.handwriting }}>
        Example 4: Complete Animation Sequence
      </h2>
      
      <div style={{ position: 'relative', height: '200px', background: NOTEBOOK_THEME.paperBg, borderRadius: '8px', marginTop: '20px' }}>
        {/* Waypoints */}
        {blueprint.items.map((item, i) => (
          <div
            key={item.id}
            style={{
              position: 'absolute',
              left: item.position.x - 8,
              top: item.position.y - 8,
              width: 16,
              height: 16,
              borderRadius: '50%',
              background: NOTEBOOK_THEME.highlightYellow,
              border: `2px solid ${NOTEBOOK_THEME.penBlack}`,
              fontFamily: NOTEBOOK_THEME.handwriting,
              fontSize: '10px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            {i + 1}
          </div>
        ))}
        
        {/* Animated Hand */}
        <DrawingHand
          x={handState.x}
          y={handState.y}
          rotation={handState.angle}
          pose={handState.pose}
          size={60}
        />
        
        {/* Current Beat Text */}
        <div
          style={{
            position: 'absolute',
            top: 10,
            right: 10,
            padding: '8px 12px',
            background: NOTEBOOK_THEME.highlightBlue,
            borderRadius: '8px',
            fontFamily: NOTEBOOK_THEME.handwriting,
            fontSize: '14px',
          }}
        >
          Pose: {handState.pose}
        </div>
      </div>
      
      <div style={{ marginTop: '20px', display: 'flex', gap: '12px', alignItems: 'center' }}>
        <button
          onClick={() => setIsPlaying(!isPlaying)}
          style={{ padding: '8px 16px', fontFamily: NOTEBOOK_THEME.handwriting }}
        >
          {isPlaying ? 'Pause' : 'Play'}
        </button>
        <button
          onClick={() => { setTime(0); setIsPlaying(false); }}
          style={{ padding: '8px 16px', fontFamily: NOTEBOOK_THEME.handwriting }}
        >
          Reset
        </button>
        <span style={{ fontFamily: NOTEBOOK_THEME.handwriting }}>
          Time: {time.toFixed(1)}s / {maxTime.toFixed(1)}s
        </span>
      </div>
    </div>
  );
};

// ============================================
// ALL EXAMPLES
// ============================================

export const AllHandExamples = () => {
  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '40px 20px' }}>
      <h1 style={{ fontFamily: NOTEBOOK_THEME.handwriting }}>
        ✋ Drawing Hand System
      </h1>
      <p>The signature feature - animated hand that follows strokes!</p>
      
      <hr style={{ margin: '40px 0' }} />
      
      <Example1_Poses />
      <hr style={{ margin: '40px 0' }} />
      
      <Example2_FollowPath />
      <hr style={{ margin: '40px 0' }} />
      
      <Example3_WithBubble />
      <hr style={{ margin: '40px 0' }} />
      
      <Example4_CompleteSequence />
    </div>
  );
};

export default AllHandExamples;

