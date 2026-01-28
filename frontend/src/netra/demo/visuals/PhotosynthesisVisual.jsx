/**
 * 🌿 PHOTOSYNTHESIS VISUAL v5.0 - CINEMATIC MICRO-WORLD
 * ======================================================
 * 
 * High-end, world-class simulation for VC Demo.
 * 
 * Architecture:
 * - Phase-based cinematic storytelling
 * - Organic procedural shapes (no boxes)
 * - Natural particle flow (CO2, H2O, O2)
 * - Atmospheric depth and lighting
 * - Camera-driven focus transitions
 * 
 * @author Netra Team
 * @version 5.0.0
 */

import React, { useEffect, useRef, useState } from 'react';

// Cinematic Phases
const PHASES = {
  ATMOSPHERE: 'atmosphere',   // Show whole plant in nature
  FOCUS_ZOOM: 'focus_zoom',   // Zoom into leaf surface
  MICRO_WORLD: 'micro_world', // Reveal cellular tissue
  SIMULATION: 'simulation',   // Full interactive simulation
};

// Molecule Particle System
class Particle {
  constructor(type, x, y, vx, vy, options = {}) {
    this.type = type; // 'co2', 'h2o', 'o2', 'glucose'
    this.x = x;
    this.y = y;
    this.vx = vx;
    this.vy = vy;
    this.size = options.size || 3;
    this.alpha = options.alpha || 1;
    this.life = 1;
    this.isAbsorbed = false;
    this.wobble = Math.random() * Math.PI * 2;
  }

  update(dt, windX = 0, windY = 0) {
    this.x += (this.vx + windX) * dt * 0.05;
    this.y += (this.vy + windY) * dt * 0.05;
    
    // Gentle wobble
    this.wobble += dt * 0.005;
    this.x += Math.sin(this.wobble) * 0.2;
    
    if (this.isAbsorbed) {
      this.life -= dt * 0.002;
    }
  }

  draw(ctx) {
  ctx.save();
  ctx.globalAlpha = this.alpha * this.life;

  // Slight parallax wobble glow size
  const base = this.size * 2.2;
  const pulse = 1 + Math.sin(this.wobble) * 0.08;
  const r = base * pulse;

  // Premium palette (soft, cinematic)
  const palette = {
    co2: {
      core: 'rgba(148, 163, 184, 0.35)',  // smoky slate
      glow: 'rgba(15, 23, 42, 0.0)',
      halo: 'rgba(148, 163, 184, 0.18)',
    },
    h2o: {
      core: 'rgba(125, 211, 252, 0.35)',  // water-cyan
      glow: 'rgba(59, 130, 246, 0.0)',
      halo: 'rgba(125, 211, 252, 0.18)',
    },
    o2: {
      core: 'rgba(103, 232, 249, 0.30)',  // oxygen airy
      glow: 'rgba(6, 182, 212, 0.0)',
      halo: 'rgba(103, 232, 249, 0.16)',
    },
    energy: {
      core: 'rgba(253, 230, 138, 0.55)',  // warm photon
      glow: 'rgba(245, 158, 11, 0.0)',
      halo: 'rgba(253, 230, 138, 0.22)',
    },
  };

  const style = palette[this.type] || palette.co2;

  // 1) Outer halo glow
  ctx.save();
  ctx.globalCompositeOperation = 'screen';
  const halo = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, r * 3.2);
  halo.addColorStop(0, style.halo);
  halo.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = halo;
  ctx.beginPath();
  ctx.arc(this.x, this.y, r * 2.6, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();

  // 2) Soft core blob
  const core = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, r * 2.1);
  core.addColorStop(0, style.core);
  core.addColorStop(1, style.glow);

  ctx.fillStyle = core;
  ctx.beginPath();
  ctx.arc(this.x, this.y, r, 0, Math.PI * 2);
  ctx.fill();

  // 3) Specular highlight for water + oxygen (makes it feel liquid)
  if (this.type === 'h2o' || this.type === 'o2') {
    ctx.save();
    ctx.globalAlpha *= 0.65;
    ctx.fillStyle = 'rgba(255,255,255,0.25)';
    ctx.beginPath();
    ctx.arc(this.x - r * 0.35, this.y - r * 0.35, r * 0.35, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }

  // 4) Photon streak effect for energy
  if (this.type === 'energy') {
    ctx.save();
    ctx.globalCompositeOperation = 'screen';
    ctx.globalAlpha *= 0.75;
    ctx.strokeStyle = 'rgba(255,255,255,0.22)';
    ctx.lineWidth = 1.2;

    const len = 24 + Math.sin(this.wobble) * 8;
    ctx.beginPath();
    ctx.moveTo(this.x - 6, this.y - len);
    ctx.lineTo(this.x + 6, this.y + len * 0.6);
    ctx.stroke();

    ctx.restore();
  }

  ctx.restore();   
}
}    

export default function PhotosynthesisVisual({ 
  width = 720, 
  height = 520,
  onReady,
}) {
  const canvasRef = useRef(null);
  const animationRef = useRef(null);
  
  // State
  const [phase, setPhase] = useState(PHASES.ATMOSPHERE);
  const [progress, setProgress] = useState(0);
  const [sunIntensity, setSunIntensity] = useState(0.8);
  const [isReactionRunning, setIsReactionRunning] = useState(false);
  const [showHUD, setShowHUD] = useState(true);
  const [waterLevel, setWaterLevel] = useState(0.0); // 0 → 1
  const [growth, setGrowth] = useState(0.15); // 0 → 1 (start slightly alive)
  const [isWaterOn, setIsWaterOn] = useState(false);

  useEffect(() => {
  const interval = setInterval(() => {
    // Water rises when ON, falls slowly when OFF
    setWaterLevel((w) => {
      const target = isWaterOn ? 1 : 0;
      return w + (target - w) * 0.06;
    });

    // Growth increases only when reaction is running
    setGrowth((g) => {
      if (!isReactionRunning) return g;

      // Growth speed depends on sunlight + water
      const speed = 0.0022 * sunIntensity * (0.35 + waterLevel * 0.65);
      return Math.min(1, g + speed);
    });
  }, 16);

  return () => clearInterval(interval);
}, [isReactionRunning, isWaterOn, sunIntensity, waterLevel]);



  
  // Refs for animation
  const particlesRef = useRef([]);
  const cameraRef = useRef({ x: 0, y: 0, zoom: 1, blur: 0 });
  const startTimeRef = useRef(Date.now());
  const lastTimeRef = useRef(Date.now());
  const mouseRef = useRef({ x: 0, y: 0 });

  // Initialize
  useEffect(() => {
    // Start sequence
    const sequence = async () => {
      // Atmosphere (2s)
      setPhase(PHASES.ATMOSPHERE);
      await wait(2500);
      
      // Zoom (1.5s)
      setPhase(PHASES.FOCUS_ZOOM);
      await wait(2000);
      
      // Micro World (1.5s)
      setPhase(PHASES.MICRO_WORLD);
      await wait(2000);
      
      // Ready for simulation
      setPhase(PHASES.SIMULATION);
      setIsReactionRunning(true);
      onReady?.();
    };
    
    sequence();
  }, [onReady]);

  const drawWaterPour = (ctx, time) => {
  if (!isWaterOn) return;

  // Water stream position
  const pourX = width * 0.28;
  const topY = -30;
  const bottomY = height * 0.78;

  ctx.save();
  ctx.globalCompositeOperation = 'screen';
  ctx.globalAlpha = 0.65 * (0.3 + waterLevel * 0.7);

  // Stream glow
  const streamGrad = ctx.createLinearGradient(pourX, topY, pourX, bottomY);
  streamGrad.addColorStop(0, 'rgba(125, 211, 252, 0.0)');
  streamGrad.addColorStop(0.2, 'rgba(125, 211, 252, 0.35)');
  streamGrad.addColorStop(1, 'rgba(125, 211, 252, 0.05)');

  ctx.strokeStyle = streamGrad;
  ctx.lineWidth = 10;
  ctx.lineCap = 'round';

  ctx.beginPath();
  ctx.moveTo(pourX, topY);
  ctx.lineTo(pourX + Math.sin(time * 2) * 6, bottomY);
  ctx.stroke();

  // Droplets
  for (let i = 0; i < 18; i++) {
    const t = (time * 0.7 + i * 0.12) % 1;
    const y = topY + t * (bottomY - topY);
    const x = pourX + Math.sin(time * 3 + i) * 10;

    const dropR = 2 + Math.sin(time * 4 + i) * 0.6;

    ctx.fillStyle = 'rgba(255,255,255,0.20)';
    ctx.beginPath();
    ctx.arc(x, y, dropR, 0, Math.PI * 2);
    ctx.fill();
  }

  ctx.restore();
};


  // Main loop
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    
    const animate = () => {
      const now = Date.now();
      const dt = now - lastTimeRef.current;
      lastTimeRef.current = now;
      const time = (now - startTimeRef.current) / 1000;

      // Update Phase Progress
      updateProgress(time);

      // Clear
      ctx.fillStyle = '#070A12';
      ctx.fillRect(0, 0, width, height);

      // Update Particles
      updateParticles(dt, time);

      // Camera Controls
      applyCamera(ctx);

      // Draw Layers
      drawBackground(ctx, time);
      
      // Water pour should be ABOVE background but BEFORE plant (cinematic)
if (phase === PHASES.ATMOSPHERE || phase === PHASES.FOCUS_ZOOM) {
  drawWaterPour(ctx, time);
}

// Plant environment (soil + stem + leaves growth)
if (phase === PHASES.ATMOSPHERE || (phase === PHASES.FOCUS_ZOOM && progress < 0.8)) {
  drawPlantEnvironment(ctx, time);
}
      
      if (phase !== PHASES.ATMOSPHERE) {
        drawMicroWorld(ctx, time);
      }

      ctx.restore();

      // Cinematic Post FX (vignette + grain + soft bloom)
     drawCinematicPostFX(ctx, time);

      // UI Overlays (static)
      drawUI(ctx, time);

      animationRef.current = requestAnimationFrame(animate);
    };

    animate();
    return () => cancelAnimationFrame(animationRef.current);
  }, [width, height, phase, progress, sunIntensity, isReactionRunning]);

  // Helper: wait
  const wait = (ms) => new Promise(resolve => setTimeout(resolve, ms));

  // Update logic
  const updateProgress = (time) => {
    // Generic progress per phase (can be refined)
    const t = (time % 2.5) / 2.5;
    setProgress(t);
  };

   


  const updateParticles = (dt, time) => {
    // Generate new particles if reaction is on
    if (isReactionRunning && phase === PHASES.SIMULATION) {
      // CO2 from air
      if (Math.random() < 0.1 * sunIntensity) {
        particlesRef.current.push(new Particle(
          'co2', 
          width * 0.2 + (Math.random() - 0.5) * 100, 
          -20, 
          0.2, 0.5, { size: 4 }
        ));
      }
      // H2O from xylem/bottom
      if (Math.random() < 0.1 * sunIntensity) {
        particlesRef.current.push(new Particle(
          'h2o', 
          width * 0.5 + (Math.random() - 0.5) * 20, 
          height + 20, 
          0, -0.6, { size: 3 }
        ));
      }
      // Energy from top
      if (Math.random() < 0.2 * sunIntensity) {
        particlesRef.current.push(new Particle(
          'energy', 
          width * 0.7 + (Math.random() - 0.5) * 300, 
          -50, 
          -0.3, 1.2, { size: 2 }
        ));
      }
    }

    // Update existing
    particlesRef.current.forEach(p => {
      p.update(dt, Math.sin(time) * 0.1, 0);
      
      // Absorption logic
      if (phase === PHASES.SIMULATION) {
        const targetX = width / 2;
        const targetY = height / 2;
        const dist = Math.sqrt((p.x - targetX) ** 2 + (p.y - targetY) ** 2);
        
        if (dist < 80 && !p.isAbsorbed) {
          p.isAbsorbed = true;
          // Spawn O2 bubble if it was CO2/H2O
          if (p.type === 'co2' || p.type === 'h2o') {
            if (Math.random() < 0.3) {
              setTimeout(() => {
                particlesRef.current.push(new Particle(
                  'o2', p.x, p.y, 0.1, -0.8, { size: 5 }
                ));
              }, 500);
            }
          }
        }
      }
    });

    // Cleanup dead particles
    particlesRef.current = particlesRef.current.filter(p => p.life > 0 && p.y > -100 && p.y < height + 100);
  };

  const applyCamera = (ctx) => {
    ctx.save();
    
    // Target camera states
    let target = { x: 0, y: 0, zoom: 1, blur: 0 };
    
    if (phase === PHASES.ATMOSPHERE) {
      target = { x: 0, y: 0, zoom: 0.9, blur: 0 };
    } else if (phase === PHASES.FOCUS_ZOOM) {
      const t = progress;
      target = { 
        x: width * 0.1 * t, 
        y: height * 0.1 * t, 
        zoom: 0.9 + t * 1.2, 
        blur: t * 5 
      };
    } else {
      target = { x: 0, y: 0, zoom: 1.8, blur: 0 };
    }

    // Smooth lerp
    cameraRef.current.x += (target.x - cameraRef.current.x) * 0.05;
    cameraRef.current.y += (target.y - cameraRef.current.y) * 0.05;
    cameraRef.current.zoom += (target.zoom - cameraRef.current.zoom) * 0.05;
    cameraRef.current.blur += (target.blur - cameraRef.current.blur) * 0.05;

    const cam = cameraRef.current;
    ctx.translate(width / 2, height / 2);
    ctx.scale(cam.zoom, cam.zoom);
    ctx.translate(-width / 2 + cam.x, -height / 2 + cam.y);
    
    if (cam.blur > 0.1) {
      ctx.filter = `blur(${cam.blur}px)`;
    }
  };

  const drawCinematicPostFX = (ctx, time) => {
  // Vignette
  const vignette = ctx.createRadialGradient(
    width / 2,
    height / 2,
    Math.min(width, height) * 0.35,
    width / 2,
    height / 2,
    Math.max(width, height)
  );

  vignette.addColorStop(0, 'rgba(0,0,0,0)');
  vignette.addColorStop(1, 'rgba(0,0,0,0.28)');

  ctx.save();
  ctx.fillStyle = vignette;
  ctx.fillRect(0, 0, width, height);
  ctx.restore();

  // Film grain (subtle)
  ctx.save();
  ctx.globalAlpha = 0.05;
  for (let i = 0; i < 600; i++) {
    const x = Math.random() * width;
    const y = Math.random() * height;
    ctx.fillStyle = 'rgba(255,255,255,0.25)';
    ctx.fillRect(x, y, 1, 1);
  }

};


  // Drawing Layers
  const drawBackground = (ctx, time) => {
    // Atmospheric sky
    const skyGrad = ctx.createLinearGradient(0, 0, 0, height);
    skyGrad.addColorStop(0, '#E1F5FE');
    skyGrad.addColorStop(1, '#B3E5FC');
    ctx.fillStyle = skyGrad;
    ctx.fillRect(-width, -height, width * 3, height * 3);

   

    // Cinematic Sunlight (Glow)
    const sunX = width * 0.8;
    const sunY = height * 0.15;
    const glow = ctx.createRadialGradient(sunX, sunY, 0, sunX, sunY, 300);
    glow.addColorStop(0, `rgba(255, 255, 255, ${0.4 * sunIntensity})`);
    glow.addColorStop(0.5, `rgba(255, 243, 176, ${0.15 * sunIntensity})`);
    glow.addColorStop(1, 'transparent');
    ctx.fillStyle = glow;
    ctx.fillRect(-width, -height, width * 3, height * 3);

    // Sun Rays
    ctx.save();
    ctx.translate(sunX, sunY);
    ctx.rotate(time * 0.1);
    ctx.strokeStyle = `rgba(255, 255, 255, ${0.1 * sunIntensity})`;
    ctx.lineWidth = 40;
    for (let i = 0; i < 6; i++) {
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.lineTo(1000, 0);
      ctx.stroke();
      ctx.rotate(Math.PI / 3);
    }
    ctx.restore();
  };

  const drawPlantEnvironment = (ctx, time) => {
  // -----------------------------
  // 1) Ground (dry → wet)
  // -----------------------------
  const dry = { r: 121, g: 85, b: 72 };   // #795548
  const wet = { r: 62, g: 39, b: 35 };    // darker wet soil

  const mix = (a, b, t) => Math.round(a + (b - a) * t);
  const wetT = Math.min(1, waterLevel * 0.9);

  ctx.fillStyle = `rgb(${mix(dry.r, wet.r, wetT)}, ${mix(dry.g, wet.g, wetT)}, ${mix(dry.b, wet.b, wetT)})`;
  ctx.beginPath();
  ctx.ellipse(width / 2, height + 100, width * 1.2, 300, 0, 0, Math.PI * 2);
  ctx.fill();

  // Wet sheen highlight (optional but premium)
  if (wetT > 0.05) {
    ctx.save();
    ctx.globalAlpha = 0.12 * wetT;
    ctx.fillStyle = 'rgba(255,255,255,0.35)';
    ctx.beginPath();
    ctx.ellipse(width / 2 + 40, height + 50, width * 0.55, 120, -0.1, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }

  // -----------------------------
  // 2) Stem Growth
  // -----------------------------
  const g = 0.55 + growth * 0.75;

  ctx.strokeStyle = '#2E7D32';
  ctx.lineWidth = 15 * g;
  ctx.lineCap = 'round';

  // Stem top position changes with growth
  const stemTopY = height / 2 + 60 - growth * 140;

  ctx.beginPath();
  ctx.moveTo(width / 2, height);
  ctx.quadraticCurveTo(width / 2 - 10, height / 2 + 120, width / 2, stemTopY);
  ctx.stroke();

  // -----------------------------
  // 3) Leaves scale with growth
  // -----------------------------
  const mainW = 140 + growth * 120;
  const mainH = 80 + growth * 70;

  // Main Leaf
  drawOrganicLeaf(ctx, width / 2, stemTopY - 30, mainW, mainH, -0.2, time);

  // Side Leaves
  drawOrganicLeaf(ctx, width / 2 - 70, stemTopY + 40, 80 + growth * 70, 50 + growth * 40, -0.6, time);
  drawOrganicLeaf(ctx, width / 2 + 85, stemTopY + 20, 70 + growth * 65, 45 + growth * 35, 0.4, time);
};

const drawLeafPath = (ctx, ox, oy, w, h) => {
  ctx.moveTo(ox, oy - h / 2);
  ctx.bezierCurveTo(
    ox + w / 2, oy - h / 2,
    ox + w / 2, oy + h / 2,
    ox, oy + h / 2
  );
  ctx.bezierCurveTo(
    ox - w / 2, oy + h / 2,
    ox - w / 2, oy - h / 2,
    ox, oy - h / 2
  );
};

  const drawOrganicLeaf = (ctx, x, y, w, h, rotation, time) => {
  ctx.save();
  ctx.translate(x, y);
  ctx.rotate(rotation + Math.sin(time) * 0.02); // subtle wind sway

  // Shadow
  ctx.fillStyle = 'rgba(0,0,0,0.12)';
  ctx.beginPath();
  drawLeafPath(ctx, 6, 6, w, h);
  ctx.fill();

  // Leaf Body (premium gradient)
  const grad = ctx.createLinearGradient(0, -h / 2, 0, h / 2);
  grad.addColorStop(0, 'rgba(134, 239, 172, 0.95)'); // fresh top
  grad.addColorStop(1, 'rgba(34, 197, 94, 0.95)');   // deep bottom

  ctx.fillStyle = grad;
  ctx.beginPath();
  drawLeafPath(ctx, 0, 0, w, h);
  ctx.fill();

  // Gloss highlight (cinematic)
  ctx.save();
  ctx.globalAlpha = 0.18;
  ctx.fillStyle = 'rgba(255,255,255,0.35)';
  ctx.beginPath();
  ctx.ellipse(-w * 0.12, -h * 0.12, w * 0.22, h * 0.12, -0.4, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();

  // Veins
  ctx.strokeStyle = 'rgba(15, 23, 42, 0.18)';
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(0, -h / 2);
  ctx.lineTo(0, h / 2);
  ctx.stroke();

  // Side veins
  ctx.strokeStyle = 'rgba(15, 23, 42, 0.12)';
  ctx.lineWidth = 1.5;

  for (let i = 1; i < 6; i++) {
    const vy = -h / 2 + (i * h) / 6;
    const vw = (w / 2) * (1 - Math.abs(vy) / (h / 2));

    ctx.beginPath();
    ctx.moveTo(0, vy);
    ctx.quadraticCurveTo(vw * 0.55, vy - 6, vw, vy - 12);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(0, vy);
    ctx.quadraticCurveTo(-vw * 0.55, vy - 6, -vw, vy - 12);
    ctx.stroke();
  }

  ctx.restore();
};


  const drawMicroWorld = (ctx, time) => {
    const opacity = (phase === PHASES.FOCUS_ZOOM) ? (progress > 0.6 ? (progress - 0.6) / 0.4 : 0) : 1;
    ctx.globalAlpha = opacity;

    const cx = width / 2;
    const cy = height / 2;

    // Organic Tissue Silhouette (THE RECTANGLE REPLACEMENT)
    ctx.save();
    ctx.translate(cx, cy);
    
    // Multiple layers for organic depth
    for (let layer = 0; layer < 3; layer++) {
      const lScale = 1 - layer * 0.1;
      const lAlpha = 0.8 - layer * 0.2;
      const tissueGrad = ctx.createRadialGradient(0, -40, 20, 0, 0, 280);
       tissueGrad.addColorStop(0, `rgba(220, 252, 231, ${0.55 * lAlpha})`);
      tissueGrad.addColorStop(0.45, `rgba(134, 239, 172, ${0.35 * lAlpha})`);
      tissueGrad.addColorStop(1, `rgba(34, 197, 94, ${0.12 * lAlpha})`);
      ctx.fillStyle = tissueGrad;

      
      ctx.beginPath();
      const segments = 24;
      for (let i = 0; i < segments; i++) {
        const angle = (i / segments) * Math.PI * 2;
        const dist = (180 + Math.sin(angle * 4 + time + layer) * 10) * lScale;
        const tx = Math.cos(angle) * dist;
        const ty = Math.sin(angle) * dist * 0.6;
        if (i === 0) ctx.moveTo(tx, ty);
        else ctx.lineTo(tx, ty);
      }
      ctx.closePath();
      ctx.fill();
      
      // Membrane outline
      ctx.strokeStyle = `rgba(255, 255, 255, ${0.08})`;
     ctx.lineWidth = 2;
     ctx.stroke();

    }

    // Mesophyll Cells (Circular blobs)
    for (let i = 0; i < 8; i++) {
      const angle = (i / 8) * Math.PI * 2;
      const dist = 100;
      const bx = Math.cos(angle) * dist;
      const by = Math.sin(angle) * dist * 0.5;
      
      drawCell(ctx, bx, by, time + i);
    }

    // Main Reaction Center
    drawReactionCenter(ctx, 0, 0, time);

    ctx.restore();

    // Draw active particles
    particlesRef.current.forEach(p => p.draw(ctx));

    ctx.globalAlpha = 1;
  };

  const drawCell = (ctx, x, y, time) => {
    ctx.save();
    ctx.translate(x, y);
    
    // Cell Body
    ctx.fillStyle = 'rgba(76, 175, 80, 0.4)';
    ctx.beginPath();
    ctx.ellipse(0, 0, 30, 20, Math.sin(time) * 0.1, 0, Math.PI * 2);
    ctx.fill();
    
    // Chloroplasts inside cell
    ctx.fillStyle = '#1B5E20';
    for (let i = 0; i < 4; i++) {
      const cx = Math.sin(time + i) * 10;
      const cy = Math.cos(time * 0.8 + i) * 8;
      ctx.beginPath();
      ctx.ellipse(cx, cy, 6, 4, i, 0, Math.PI * 2);
      ctx.fill();
    }
    
    ctx.restore();
  };

  const drawReactionCenter = (ctx, x, y, time) => {
    // Large central chloroplast for simulation focus
    ctx.save();
    ctx.translate(x, y);
    
    const pulse = 1 + Math.sin(time * 3) * 0.05 * sunIntensity;
    
    // Glow
    const glow = ctx.createRadialGradient(0, 0, 0, 0, 0, 100);
    glow.addColorStop(0, `rgba(165, 214, 167, ${0.4 * sunIntensity})`);
    glow.addColorStop(1, 'transparent');
    ctx.fillStyle = glow;
    ctx.beginPath(); ctx.arc(0, 0, 100 * pulse, 0, Math.PI * 2); ctx.fill();

    // Chloroplast Body
    const cpGrad = ctx.createRadialGradient(-20, -10, 0, 0, 0, 70);
    cpGrad.addColorStop(0, '#A5D6A7');
    cpGrad.addColorStop(1, '#2E7D32');
    ctx.fillStyle = cpGrad;
    ctx.beginPath();
    ctx.ellipse(0, 0, 70 * pulse, 45 * pulse, 0.1, 0, Math.PI * 2);
    ctx.fill();
    
    // Double Membrane
    ctx.strokeStyle = '#1B5E20';
    ctx.lineWidth = 3;
    ctx.stroke();

    // Thylakoids (Grana)
    ctx.fillStyle = '#1B5E20';
    for (let i = -2; i <= 2; i++) {
      for (let j = -2; j <= 2; j++) {
        if (Math.abs(i) + Math.abs(j) > 3) continue;
        const tx = i * 20 + Math.sin(time + j) * 2;
        const ty = j * 12 + Math.cos(time * 0.7 + i) * 2;
        
        // Glow thylakoids
        if (isReactionRunning) {
          ctx.shadowBlur = 10;
          ctx.shadowColor = `rgba(129, 199, 132, ${sunIntensity})`;
        }
        
        ctx.beginPath();
        ctx.roundRect(tx - 6, ty - 2, 12, 4, 1);
        ctx.fill();
        ctx.shadowBlur = 0;
      }
    }

    ctx.restore();
  };

  const drawUI = (ctx, time) => {
    if (phase === PHASES.SIMULATION) {
      // Equation (minimal and premium)
      ctx.fillStyle = 'rgba(30, 41, 59, 0.8)';
      ctx.font = '600 14px Inter, sans-serif';
      ctx.textAlign = 'center';
      
      const text = "6CO₂ + 6H₂O + Light → C₆H₁₂O₆ + 6O₂";
      const metrics = ctx.measureText(text);
      
      ctx.fillStyle = 'rgba(255,255,255,0.9)';
      ctx.beginPath();
      ctx.roundRect(width/2 - metrics.width/2 - 20, height - 60, metrics.width + 40, 40, 20);
      ctx.fill();
      
      ctx.fillStyle = '#1e293b';
      ctx.fillText(text, width/2, height - 35);
    }
    
    // Cinematic labels
    if (phase === PHASES.ATMOSPHERE) {
      ctx.fillStyle = 'rgba(30, 41, 59, 0.6)';
      ctx.font = '300 18px Inter, sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText("Observing the living plant in nature...", width/2, height - 100);
    } else if (phase === PHASES.FOCUS_ZOOM) {
      ctx.fillStyle = 'rgba(30, 41, 59, 0.6)';
      ctx.font = '300 18px Inter, sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText("Zooming into leaf tissue...", width/2, height - 100);
    }
  };

  return (
  <div className="relative w-full h-full bg-[#070A12] overflow-hidden rounded-2xl border border-white/10 shadow-[0_30px_120px_rgba(0,0,0,0.45)]">
    <canvas
      ref={canvasRef}
      width={width}
      height={height}
      style={{ width: '100%', height: '100%' }}
    />

    {/* 🎬 Cinematic HUD Overlay (Premium UI) */}
    {showHUD && (
      <div className="pointer-events-none absolute inset-0">
        
        {/* Top-left: System HUD */}
        <div className="pointer-events-auto absolute top-4 left-4">
          <div className="rounded-2xl border border-white/10 bg-black/35 backdrop-blur-xl shadow-[0_20px_70px_rgba(0,0,0,0.35)] px-4 py-3 min-w-[280px]">
            
            <div className="flex items-center justify-between">
              <div className="text-[10px] uppercase tracking-[0.22em] text-white/55">
                Photosynthesis
              </div>

              <div
                className={`text-[10px] font-semibold px-2 py-1 rounded-full border ${
                  isReactionRunning
                    ? "text-emerald-200 border-emerald-300/20 bg-emerald-400/10"
                    : "text-slate-200 border-white/10 bg-white/5"
                }`}
              >
                {isReactionRunning ? "LIVE" : "PAUSED"}
              </div>
            </div>

            {/* Divider */}
            <div className="mt-3 h-px w-full bg-white/10" />

            {/* Sunlight Control */}
            <div className="mt-3">
              <div className="flex items-center justify-between">
                <div className="text-[11px] text-white/70 font-medium">
                  ☀️ Sunlight
                </div>
                <div className="text-[11px] text-white/80 font-semibold tabular-nums">
                  {Math.round(sunIntensity * 100)}%
                </div>
              </div>

              <div className="mt-2">
                <input
                  type="range"
                  min="0.2"
                  max="1.5"
                  step="0.05"
                  value={sunIntensity}
                  onChange={(e) => setSunIntensity(parseFloat(e.target.value))}
                  className="w-full h-1.5 rounded-lg appearance-none cursor-pointer accent-amber-300"
                />
              </div>

              {/* Micro indicators */}
              <div className="mt-3 grid grid-cols-3 gap-2">
                <div className="rounded-xl border border-white/10 bg-white/5 px-2 py-2">
                  <div className="text-[10px] text-white/45 uppercase tracking-wider">
                    CO₂
                  </div>
                  <div className="text-[12px] text-white/80 font-semibold">
                    Intake
                  </div>
                </div>

                <div className="rounded-xl border border-white/10 bg-white/5 px-2 py-2">
                  <div className="text-[10px] text-white/45 uppercase tracking-wider">
                    H₂O
                  </div>
                  <div className="text-[12px] text-white/80 font-semibold">
                    Flow
                  </div>
                </div>

                <div className="rounded-xl border border-white/10 bg-white/5 px-2 py-2">
                  <div className="text-[10px] text-white/45 uppercase tracking-wider">
                    O₂
                  </div>
                  <div className="text-[12px] text-white/80 font-semibold">
                    Output
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Top-right: Quick Controls */}
        <div className="pointer-events-auto absolute top-4 right-4 flex items-center gap-2">
          <button
            onClick={() => setIsReactionRunning((v) => !v)}
            className="px-3 py-2 rounded-2xl border border-white/10 bg-black/30 backdrop-blur-xl text-white/80 text-xs font-semibold hover:bg-black/45 transition"
          >
            {isReactionRunning ? "Pause" : "Play"}
          </button>

          <button
            onClick={() => setSunIntensity(0.8)}
            className="px-3 py-2 rounded-2xl border border-white/10 bg-black/30 backdrop-blur-xl text-white/80 text-xs font-semibold hover:bg-black/45 transition"
          >
            Reset Light
          </button>

          <button
            onClick={() => setShowHUD(false)}
            className="px-3 py-2 rounded-2xl border border-white/10 bg-black/30 backdrop-blur-xl text-white/80 text-xs font-semibold hover:bg-black/45 transition"
          >
            Hide UI
          </button>
        </div>

        {/* Bottom-center: Cinematic Subtitle */}
        <div className="pointer-events-none absolute bottom-5 left-1/2 -translate-x-1/2">
          <div className="rounded-full border border-white/10 bg-black/30 backdrop-blur-xl px-5 py-2 shadow-[0_20px_60px_rgba(0,0,0,0.35)]">
            <p className="text-xs text-white/75 tracking-wide">
              {phase === PHASES.ATMOSPHERE &&
                "A plant waits for light to begin converting energy into life."}
              {phase === PHASES.FOCUS_ZOOM &&
                "Zooming into the leaf surface — gas exchange begins here."}
              {phase === PHASES.MICRO_WORLD &&
                "Inside the tissue, chloroplasts prepare the reaction engine."}
              {phase === PHASES.SIMULATION &&
                "Adjust sunlight to change the reaction speed in real-time."}
            </p>
          </div>
        </div>

        {/* Bottom-right: Tiny Hint */}
        <div className="pointer-events-none absolute bottom-5 right-5">
          <div className="text-[11px] text-white/40 italic">
            Powered by Netra Visual Engine
          </div>
        </div>
      </div>
    )}

    {/* If HUD is hidden, show a tiny button to restore */}
    {!showHUD && (
      <div className="pointer-events-auto absolute top-4 right-4">
        <button
          onClick={() => setShowHUD(true)}
          className="px-3 py-2 rounded-2xl border border-white/10 bg-black/30 backdrop-blur-xl text-white/80 text-xs font-semibold hover:bg-black/45 transition"
        >
          Show UI
        </button>
      </div>
    )}
  </div>
);}
