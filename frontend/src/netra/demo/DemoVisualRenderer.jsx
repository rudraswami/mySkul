/**
 * 🎬 DEMO VISUAL RENDERER v2.0
 * ============================
 * 
 * Premium visual renderer for VC demo.
 * MagicBook-style container with light background.
 * 
 * @author Netra Team
 * @version 2.0.0 (VC Demo - Premium)
 */

import React, { useEffect, useRef, useState, useCallback } from 'react';
import CircuitVisual from './visuals/CircuitVisual';
import PhotosynthesisVisual from './visuals/PhotosynthesisVisual';

// MagicBook-style theme (light, clean, notebook feel)
const DEMO_THEME = {
  background: '#fdfcf8',
  surface: '#ffffff',
  border: '#e2e8f0',
  text: '#1e293b',
  textMuted: '#64748b',
  accent: '#8b5cf6',
  success: '#22c55e',
};

/**
 * Demo Visual Renderer Component
 */
export default function DemoVisualRenderer({ 
  demoConfig, 
  width = 640,  // Reduced from 720 for better proportions
  height = 440, // Reduced from 520
  onReady,
  onPhaseChange,
}) {
  const containerRef = useRef(null);
  const [isReady, setIsReady] = useState(false);
  const [currentPhase, setCurrentPhase] = useState('loading');

  // Handle visual ready
  const handleVisualReady = useCallback(() => {
    setIsReady(true);
    setCurrentPhase('interactive');
    onReady?.();
    console.log('🎬 [DEMO] Visual ready:', demoConfig.visualType);
  }, [demoConfig, onReady]);

  // Handle phase change
  const handlePhaseChange = useCallback((phase) => {
    setCurrentPhase(phase);
    onPhaseChange?.(phase);
  }, [onPhaseChange]);

  // Render the appropriate visual
  const renderVisual = () => {
    const commonProps = {
      width,
      height,
      theme: DEMO_THEME,
      isPlaying: true,
      onReady: handleVisualReady,
      onPhaseChange: handlePhaseChange,
    };

    switch (demoConfig.visualType) {
      case 'circuit':
        return <CircuitVisual {...commonProps} />;
      case 'photosynthesis':
        return <PhotosynthesisVisual {...commonProps} />;
      default:
        return <div>Unknown demo visual type</div>;
    }
  };

  return (
    <div 
      ref={containerRef}
      className="demo-visual-container"
      style={{
        width: '100%',
        height: '100%',
        minHeight: height,
        background: DEMO_THEME.background,
        borderRadius: '16px',
        overflow: 'hidden',
        position: 'relative',
        border: `1px solid ${DEMO_THEME.border}`,
        boxShadow: '0 4px 20px rgba(0, 0, 0, 0.08)',
      }}
    >
      {/* Main Visual Area */}
      <div style={{ width: '100%', height: '100%' }}>
        {renderVisual()}
      </div>

      {/* Title Bar */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        padding: '12px 20px',
        background: 'linear-gradient(to bottom, rgba(253, 252, 248, 0.95), transparent)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        pointerEvents: 'none',
        zIndex: 10,
      }}>
        {/* Netra Badge */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          pointerEvents: 'auto',
        }}>
          <div style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            background: isReady ? DEMO_THEME.success : DEMO_THEME.accent,
            boxShadow: isReady ? `0 0 8px ${DEMO_THEME.success}` : 'none',
          }} />
          <span style={{ 
            color: DEMO_THEME.text, 
            fontWeight: 600,
            fontSize: '13px',
            fontFamily: 'Inter, system-ui, sans-serif',
          }}>
            {demoConfig.title}
          </span>
        </div>

        {/* Status Badge */}
        <span style={{
          color: DEMO_THEME.textMuted,
          fontSize: '11px',
          padding: '4px 10px',
          background: 'rgba(255,255,255,0.8)',
          borderRadius: '12px',
          fontFamily: 'Inter, system-ui, sans-serif',
          fontWeight: 500,
          pointerEvents: 'auto',
        }}>
          {isReady ? '✨ Interactive' : '⏳ Generating...'}
        </span>
      </div>

      {/* Bottom Bar */}
      <div style={{
        position: 'absolute',
        bottom: 0,
        left: 0,
        right: 0,
        padding: '12px 20px',
        background: 'linear-gradient(to top, rgba(253, 252, 248, 0.95), transparent)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        pointerEvents: 'none',
        zIndex: 10,
      }}>
        <span style={{
          color: DEMO_THEME.textMuted,
          fontSize: '11px',
          fontFamily: 'Inter, system-ui, sans-serif',
        }}>
          Powered by <strong style={{ color: DEMO_THEME.accent }}>Netra</strong> Visual Engine
        </span>
      </div>
    </div>
  );
}
