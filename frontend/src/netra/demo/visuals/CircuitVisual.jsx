/**
 * ⚡ CIRCUIT ELECTRICITY VISUAL v2.0
 * ==================================
 * 
 * Premium, Apple-level interactive simulation of electricity in a circuit.
 * NOT a video - a true interactive simulation.
 * 
 * Features:
 * - MagicBook-style light background with notebook grid
 * - Progressive generation reveal (not instant)
 * - True interactivity (instant response to user actions)
 * - Cinematic wow factor (zoom, focus, step mode)
 * - Tooltips on components
 * - Step-by-step guided mode
 * 
 * @author Netra Team
 * @version 2.0.0 (VC Demo - Premium)
 */

import React, { useEffect, useRef, useState, useCallback } from 'react';

// Generation phases (progressive reveal)
const GENERATION_PHASES = {
  LOADING: 'loading',
  DRAWING_GRID: 'drawing_grid',
  PLACING_BATTERY: 'placing_battery',
  DRAWING_WIRES: 'drawing_wires',
  PLACING_SWITCH: 'placing_switch',
  PLACING_BULB: 'placing_bulb',
  READY: 'ready',
  INTERACTIVE: 'interactive',
};

// Step mode for guided learning
const LEARNING_STEPS = [
  { id: 1, title: 'Battery provides energy', focus: 'battery', hint: 'The battery creates electrical potential (voltage)' },
  { id: 2, title: 'Toggle the switch', focus: 'switch', hint: 'Click the switch to complete the circuit' },
  { id: 3, title: 'Current flows through wire', focus: 'wire', hint: 'Electrons flow from - to + terminal' },
  { id: 4, title: 'Bulb converts energy to light', focus: 'bulb', hint: 'Electrical energy → Light + Heat' },
];

// Premium color palette (MagicBook style)
const COLORS = {
  // Background
  paper: '#fdfcf8',
  grid: '#e2e8f0',
  gridDark: '#cbd5e1',
  
  // Components
  wire: '#3b82f6',
  wireGlow: '#60a5fa',
  battery: '#1e293b',
  batteryPositive: '#ef4444',
  batteryNegative: '#3b82f6',
  switch: '#475569',
  switchOn: '#22c55e',
  switchOff: '#ef4444',
  bulbOff: '#94a3b8',
  bulbOn: '#fbbf24',
  bulbGlow: '#fef3c7',
  
  // Electrons
  electron: '#00d4ff',
  electronGlow: '#38bdf8',
  
  // UI
  text: '#1e293b',
  textMuted: '#64748b',
  accent: '#8b5cf6',
  tooltip: '#1e293b',
};

// Electron particle
class Electron {
  constructor(pathIndex, offset, speed) {
    this.pathIndex = pathIndex;
    this.offset = offset;
    this.speed = speed;
    this.progress = offset;
    this.size = 5 + Math.random() * 2;
    this.pulsePhase = Math.random() * Math.PI * 2;
  }

  update(dt, isFlowing, voltage) {
    if (isFlowing) {
      this.progress += dt * this.speed * voltage * 0.0004;
      if (this.progress > 1) this.progress -= 1;
    }
    this.pulsePhase += dt * 0.008;
  }
}

export default function CircuitVisual({ 
  width = 720, 
  height = 520, 
  theme,
  isPlaying,
  onReady,
  onPhaseChange,
}) {
  const canvasRef = useRef(null);
  const animationRef = useRef(null);
  
  // Generation state (progressive reveal)
  const [generationPhase, setGenerationPhase] = useState(GENERATION_PHASES.LOADING);
  const [generationProgress, setGenerationProgress] = useState(0);
  
  // Interactive state
  const [switchOn, setSwitchOn] = useState(false);
  const [voltage, setVoltage] = useState(0.7);
  const [resistance, setResistance] = useState(0.5);
  
  // Learning mode
  const [currentStep, setCurrentStep] = useState(0);
  const [showStepMode, setShowStepMode] = useState(true);
  const [hoveredComponent, setHoveredComponent] = useState(null);
  
  // Camera/focus
  const [cameraFocus, setCameraFocus] = useState({ x: 0, y: 0, zoom: 1 });
  const [targetFocus, setTargetFocus] = useState({ x: 0, y: 0, zoom: 1 });
  
  // Electrons
  const [electrons, setElectrons] = useState([]);
  
  // Timing
  const startTimeRef = useRef(Date.now());
  const lastTimeRef = useRef(Date.now());
  const generationStartRef = useRef(null);

  // Circuit geometry
  const circuitPath = useRef([]);
  const componentBounds = useRef({});

  // Initialize circuit geometry
  useEffect(() => {
    const cx = width / 2;
    const cy = height / 2;
    const w = width * 0.6;
    const h = height * 0.5;

    // Define wire path points
    const path = [];
    const segments = 60;
    
    // Create rectangular path with rounded corners
    for (let i = 0; i <= segments; i++) {
      const t = i / segments;
      let x, y;
      
      if (t < 0.25) {
        // Top edge (left to right)
        const lt = t / 0.25;
        x = cx - w/2 + lt * w;
        y = cy - h/2;
      } else if (t < 0.5) {
        // Right edge (top to bottom)
        const lt = (t - 0.25) / 0.25;
        x = cx + w/2;
        y = cy - h/2 + lt * h;
      } else if (t < 0.75) {
        // Bottom edge (right to left)
        const lt = (t - 0.5) / 0.25;
        x = cx + w/2 - lt * w;
        y = cy + h/2;
      } else {
        // Left edge (bottom to top)
        const lt = (t - 0.75) / 0.25;
        x = cx - w/2;
        y = cy + h/2 - lt * h;
      }
      
      path.push({ x, y });
    }
    
    circuitPath.current = path;

    // Component positions and bounds
    componentBounds.current = {
      battery: { x: cx - w/2 - 10, y: cy, width: 70, height: 110, label: 'Battery', info: 'Provides electrical energy (12V DC)' },
      switch: { x: cx, y: cy - h/2 - 5, width: 80, height: 40, label: 'Switch', info: 'Controls current flow (ON/OFF)' },
      bulb: { x: cx + w/2 + 10, y: cy, width: 80, height: 100, label: 'Light Bulb', info: 'Converts electrical energy to light' },
      resistor: { x: cx, y: cy + h/2, width: 60, height: 25, label: 'Resistor', info: 'Controls current flow rate' },
    };

    // Create electrons
    const newElectrons = [];
    for (let i = 0; i < 20; i++) {
      newElectrons.push(new Electron(0, i / 20, 0.6 + Math.random() * 0.4));
    }
    setElectrons(newElectrons);

  }, [width, height]);

  // Progressive generation effect
  useEffect(() => {
    if (!generationStartRef.current) {
      generationStartRef.current = Date.now();
    }

    const runGeneration = () => {
      const elapsed = Date.now() - generationStartRef.current;
      
      // Phase timing (progressive reveal)
      if (elapsed < 500) {
        setGenerationPhase(GENERATION_PHASES.LOADING);
        setGenerationProgress(elapsed / 500);
      } else if (elapsed < 1000) {
        setGenerationPhase(GENERATION_PHASES.DRAWING_GRID);
        setGenerationProgress((elapsed - 500) / 500);
      } else if (elapsed < 1800) {
        setGenerationPhase(GENERATION_PHASES.PLACING_BATTERY);
        setGenerationProgress((elapsed - 1000) / 800);
      } else if (elapsed < 3000) {
        setGenerationPhase(GENERATION_PHASES.DRAWING_WIRES);
        setGenerationProgress((elapsed - 1800) / 1200);
      } else if (elapsed < 3800) {
        setGenerationPhase(GENERATION_PHASES.PLACING_SWITCH);
        setGenerationProgress((elapsed - 3000) / 800);
      } else if (elapsed < 4600) {
        setGenerationPhase(GENERATION_PHASES.PLACING_BULB);
        setGenerationProgress((elapsed - 3800) / 800);
      } else if (elapsed < 5200) {
        setGenerationPhase(GENERATION_PHASES.READY);
        setGenerationProgress((elapsed - 4600) / 600);
      } else {
        setGenerationPhase(GENERATION_PHASES.INTERACTIVE);
        onReady?.();
        return; // Stop interval
      }
    };

    const interval = setInterval(runGeneration, 50);
    runGeneration();

    return () => clearInterval(interval);
  }, [onReady]);

  // Camera animation
  useEffect(() => {
    const animateCamera = () => {
      setCameraFocus(prev => ({
        x: prev.x + (targetFocus.x - prev.x) * 0.08,
        y: prev.y + (targetFocus.y - prev.y) * 0.08,
        zoom: prev.zoom + (targetFocus.zoom - prev.zoom) * 0.08,
      }));
    };
    
    const interval = setInterval(animateCamera, 16);
    return () => clearInterval(interval);
  }, [targetFocus]);

  // Focus on step
  useEffect(() => {
    if (!showStepMode || currentStep === 0) {
      setTargetFocus({ x: 0, y: 0, zoom: 1 });
      return;
    }

    const step = LEARNING_STEPS[currentStep - 1];
    const bounds = componentBounds.current[step?.focus];
    
    if (bounds && step.focus !== 'wire') {
      setTargetFocus({
        x: (width/2 - bounds.x) * 0.3,
        y: (height/2 - bounds.y) * 0.3,
        zoom: 1.15,
      });
    } else {
      setTargetFocus({ x: 0, y: 0, zoom: 1 });
    }
  }, [currentStep, showStepMode, width, height]);

  // Main animation loop
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    const animate = () => {
      const now = Date.now();
      const dt = now - lastTimeRef.current;
      lastTimeRef.current = now;

      // Clear with paper background
      ctx.fillStyle = COLORS.paper;
      ctx.fillRect(0, 0, width, height);

      // Apply camera transform
      ctx.save();
      ctx.translate(width/2, height/2);
      ctx.scale(cameraFocus.zoom, cameraFocus.zoom);
      ctx.translate(-width/2 + cameraFocus.x, -height/2 + cameraFocus.y);

      // Draw based on generation phase
      if (generationPhase !== GENERATION_PHASES.LOADING) {
        drawNotebookGrid(ctx);
      }

      if (shouldShowComponent('battery')) {
        drawBattery(ctx, getComponentOpacity('battery'));
      }

      if (shouldShowComponent('wires')) {
        drawWires(ctx, getWireProgress());
      }

      if (shouldShowComponent('switch')) {
        drawSwitch(ctx, getComponentOpacity('switch'));
      }

      if (shouldShowComponent('bulb')) {
        drawBulb(ctx, getComponentOpacity('bulb'));
      }

      // Draw electrons only when interactive and switch is on
      if (generationPhase === GENERATION_PHASES.INTERACTIVE && switchOn && isPlaying) {
        electrons.forEach(e => e.update(dt, switchOn, voltage));
        drawElectrons(ctx);
      }

      // Draw component highlights and tooltips
      if (generationPhase === GENERATION_PHASES.INTERACTIVE) {
        drawHighlights(ctx);
      }

      ctx.restore();

      // Draw UI overlays (not affected by camera)
      if (generationPhase !== GENERATION_PHASES.INTERACTIVE) {
        drawGenerationOverlay(ctx);
      }

      animationRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [width, height, generationPhase, generationProgress, switchOn, voltage, isPlaying, electrons, cameraFocus, hoveredComponent, currentStep, showStepMode]);

  // Helper: Should show component based on generation phase
  const shouldShowComponent = (component) => {
    const phases = Object.values(GENERATION_PHASES);
    const currentIndex = phases.indexOf(generationPhase);
    
    switch (component) {
      case 'battery': return currentIndex >= phases.indexOf(GENERATION_PHASES.PLACING_BATTERY);
      case 'wires': return currentIndex >= phases.indexOf(GENERATION_PHASES.DRAWING_WIRES);
      case 'switch': return currentIndex >= phases.indexOf(GENERATION_PHASES.PLACING_SWITCH);
      case 'bulb': return currentIndex >= phases.indexOf(GENERATION_PHASES.PLACING_BULB);
      default: return false;
    }
  };

  // Helper: Get component opacity for fade-in
  const getComponentOpacity = (component) => {
    const phases = Object.values(GENERATION_PHASES);
    const currentIndex = phases.indexOf(generationPhase);
    
    let targetIndex;
    switch (component) {
      case 'battery': targetIndex = phases.indexOf(GENERATION_PHASES.PLACING_BATTERY); break;
      case 'switch': targetIndex = phases.indexOf(GENERATION_PHASES.PLACING_SWITCH); break;
      case 'bulb': targetIndex = phases.indexOf(GENERATION_PHASES.PLACING_BULB); break;
      default: return 1;
    }
    
    if (currentIndex === targetIndex) return generationProgress;
    if (currentIndex > targetIndex) return 1;
    return 0;
  };

  // Helper: Get wire drawing progress
  const getWireProgress = () => {
    if (generationPhase === GENERATION_PHASES.DRAWING_WIRES) return generationProgress;
    if (Object.values(GENERATION_PHASES).indexOf(generationPhase) > Object.values(GENERATION_PHASES).indexOf(GENERATION_PHASES.DRAWING_WIRES)) return 1;
    return 0;
  };

  // Drawing functions
  const drawNotebookGrid = (ctx) => {
    const gridSize = 25;
    const dotSize = 1.5;
    
    ctx.fillStyle = COLORS.grid;
    
    for (let x = gridSize; x < width; x += gridSize) {
      for (let y = gridSize; y < height; y += gridSize) {
        ctx.beginPath();
        ctx.arc(x, y, dotSize, 0, Math.PI * 2);
        ctx.fill();
      }
    }
  };

  const drawWires = (ctx, progress) => {
    const path = circuitPath.current;
    if (path.length < 2 || progress === 0) return;

    const drawLength = Math.floor(path.length * progress);
    
    // Wire shadow
    ctx.strokeStyle = 'rgba(0, 0, 0, 0.1)';
    ctx.lineWidth = 10;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    
    ctx.beginPath();
    ctx.moveTo(path[0].x + 2, path[0].y + 2);
    for (let i = 1; i < drawLength; i++) {
      ctx.lineTo(path[i].x + 2, path[i].y + 2);
    }
    ctx.stroke();

    // Main wire
    const isActive = switchOn && generationPhase === GENERATION_PHASES.INTERACTIVE;
    
    if (isActive) {
      // Glowing wire when active
      ctx.shadowColor = COLORS.wireGlow;
      ctx.shadowBlur = 15;
    }
    
    ctx.strokeStyle = isActive ? COLORS.wireGlow : COLORS.wire;
    ctx.lineWidth = 6;
    
    ctx.beginPath();
    ctx.moveTo(path[0].x, path[0].y);
    for (let i = 1; i < drawLength; i++) {
      ctx.lineTo(path[i].x, path[i].y);
    }
    ctx.stroke();
    
    // Inner wire highlight
    ctx.shadowBlur = 0;
    ctx.strokeStyle = isActive ? '#93c5fd' : '#60a5fa';
    ctx.lineWidth = 2;
    ctx.stroke();
  };

  const drawBattery = (ctx, opacity) => {
    const { x, y, width: w, height: h } = componentBounds.current.battery;
    
    ctx.globalAlpha = opacity;
    
    // Battery body shadow
    ctx.fillStyle = 'rgba(0, 0, 0, 0.15)';
    ctx.beginPath();
    ctx.roundRect(x - w/2 + 3, y - h/2 + 3, w, h, 8);
    ctx.fill();
    
    // Battery body
    const gradient = ctx.createLinearGradient(x - w/2, y, x + w/2, y);
    gradient.addColorStop(0, '#374151');
    gradient.addColorStop(0.3, '#4b5563');
    gradient.addColorStop(0.7, '#4b5563');
    gradient.addColorStop(1, '#374151');
    
    ctx.fillStyle = gradient;
    ctx.beginPath();
    ctx.roundRect(x - w/2, y - h/2, w, h, 8);
    ctx.fill();
    
    // Battery border
    ctx.strokeStyle = '#1f2937';
    ctx.lineWidth = 2;
    ctx.stroke();
    
    // Positive terminal
    ctx.fillStyle = COLORS.batteryPositive;
    ctx.beginPath();
    ctx.roundRect(x - 12, y - h/2 - 18, 24, 22, 4);
    ctx.fill();
    ctx.strokeStyle = '#b91c1c';
    ctx.lineWidth = 2;
    ctx.stroke();
    
    // Plus symbol
    ctx.fillStyle = '#fff';
    ctx.fillRect(x - 6, y - h/2 - 12, 12, 3);
    ctx.fillRect(x - 1.5, y - h/2 - 17, 3, 13);
    
    // Negative terminal
    ctx.fillStyle = COLORS.batteryNegative;
    ctx.beginPath();
    ctx.roundRect(x - 12, y + h/2 - 4, 24, 22, 4);
    ctx.fill();
    ctx.strokeStyle = '#1d4ed8';
    ctx.lineWidth = 2;
    ctx.stroke();
    
    // Minus symbol
    ctx.fillStyle = '#fff';
    ctx.fillRect(x - 6, y + h/2 + 5, 12, 3);
    
    // Voltage label
    ctx.fillStyle = COLORS.bulbOn;
    ctx.font = 'bold 18px Inter, system-ui, sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(`${Math.round(voltage * 12)}V`, x, y);
    
    // Component label
    ctx.fillStyle = COLORS.textMuted;
    ctx.font = '12px Inter, system-ui, sans-serif';
    ctx.fillText('BATTERY', x, y + h/2 + 35);
    
    ctx.globalAlpha = 1;
  };

  const drawSwitch = (ctx, opacity) => {
    const { x, y, width: w, height: h } = componentBounds.current.switch;
    
    ctx.globalAlpha = opacity;
    
    // Switch housing
    ctx.fillStyle = '#e2e8f0';
    ctx.beginPath();
    ctx.roundRect(x - w/2, y - h/2, w, h, 6);
    ctx.fill();
    ctx.strokeStyle = '#94a3b8';
    ctx.lineWidth = 2;
    ctx.stroke();
    
    // Contact points
    ctx.fillStyle = '#64748b';
    ctx.beginPath();
    ctx.arc(x - 28, y, 6, 0, Math.PI * 2);
    ctx.arc(x + 28, y, 6, 0, Math.PI * 2);
    ctx.fill();
    
    // Switch lever
    ctx.strokeStyle = switchOn ? COLORS.switchOn : COLORS.switchOff;
    ctx.lineWidth = 5;
    ctx.lineCap = 'round';
    
    if (switchOn) {
      // Glow when on
      ctx.shadowColor = COLORS.switchOn;
      ctx.shadowBlur = 10;
    }
    
    ctx.beginPath();
    ctx.moveTo(x - 28, y);
    if (switchOn) {
      ctx.lineTo(x + 28, y);
    } else {
      ctx.lineTo(x + 15, y - 25);
    }
    ctx.stroke();
    ctx.shadowBlur = 0;
    
    // Lever handle
    ctx.fillStyle = switchOn ? COLORS.switchOn : COLORS.switchOff;
    ctx.beginPath();
    if (switchOn) {
      ctx.arc(x + 28, y, 8, 0, Math.PI * 2);
    } else {
      ctx.arc(x + 15, y - 25, 8, 0, Math.PI * 2);
    }
    ctx.fill();
    
    // Label
    ctx.fillStyle = COLORS.textMuted;
    ctx.font = '12px Inter, system-ui, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('SWITCH', x, y + h/2 + 20);
    
    // Status indicator
    ctx.fillStyle = switchOn ? COLORS.switchOn : COLORS.switchOff;
    ctx.font = 'bold 10px Inter, system-ui, sans-serif';
    ctx.fillText(switchOn ? 'ON' : 'OFF', x, y + h/2 + 35);
    
    ctx.globalAlpha = 1;
  };

  const drawBulb = (ctx, opacity) => {
    const { x, y, width: w, height: h } = componentBounds.current.bulb;
    const isLit = switchOn && generationPhase === GENERATION_PHASES.INTERACTIVE;
    const brightness = isLit ? voltage * (1 - resistance * 0.5) : 0;
    
    ctx.globalAlpha = opacity;
    
    // Bulb glow (when lit)
    if (isLit && brightness > 0) {
      const glowRadius = 60 + brightness * 40;
      const gradient = ctx.createRadialGradient(x, y - 15, 0, x, y - 15, glowRadius);
      gradient.addColorStop(0, `rgba(251, 191, 36, ${brightness * 0.6})`);
      gradient.addColorStop(0.4, `rgba(251, 191, 36, ${brightness * 0.3})`);
      gradient.addColorStop(1, 'transparent');
      ctx.fillStyle = gradient;
      ctx.fillRect(x - glowRadius, y - 15 - glowRadius, glowRadius * 2, glowRadius * 2);
    }
    
    // Bulb glass
    ctx.shadowColor = isLit ? COLORS.bulbOn : 'transparent';
    ctx.shadowBlur = isLit ? 20 : 0;
    
    const bulbGradient = ctx.createRadialGradient(x - 10, y - 25, 0, x, y - 10, 40);
    if (isLit) {
      bulbGradient.addColorStop(0, '#fffbeb');
      bulbGradient.addColorStop(0.5, COLORS.bulbOn);
      bulbGradient.addColorStop(1, '#f59e0b');
    } else {
      bulbGradient.addColorStop(0, '#f1f5f9');
      bulbGradient.addColorStop(1, '#cbd5e1');
    }
    
    ctx.fillStyle = bulbGradient;
    ctx.beginPath();
    ctx.arc(x, y - 10, 35, 0, Math.PI * 2);
    ctx.fill();
    
    // Glass highlight
    ctx.fillStyle = 'rgba(255, 255, 255, 0.4)';
    ctx.beginPath();
    ctx.arc(x - 12, y - 22, 10, 0, Math.PI * 2);
    ctx.fill();
    
    ctx.shadowBlur = 0;
    
    // Bulb base (screw cap)
    const baseGradient = ctx.createLinearGradient(x - 15, y + 25, x + 15, y + 25);
    baseGradient.addColorStop(0, '#78716c');
    baseGradient.addColorStop(0.5, '#a8a29e');
    baseGradient.addColorStop(1, '#78716c');
    
    ctx.fillStyle = baseGradient;
    ctx.beginPath();
    ctx.roundRect(x - 15, y + 25, 30, 30, 4);
    ctx.fill();
    
    // Screw threads
    ctx.strokeStyle = '#57534e';
    ctx.lineWidth = 1.5;
    for (let i = 0; i < 4; i++) {
      ctx.beginPath();
      ctx.moveTo(x - 15, y + 30 + i * 7);
      ctx.lineTo(x + 15, y + 30 + i * 7);
      ctx.stroke();
    }
    
    // Filament
    ctx.strokeStyle = isLit ? `rgba(255, 255, 255, ${0.8 + brightness * 0.2})` : '#94a3b8';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(x - 10, y + 10);
    ctx.quadraticCurveTo(x - 5, y - 15, x, y + 5);
    ctx.quadraticCurveTo(x + 5, y - 20, x + 10, y + 10);
    ctx.stroke();
    
    // Label
    ctx.fillStyle = COLORS.textMuted;
    ctx.font = '12px Inter, system-ui, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('LIGHT BULB', x, y + 70);
    
    ctx.globalAlpha = 1;
  };

  const drawElectrons = (ctx) => {
    const path = circuitPath.current;
    if (path.length < 2) return;

    electrons.forEach(electron => {
      const idx = Math.floor(electron.progress * (path.length - 1));
      const nextIdx = (idx + 1) % path.length;
      const t = (electron.progress * (path.length - 1)) % 1;
      
      const p1 = path[idx];
      const p2 = path[nextIdx];
      
      const x = p1.x + (p2.x - p1.x) * t;
      const y = p1.y + (p2.y - p1.y) * t;
      
      // Electron glow
      const pulse = 0.6 + Math.sin(electron.pulsePhase) * 0.4;
      const gradient = ctx.createRadialGradient(x, y, 0, x, y, electron.size * 3);
      gradient.addColorStop(0, `rgba(0, 212, 255, ${pulse})`);
      gradient.addColorStop(0.5, `rgba(0, 212, 255, ${pulse * 0.4})`);
      gradient.addColorStop(1, 'transparent');
      ctx.fillStyle = gradient;
      ctx.fillRect(x - 15, y - 15, 30, 30);
      
      // Electron core
      ctx.fillStyle = COLORS.electron;
      ctx.beginPath();
      ctx.arc(x, y, electron.size, 0, Math.PI * 2);
      ctx.fill();
      
      // Inner highlight
      ctx.fillStyle = '#fff';
      ctx.beginPath();
      ctx.arc(x - 1, y - 1, electron.size * 0.4, 0, Math.PI * 2);
      ctx.fill();
    });
  };

  const drawHighlights = (ctx) => {
    // Draw step highlight
    if (showStepMode && currentStep > 0) {
      const step = LEARNING_STEPS[currentStep - 1];
      const bounds = componentBounds.current[step?.focus];
      
      if (bounds && step.focus !== 'wire') {
        // Highlight ring
        ctx.strokeStyle = COLORS.accent;
        ctx.lineWidth = 3;
        ctx.setLineDash([8, 4]);
        ctx.beginPath();
        ctx.arc(bounds.x, bounds.y, Math.max(bounds.width, bounds.height) * 0.7, 0, Math.PI * 2);
        ctx.stroke();
        ctx.setLineDash([]);
      }
    }
    
    // Draw tooltip for hovered component
    if (hoveredComponent) {
      const bounds = componentBounds.current[hoveredComponent];
      if (bounds) {
        drawTooltip(ctx, bounds.x, bounds.y - bounds.height/2 - 40, bounds.info);
      }
    }
  };

  const drawTooltip = (ctx, x, y, text) => {
    ctx.font = '12px Inter, system-ui, sans-serif';
    const metrics = ctx.measureText(text);
    const padding = 10;
    const w = metrics.width + padding * 2;
    const h = 28;
    
    // Tooltip background
    ctx.fillStyle = COLORS.tooltip;
    ctx.beginPath();
    ctx.roundRect(x - w/2, y - h/2, w, h, 6);
    ctx.fill();
    
    // Arrow
    ctx.beginPath();
    ctx.moveTo(x - 6, y + h/2);
    ctx.lineTo(x, y + h/2 + 8);
    ctx.lineTo(x + 6, y + h/2);
    ctx.fill();
    
    // Text
    ctx.fillStyle = '#fff';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(text, x, y);
  };

  const drawGenerationOverlay = (ctx) => {
    // Semi-transparent overlay
    ctx.fillStyle = 'rgba(253, 252, 248, 0.9)';
    ctx.fillRect(0, 0, width, height);
    
    // Generation status
    const statusText = {
      [GENERATION_PHASES.LOADING]: 'Analyzing question...',
      [GENERATION_PHASES.DRAWING_GRID]: 'Setting up workspace...',
      [GENERATION_PHASES.PLACING_BATTERY]: 'Adding battery...',
      [GENERATION_PHASES.DRAWING_WIRES]: 'Drawing circuit wires...',
      [GENERATION_PHASES.PLACING_SWITCH]: 'Placing switch...',
      [GENERATION_PHASES.PLACING_BULB]: 'Adding light bulb...',
      [GENERATION_PHASES.READY]: 'Preparing simulation...',
    };
    
    // Centered text
    ctx.fillStyle = COLORS.text;
    ctx.font = '16px Inter, system-ui, sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(statusText[generationPhase] || 'Generating...', width/2, height/2 - 20);
    
    // Progress bar
    const barWidth = 200;
    const barHeight = 6;
    const barX = (width - barWidth) / 2;
    const barY = height/2 + 10;
    
    // Bar background
    ctx.fillStyle = '#e2e8f0';
    ctx.beginPath();
    ctx.roundRect(barX, barY, barWidth, barHeight, 3);
    ctx.fill();
    
    // Bar progress
    const phases = Object.values(GENERATION_PHASES);
    const currentIndex = phases.indexOf(generationPhase);
    const totalProgress = (currentIndex + generationProgress) / (phases.length - 1);
    
    const gradient = ctx.createLinearGradient(barX, barY, barX + barWidth, barY);
    gradient.addColorStop(0, COLORS.accent);
    gradient.addColorStop(1, '#a78bfa');
    ctx.fillStyle = gradient;
    ctx.beginPath();
    ctx.roundRect(barX, barY, barWidth * totalProgress, barHeight, 3);
    ctx.fill();
    
    // Netra branding
    ctx.fillStyle = COLORS.textMuted;
    ctx.font = '11px Inter, system-ui, sans-serif';
    ctx.fillText('Netra Visual Engine', width/2, height/2 + 40);
  };

  // Handle canvas click
  const handleCanvasClick = (e) => {
    if (generationPhase !== GENERATION_PHASES.INTERACTIVE) return;
    
    const rect = canvasRef.current.getBoundingClientRect();
    const scaleX = width / rect.width;
    const scaleY = height / rect.height;
    const x = (e.clientX - rect.left) * scaleX;
    const y = (e.clientY - rect.top) * scaleY;
    
    // Check switch click
    const sw = componentBounds.current.switch;
    if (x > sw.x - sw.width/2 && x < sw.x + sw.width/2 &&
        y > sw.y - sw.height/2 - 20 && y < sw.y + sw.height/2 + 20) {
      setSwitchOn(prev => !prev);
      
      // Progress to next step if on step 2
      if (showStepMode && currentStep === 2 && !switchOn) {
        setTimeout(() => setCurrentStep(3), 500);
      }
    }
  };

  // Handle mouse move for tooltips
  const handleMouseMove = (e) => {
    if (generationPhase !== GENERATION_PHASES.INTERACTIVE) return;
    
    const rect = canvasRef.current.getBoundingClientRect();
    const scaleX = width / rect.width;
    const scaleY = height / rect.height;
    const x = (e.clientX - rect.left) * scaleX;
    const y = (e.clientY - rect.top) * scaleY;
    
    // Check component hover
    let hovered = null;
    for (const [name, bounds] of Object.entries(componentBounds.current)) {
      if (x > bounds.x - bounds.width/2 - 10 && x < bounds.x + bounds.width/2 + 10 &&
          y > bounds.y - bounds.height/2 - 10 && y < bounds.y + bounds.height/2 + 10) {
        hovered = name;
        break;
      }
    }
    setHoveredComponent(hovered);
  };

  // Handle next/prev step
  const nextStep = () => {
    if (currentStep < LEARNING_STEPS.length) {
      setCurrentStep(prev => prev + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(prev => prev - 1);
    }
  };

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%', background: COLORS.paper }}>
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        onClick={handleCanvasClick}
        onMouseMove={handleMouseMove}
        style={{ 
          width: '100%', 
          height: '100%',
          cursor: generationPhase === GENERATION_PHASES.INTERACTIVE ? 'pointer' : 'default',
        }}
      />
      
      {/* Controls Panel - Only show when interactive */}
      {generationPhase === GENERATION_PHASES.INTERACTIVE && (
        <>
          {/* Voltage Control */}
          <div style={{
            position: 'absolute',
            left: 16,
            top: 16,
            background: 'white',
            padding: '12px 16px',
            borderRadius: '12px',
            boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
            border: '1px solid #e2e8f0',
          }}>
            <div style={{ 
              color: COLORS.textMuted, 
              fontSize: '11px', 
              marginBottom: '6px',
              fontWeight: 600,
              letterSpacing: '0.5px',
            }}>
              VOLTAGE
            </div>
            <input
              type="range"
              min="0.3"
              max="1"
              step="0.05"
              value={voltage}
              onChange={(e) => setVoltage(parseFloat(e.target.value))}
              style={{ width: '100px', accentColor: COLORS.accent }}
            />
            <div style={{ 
              color: COLORS.bulbOn, 
              fontSize: '16px', 
              fontWeight: 'bold',
              marginTop: '4px',
            }}>
              {Math.round(voltage * 12)}V
            </div>
          </div>

          {/* Step Mode Panel */}
          {showStepMode && (
            <div style={{
              position: 'absolute',
              right: 16,
              top: 16,
              background: 'white',
              padding: '16px',
              borderRadius: '12px',
              boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
              border: '1px solid #e2e8f0',
              width: '220px',
            }}>
              <div style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center',
                marginBottom: '12px',
              }}>
                <span style={{ 
                  color: COLORS.text, 
                  fontSize: '13px', 
                  fontWeight: 600 
                }}>
                  📚 Step-by-Step
                </span>
                <button
                  onClick={() => setShowStepMode(false)}
                  style={{
                    background: 'none',
                    border: 'none',
                    color: COLORS.textMuted,
                    cursor: 'pointer',
                    fontSize: '14px',
                  }}
                >
                  ✕
                </button>
              </div>
              
              {currentStep === 0 ? (
                <button
                  onClick={() => setCurrentStep(1)}
                  style={{
                    width: '100%',
                    padding: '10px',
                    background: COLORS.accent,
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    fontWeight: 600,
                    fontSize: '13px',
                  }}
                >
                  Start Learning →
                </button>
              ) : (
                <>
                  <div style={{ 
                    color: COLORS.accent, 
                    fontSize: '12px', 
                    fontWeight: 600,
                    marginBottom: '6px',
                  }}>
                    Step {currentStep} of {LEARNING_STEPS.length}
                  </div>
                  <div style={{ 
                    color: COLORS.text, 
                    fontSize: '14px', 
                    fontWeight: 600,
                    marginBottom: '8px',
                  }}>
                    {LEARNING_STEPS[currentStep - 1]?.title}
                  </div>
                  <div style={{ 
                    color: COLORS.textMuted, 
                    fontSize: '12px',
                    marginBottom: '12px',
                    lineHeight: '1.4',
                  }}>
                    💡 {LEARNING_STEPS[currentStep - 1]?.hint}
                  </div>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <button
                      onClick={prevStep}
                      disabled={currentStep <= 1}
                      style={{
                        flex: 1,
                        padding: '8px',
                        background: currentStep <= 1 ? '#f1f5f9' : '#e2e8f0',
                        color: currentStep <= 1 ? '#94a3b8' : COLORS.text,
                        border: 'none',
                        borderRadius: '6px',
                        cursor: currentStep <= 1 ? 'not-allowed' : 'pointer',
                        fontSize: '12px',
                        fontWeight: 500,
                      }}
                    >
                      ← Back
                    </button>
                    <button
                      onClick={nextStep}
                      disabled={currentStep >= LEARNING_STEPS.length}
                      style={{
                        flex: 1,
                        padding: '8px',
                        background: currentStep >= LEARNING_STEPS.length ? '#f1f5f9' : COLORS.accent,
                        color: currentStep >= LEARNING_STEPS.length ? '#94a3b8' : 'white',
                        border: 'none',
                        borderRadius: '6px',
                        cursor: currentStep >= LEARNING_STEPS.length ? 'not-allowed' : 'pointer',
                        fontSize: '12px',
                        fontWeight: 500,
                      }}
                    >
                      Next →
                    </button>
                  </div>
                </>
              )}
            </div>
          )}

          {/* Interactive Hint */}
          <div style={{
            position: 'absolute',
            left: '50%',
            bottom: 60,
            transform: 'translateX(-50%)',
            background: 'rgba(30, 41, 59, 0.9)',
            padding: '10px 20px',
            borderRadius: '20px',
            fontSize: '13px',
            color: 'white',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
          }}>
            <span style={{ fontSize: '16px' }}>👆</span>
            <span>Click the <strong>switch</strong> to {switchOn ? 'stop' : 'start'} current flow</span>
          </div>
        </>
      )}
    </div>
  );
}
