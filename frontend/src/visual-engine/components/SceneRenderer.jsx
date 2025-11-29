/**
 * SceneRenderer - SVG-based Scene Drawing Component
 * Renders backgrounds, props, actors, vectors, and labels
 */

import React, { useMemo } from 'react';
import { motion } from 'framer-motion';
import BackgroundLayer from './BackgroundLayer';
import PropsLayer from './PropsLayer';
import ActorLayer from './ActorLayer';
import VectorArrow from './VectorArrow';
import LabelsLayer from './LabelsLayer';

const SceneRenderer = ({
  config,
  animState,
  timeline,
  language,
  onTap,
  onLongPress,
  onSwipe,
  activeLabel,
  showFormula,
}) => {
  const viewBox = `0 0 ${config.viewport?.width || 640} ${config.viewport?.height || 360}`;

  // Calculate prop positions based on animation state
  const animatedProps = useMemo(() => {
    if (!animState?.activeAnimations?.length) return config.props;

    return config.props.map(prop => {
      const anim = animState.activeAnimations.find(a => a.target === prop.id);
      if (!anim) return prop;

      const values = timeline.calculateValues(anim);
      if (!values) return prop;

      return {
        ...prop,
        animatedPosition: {
          x: (prop.position?.x || 0.5) + (values.x || 0) / (config.viewport?.width || 640),
          y: (prop.position?.y || 0.5) + (values.y || 0) / (config.viewport?.height || 360),
        },
        animatedRotation: values.rotation || 0,
        animatedScale: values.scale || 1,
      };
    });
  }, [config.props, animState, timeline, config.viewport]);

  // Calculate vector arrows
  const vectors = useMemo(() => {
    if (!animState?.activeAnimations?.length) return [];

    return animState.activeAnimations
      .filter(a => a.type === 'vector_grow')
      .map(anim => {
        const values = timeline.calculateValues(anim);
        return {
          id: anim.id,
          ...values,
          target: anim.target,
        };
      });
  }, [animState, timeline]);

  // Handle touch/click interactions
  const handleClick = (e) => {
    const svg = e.currentTarget;
    const rect = svg.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width;
    const y = (e.clientY - rect.top) / rect.height;

    // Check if click is on a prop
    const clickedProp = animatedProps.find(prop => {
      const px = prop.animatedPosition?.x || prop.position?.x || 0.5;
      const py = prop.animatedPosition?.y || prop.position?.y || 0.5;
      const tolerance = 0.1;
      return Math.abs(px - x) < tolerance && Math.abs(py - y) < tolerance;
    });

    if (clickedProp) {
      onTap?.(clickedProp.id, { x, y });
    } else {
      onTap?.('background', { x, y });
    }
  };

  let pressTimer;
  const handleTouchStart = (e) => {
    pressTimer = setTimeout(() => {
      const touch = e.touches[0];
      onLongPress?.('scene');
    }, 500);
  };

  const handleTouchEnd = () => {
    clearTimeout(pressTimer);
  };

  return (
    <motion.svg
      viewBox={viewBox}
      className="w-full h-auto cursor-pointer"
      style={{ minHeight: '300px', maxHeight: '500px' }}
      onClick={handleClick}
      onTouchStart={handleTouchStart}
      onTouchEnd={handleTouchEnd}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      {/* Definitions */}
      <defs>
        {/* Gradients */}
        <linearGradient id="sky-gradient" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor={config.scene?.gradient?.[0] || '#87CEEB'} />
          <stop offset="100%" stopColor={config.scene?.gradient?.[1] || '#E0F7FA'} />
        </linearGradient>
        
        <linearGradient id="ground-gradient" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="#8BC34A" />
          <stop offset="100%" stopColor="#558B2F" />
        </linearGradient>

        {/* Arrow markers */}
        <marker id="arrow-orange" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto">
          <path d="M 0 0 L 12 6 L 0 12 L 3 6 Z" fill="#FF9800" />
        </marker>
        
        <marker id="arrow-green" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto">
          <path d="M 0 0 L 12 6 L 0 12 L 3 6 Z" fill="#4CAF50" />
        </marker>

        {/* Glow filter */}
        <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation="3" result="blur" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>

        {/* Shadow filter */}
        <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
          <feDropShadow dx="2" dy="4" stdDeviation="3" floodOpacity="0.3" />
        </filter>
      </defs>

      {/* Background Layer */}
      <BackgroundLayer 
        sceneType={config.scene?.background} 
        width={config.viewport?.width || 640}
        height={config.viewport?.height || 360}
        groundLevel={config.scene?.groundLevel || 0.75}
      />

      {/* Props Layer */}
      <PropsLayer
        props={animatedProps}
        width={config.viewport?.width || 640}
        height={config.viewport?.height || 360}
        onPropClick={(propId) => onTap?.(propId)}
      />

      {/* Actor Layer (Professor) */}
      <ActorLayer
        actors={config.actors}
        animState={animState}
        width={config.viewport?.width || 640}
        height={config.viewport?.height || 360}
      />

      {/* Vector Arrows */}
      {vectors.map(vector => (
        <VectorArrow
          key={vector.id}
          {...vector}
          width={config.viewport?.width || 640}
          height={config.viewport?.height || 360}
        />
      ))}

      {/* Labels Layer */}
      <LabelsLayer
        labels={config.labels}
        props={animatedProps}
        actors={config.actors}
        language={language}
        activeLabel={activeLabel}
        width={config.viewport?.width || 640}
        height={config.viewport?.height || 360}
      />
    </motion.svg>
  );
};

export default SceneRenderer;







