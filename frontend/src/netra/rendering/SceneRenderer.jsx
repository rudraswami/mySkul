/**
 * 🎬 SCENE RENDERER
 * ==================
 * 
 * Renders SceneObjects as rich visual scenes, NOT boxes.
 * 
 * This renderer:
 * - Takes SceneObjects from SceneObjectResolver
 * - Uses spatial rules for intelligent positioning
 * - Renders using ScenePrimitives (not GenericShape!)
 * - Creates animated, teaching-friendly visuals
 * 
 * PRINCIPLE: Every render creates a scene, not a diagram.
 */

import React, { useMemo, useRef, useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  OBJECT_TYPES,
  VISUAL_FORMS,
  SPATIAL_RULES,
} from '../reasoning/SceneObjectResolver';
import {
  OutdoorEnvironment,
  LabEnvironment,
  RoomEnvironment,
  GroundSurface,
  IceSurface,
  CarpetSurface,
  MicroscopicSurface,
  SlidingBlock,
  RollingBall,
  PersonFigure,
  CarFigure,
  ForceArrow,
  MotionTrail,
  ChaosScatter,
  SceneDivider,
  SceneLabel,
  getScenePrimitive,
} from '../primitives/ScenePrimitives';

// ============================================
// LAYOUT CALCULATOR
// ============================================

/**
 * Calculate positions based on spatial rules
 */
class SceneLayoutCalculator {
  constructor(width, height) {
    this.width = width;
    this.height = height;
    this.positions = new Map();  // id → {x, y, width, height}
    // Ground level at 70% down - leaves room for sky and ground
    this.groundY = height * 0.70;
  }
  
  /**
   * Calculate positions for all scene objects
   */
  calculate(sceneObjects) {
    console.log('🎬 [Layout] Calculating positions for', sceneObjects.length, 'objects');
    console.log('🎬 [Layout] Canvas:', this.width, 'x', this.height, '| groundY:', this.groundY);
    
    // First pass: position environments and surfaces
    const environments = sceneObjects.filter(o => o.objectType === OBJECT_TYPES.ENVIRONMENT);
    const surfaces = sceneObjects.filter(o => o.objectType === OBJECT_TYPES.SURFACE);
    const actors = sceneObjects.filter(o => o.objectType === OBJECT_TYPES.ACTOR);
    const forces = sceneObjects.filter(o => o.objectType === OBJECT_TYPES.FORCE);
    const effects = sceneObjects.filter(o => o.objectType === OBJECT_TYPES.EFFECT);
    const labels = sceneObjects.filter(o => o.objectType === OBJECT_TYPES.LABEL);
    const others = sceneObjects.filter(o => 
      !environments.includes(o) && 
      !surfaces.includes(o) && 
      !actors.includes(o) && 
      !forces.includes(o) &&
      !effects.includes(o) &&
      !labels.includes(o)
    );
    
    console.log('🎬 [Layout] Found:', {
      environments: environments.length,
      surfaces: surfaces.length,
      actors: actors.length,
      forces: forces.length,
      effects: effects.length,
      labels: labels.length,
    });
    
    // Position environments (full canvas)
    environments.forEach(env => {
      this.positions.set(env.id, {
        x: 0,
        y: 0,
        width: this.width,
        height: this.height,
      });
    });
    
    // Position surfaces
    this.positionSurfaces(surfaces);
    
    // Position actors PROMINENTLY
    this.positionActors(actors, surfaces);
    
    // Position forces relative to actors
    this.positionForces(forces, actors);
    
    // Position effects
    this.positionEffects(effects, actors, surfaces);
    
    // Position labels
    this.positionLabels(labels);
    
    // Position remaining objects
    this.positionOthers(others);
    
    return this.positions;
  }
  
  positionSurfaces(surfaces) {
    const hasSplitView = surfaces.some(s => 
      s.spatialRules.some(r => r.rule === SPATIAL_RULES.LEFT_OF || r.rule === SPATIAL_RULES.RIGHT_OF)
    );
    
    if (hasSplitView) {
      // Split view - two surfaces side by side
      const leftSurface = surfaces.find(s => s.spatialRules.some(r => r.rule === SPATIAL_RULES.LEFT_OF));
      const rightSurface = surfaces.find(s => s.spatialRules.some(r => r.rule === SPATIAL_RULES.RIGHT_OF));
      
      if (leftSurface) {
        this.positions.set(leftSurface.id, {
          x: 0,
          y: this.groundY,
          width: this.width / 2 - 20,
          height: this.height - this.groundY,  // Fill to bottom
        });
      }
      if (rightSurface) {
        this.positions.set(rightSurface.id, {
          x: this.width / 2 + 20,
          y: this.groundY,
          width: this.width / 2 - 20,
          height: this.height - this.groundY,
        });
      }
    } else {
      // Single surface spans width
      surfaces.forEach((surface, index) => {
        const isMicroscopic = surface.visualForm === VISUAL_FORMS.MICROSCOPIC_BUMPS;
        
        const pos = {
          x: isMicroscopic ? 50 : 0,
          y: isMicroscopic ? this.height * 0.4 : this.groundY,
          width: isMicroscopic ? this.width - 100 : this.width,
          height: isMicroscopic ? 200 : this.height - this.groundY,  // Fill to bottom
        };
        
        this.positions.set(surface.id, pos);
        console.log('🎬 [Layout] Surface', surface.id, ':', pos);
      });
    }
  }
  
  positionActors(actors, surfaces) {
    const hasSplitView = surfaces.some(s => 
      s.spatialRules.some(r => r.rule === SPATIAL_RULES.LEFT_OF || r.rule === SPATIAL_RULES.RIGHT_OF)
    );
    
    // Actor dimensions - make them PROMINENT
    const actorWidth = 100;
    const actorHeight = 70;
    
    if (hasSplitView && actors.length >= 2) {
      // Split view - actors on each side
      actors.forEach((actor, index) => {
        const side = index % 2 === 0 ? 'left' : 'right';
        const baseX = side === 'left' ? this.width * 0.25 : this.width * 0.75;
        
        const pos = {
          x: baseX - actorWidth / 2,
          y: this.groundY - actorHeight,
          width: actorWidth,
          height: actorHeight,
        };
        
        this.positions.set(actor.id, pos);
        console.log('🎬 [Layout] Actor', actor.id, '(split):', pos);
      });
    } else {
      // Single scene - position actor(s) centrally on surface
      actors.forEach((actor, index) => {
        // Center the actor horizontally, positioned ON the ground
        const x = this.width / 2 - actorWidth / 2 + (index * 120);
        
        const pos = {
          x,
          y: this.groundY - actorHeight,  // Sit on top of ground
          width: actorWidth,
          height: actorHeight,
        };
        
        this.positions.set(actor.id, pos);
        console.log('🎬 [Layout] Actor', actor.id, ':', pos, '| visualForm:', actor.visualForm);
      });
    }
  }
  
  positionLabels(labels) {
    labels.forEach(label => {
      const position = label.renderHints?.position || 'top-right';
      
      let pos;
      switch (position) {
        case 'top-right':
          pos = { x: this.width - 80, y: 30 };
          break;
        case 'top-left':
          pos = { x: 20, y: 30 };
          break;
        case 'center':
          pos = { x: this.width / 2, y: 30 };
          break;
        default:
          pos = { x: this.width - 80, y: 30 };
      }
      
      this.positions.set(label.id, pos);
    });
  }
  
  positionForces(forces, actors) {
    forces.forEach(force => {
      // Find related actor
      const relatedRule = force.spatialRules.find(r => r.rule === SPATIAL_RULES.ORIGINATES_FROM || r.rule === SPATIAL_RULES.ATTACHED_TO);
      const relatedId = relatedRule?.relatedTo;
      
      let actorPos = relatedId && this.positions.get(relatedId);
      
      if (!actorPos && actors.length > 0) {
        // Default to first actor
        actorPos = this.positions.get(actors[0].id);
      }
      
      // If still no actor, create a default position
      if (!actorPos) {
        actorPos = {
          x: this.width / 2 - 50,
          y: this.groundY - 70,
          width: 100,
          height: 70,
        };
      }
      
      // Position force at center of actor
      const centerX = actorPos.x + actorPos.width / 2;
      const centerY = actorPos.y + actorPos.height / 2;
      
      // Determine direction and offset based on force variant
      const variant = force.properties?.variant || force.renderHints?.variant;
      const magnitude = force.properties?.magnitude || 70;
      let angle = 0;
      let offsetX = 0;
      let offsetY = 0;
      
      switch (variant) {
        case 'gravitational':
          angle = 90;  // Down
          offsetY = 5;
          break;
        case 'normal':
          angle = -90;  // Up
          offsetY = -5;
          break;
        case 'friction':
          angle = 180;  // Left (opposite motion)
          offsetX = -5;
          break;
        case 'applied':
          angle = 0;  // Right
          offsetX = 5;
          break;
        default:
          angle = 0;
      }
      
      const pos = {
        x: centerX + offsetX,
        y: centerY + offsetY,
        angle,
        length: magnitude,
      };
      
      this.positions.set(force.id, pos);
      console.log('🎬 [Layout] Force', force.id, ':', pos, '| variant:', variant);
    });
  }
  
  positionEffects(effects, actors, surfaces) {
    effects.forEach(effect => {
      const isRightSide = effect.spatialRules.some(r => r.rule === SPATIAL_RULES.RIGHT_OF);
      
      if (effect.visualForm === VISUAL_FORMS.CHAOS_SCATTER || effect.visualForm === 'CHAOS_SCATTER') {
        this.positions.set(effect.id, {
          x: isRightSide ? this.width * 0.75 : this.width * 0.5,
          y: this.height * 0.5,
          radius: 100,
        });
      } else {
        // Motion trail - attach to actor
        const firstActor = actors[0];
        const actorPos = firstActor && this.positions.get(firstActor.id);
        
        if (actorPos) {
          this.positions.set(effect.id, {
            x: actorPos.x - 10,
            y: actorPos.y + actorPos.height / 2,
            length: 60,
          });
        }
      }
    });
  }
  
  positionOthers(others) {
    others.forEach((obj, index) => {
      if (obj.objectType === OBJECT_TYPES.INDICATOR && obj.visualForm === 'VS_DIVIDER') {
        this.positions.set(obj.id, {
          x: this.width / 2,
          y: 0,
          height: this.height,
        });
      } else if (obj.objectType === OBJECT_TYPES.LABEL) {
        this.positions.set(obj.id, {
          x: this.width / 2,
          y: 40 + index * 30,
        });
      }
    });
  }
}

// ============================================
// SCENE OBJECT RENDERER
// ============================================

const SceneObjectRenderer = ({ sceneObject, position, domain }) => {
  const { objectType, visualForm, renderHints, label, properties } = sceneObject;
  
  // Get position data
  const { x = 0, y = 0, width = 100, height = 60, angle = 0, length = 80, radius = 100 } = position || {};
  
  // Render based on object type and visual form
  switch (objectType) {
    // ============ ENVIRONMENTS ============
    case OBJECT_TYPES.ENVIRONMENT:
      return renderEnvironment(visualForm, width, height, renderHints);
    
    // ============ SURFACES ============
    case OBJECT_TYPES.SURFACE:
      return renderSurface(visualForm, x, y, width, height, renderHints, sceneObject.animationDelay);
    
    // ============ ACTORS ============
    case OBJECT_TYPES.ACTOR:
      return renderActor(visualForm, x, y, width, height, label, renderHints, sceneObject.animationDelay);
    
    // ============ FORCES ============
    case OBJECT_TYPES.FORCE:
      return renderForce(visualForm, x, y, length, angle, label, properties, renderHints, sceneObject.animationDelay);
    
    // ============ EFFECTS ============
    case OBJECT_TYPES.EFFECT:
      return renderEffect(visualForm, x, y, radius, length, renderHints, sceneObject.animationDelay);
    
    // ============ INDICATORS ============
    case OBJECT_TYPES.INDICATOR:
      if (visualForm === 'VS_DIVIDER') {
        return <SceneDivider x={x} height={height} delay={sceneObject.animationDelay} />;
      }
      return null;
    
    // ============ LABELS ============
    case OBJECT_TYPES.LABEL:
      return <SceneLabel x={x} y={y} text={label} delay={sceneObject.animationDelay} />;
    
    default:
      console.warn(`Unknown object type: ${objectType}`);
      return null;
  }
};

// ============================================
// RENDER HELPERS
// ============================================

function renderEnvironment(visualForm, width, height, renderHints) {
  switch (visualForm) {
    case VISUAL_FORMS.OUTDOOR_SCENE:
    case 'OUTDOOR_SCENE':
      return <OutdoorEnvironment width={width} height={height} />;
    
    case VISUAL_FORMS.LAB_BACKGROUND:
    case 'LAB_BACKGROUND':
      return <LabEnvironment width={width} height={height} />;
    
    case VISUAL_FORMS.ROOM_INTERIOR:
    case 'ROOM_INTERIOR':
      return <RoomEnvironment width={width} height={height} />;
    
    default:
      return <OutdoorEnvironment width={width} height={height} />;
  }
}

function renderSurface(visualForm, x, y, width, height, renderHints, delay) {
  // Pass height for proper ground filling
  const surfaceHeight = height || 200;
  
  switch (visualForm) {
    case VISUAL_FORMS.FLAT_GROUND:
    case VISUAL_FORMS.ROUGH_SURFACE:
    case 'FLAT_GROUND':
    case 'ROUGH_SURFACE':
      return <GroundSurface y={y} width={width} height={surfaceHeight} variant="rough" delay={delay} />;
    
    case VISUAL_FORMS.SMOOTH_ICE:
    case 'SMOOTH_ICE':
      return <IceSurface y={y} width={width} delay={delay} />;
    
    case VISUAL_FORMS.CARPET_TEXTURE:
    case 'CARPET_TEXTURE':
      return <CarpetSurface y={y} width={width} delay={delay} />;
    
    case VISUAL_FORMS.MICROSCOPIC_BUMPS:
    case 'MICROSCOPIC_BUMPS':
      return <MicroscopicSurface y={y} width={width} delay={delay} />;
    
    default:
      return <GroundSurface y={y} width={width} height={surfaceHeight} delay={delay} />;
  }
}

function renderActor(visualForm, x, y, width, height, label, renderHints, delay) {
  const moving = renderHints?.animated;
  
  switch (visualForm) {
    case VISUAL_FORMS.SLIDING_BLOCK:
    case 'SLIDING_BLOCK':
      return (
        <SlidingBlock 
          x={x} 
          y={y} 
          width={width} 
          height={height} 
          label={label} 
          moving={moving}
          delay={delay}
        />
      );
    
    case VISUAL_FORMS.ROLLING_BALL:
    case 'ROLLING_BALL':
      return (
        <RollingBall 
          x={x + width / 2} 
          y={y + height / 2} 
          radius={Math.min(width, height) / 2}
          rolling={moving}
          delay={delay}
        />
      );
    
    case VISUAL_FORMS.PERSON_WALKING:
    case 'PERSON_WALKING':
      return (
        <PersonFigure 
          x={x + width / 2} 
          y={y + height} 
          action="walking"
          delay={delay}
        />
      );
    
    case VISUAL_FORMS.PERSON_SLIDING:
    case 'PERSON_SLIDING':
      return (
        <PersonFigure 
          x={x + width / 2} 
          y={y + height} 
          action="sliding"
          delay={delay}
        />
      );
    
    case VISUAL_FORMS.CAR_MOVING:
    case 'CAR_MOVING':
      return (
        <CarFigure 
          x={x} 
          y={y + height - 20} 
          moving={moving}
          delay={delay}
        />
      );
    
    default:
      // Default to sliding block
      return (
        <SlidingBlock 
          x={x} 
          y={y} 
          width={width} 
          height={height} 
          label={label}
          delay={delay}
        />
      );
  }
}

function renderForce(visualForm, x, y, length, angle, label, properties, renderHints, delay) {
  const variant = properties?.variant || renderHints?.variant || 'applied';
  
  return (
    <ForceArrow 
      x={x}
      y={y}
      length={length}
      angle={angle}
      variant={variant}
      label={label}
      delay={delay}
    />
  );
}

function renderEffect(visualForm, x, y, radius, length, renderHints, delay) {
  switch (visualForm) {
    case VISUAL_FORMS.CHAOS_SCATTER:
    case 'CHAOS_SCATTER':
      return (
        <ChaosScatter 
          centerX={x} 
          centerY={y} 
          radius={radius}
          delay={delay}
        />
      );
    
    case VISUAL_FORMS.MOTION_TRAIL:
    case 'MOTION_TRAIL':
      return (
        <MotionTrail 
          startX={x} 
          startY={y} 
          length={length}
          delay={delay}
        />
      );
    
    default:
      return null;
  }
}

// ============================================
// SVG FILTERS
// ============================================

const SceneFilters = () => (
  <defs>
    {/* Glow effect for sun/highlights */}
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="4" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
    
    {/* Drop shadow */}
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="2" dy="2" stdDeviation="3" floodOpacity="0.2" />
    </filter>
    
    {/* Sketch texture */}
    <filter id="sketch" x="-5%" y="-5%" width="110%" height="110%">
      <feTurbulence type="fractalNoise" baseFrequency="0.02" numOctaves="3" result="noise" />
      <feDisplacementMap in="SourceGraphic" in2="noise" scale="1" xChannelSelector="R" yChannelSelector="G" />
    </filter>
  </defs>
);

// ============================================
// MAIN SCENE RENDERER
// ============================================

const SceneRenderer = ({
  sceneObjects = [],
  width = 800,
  height = 600,
  domain = 'physics',
  showLabels = true,
  className = '',
  style = {},
  onRenderComplete = null,
}) => {
  const svgRef = useRef(null);
  const [isRendered, setIsRendered] = useState(false);
  
  // Calculate positions for all scene objects
  const { positions, sortedObjects } = useMemo(() => {
    if (!sceneObjects || sceneObjects.length === 0) {
      return { positions: new Map(), sortedObjects: [] };
    }
    
    const calculator = new SceneLayoutCalculator(width, height);
    const positions = calculator.calculate(sceneObjects);
    
    // Sort by draw order
    const sortedObjects = [...sceneObjects].sort((a, b) => 
      (a.drawOrder || 0) - (b.drawOrder || 0)
    );
    
    console.log('🎬 [SceneRenderer] Calculated positions for', sortedObjects.length, 'objects');
    
    return { positions, sortedObjects };
  }, [sceneObjects, width, height]);
  
  // Handle render complete
  useEffect(() => {
    if (sortedObjects.length > 0 && !isRendered) {
      const maxDelay = Math.max(...sortedObjects.map(o => o.animationDelay || 0));
      
      const timer = setTimeout(() => {
        setIsRendered(true);
        onRenderComplete?.();
      }, (maxDelay + 1) * 1000);
      
      return () => clearTimeout(timer);
    }
  }, [sortedObjects, isRendered, onRenderComplete]);
  
  // Empty state
  if (!sortedObjects || sortedObjects.length === 0) {
    return (
      <div 
        className={`scene-renderer empty ${className}`}
        style={{ width, height, ...style }}
      >
        <svg width="100%" height="100%" viewBox={`0 0 ${width} ${height}`}>
          <rect x={0} y={0} width={width} height={height} fill="#F8FAFC" />
          <text
            x={width / 2}
            y={height / 2}
            textAnchor="middle"
            fill="#94A3B8"
            fontSize={16}
            fontFamily="system-ui, sans-serif"
          >
            Preparing visual scene...
          </text>
        </svg>
      </div>
    );
  }
  
  return (
    <div
      className={`scene-renderer ${className}`}
      style={{ width, height, position: 'relative', ...style }}
    >
      <svg
        ref={svgRef}
        width="100%"
        height="100%"
        viewBox={`0 0 ${width} ${height}`}
        preserveAspectRatio="xMidYMid meet"
        style={{ background: '#F8FAFC' }}
      >
        {/* SVG Filters */}
        <SceneFilters />
        
        {/* Render all scene objects in draw order */}
        <AnimatePresence>
          {sortedObjects.map(sceneObject => (
            <SceneObjectRenderer
              key={sceneObject.id}
              sceneObject={sceneObject}
              position={positions.get(sceneObject.id)}
              domain={domain}
            />
          ))}
        </AnimatePresence>
        
        {/* Topic title (if available from first label) */}
        {showLabels && sortedObjects.some(o => o.objectType === OBJECT_TYPES.LABEL) && (
          <motion.g
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            {/* Title is rendered via SceneObjectRenderer */}
          </motion.g>
        )}
      </svg>
      
      {/* Debug badge (dev mode) */}
      {process.env.NODE_ENV === 'development' && (
        <div
          style={{
            position: 'absolute',
            bottom: 8,
            right: 8,
            background: 'rgba(0,0,0,0.7)',
            color: 'white',
            padding: '4px 10px',
            borderRadius: 4,
            fontSize: 10,
            fontFamily: 'monospace',
          }}
        >
          SceneRenderer | {sortedObjects.length} objects
        </div>
      )}
    </div>
  );
};

export default SceneRenderer;
export { SceneRenderer, SceneLayoutCalculator };
