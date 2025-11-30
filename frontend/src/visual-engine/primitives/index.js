/**
 * 🎨 VISUAL PRIMITIVES LIBRARY
 * ============================
 * 
 * Reusable SVG components for building ANY visual concept.
 * These are the building blocks of our visual engine.
 * 
 * Categories:
 * - Motion: Vehicle, Ball, Arrow, Path
 * - Display: Label, Formula, Counter, Badge
 * - Layout: Track, Grid, Container, Divider
 * - Science: Atom, Cell, Molecule, Wave
 * - Effects: Glow, Pulse, Trail, Burst
 */

export { default as Vehicle } from './Vehicle';
export { default as Ball } from './Ball';
export { default as Arrow } from './Arrow';
export { default as Label } from './Label';
export { default as Formula } from './Formula';
export { default as Counter } from './Counter';
export { default as Track } from './Track';
export { default as Container } from './Container';
export { default as Atom } from './Atom';
export { default as Cell } from './Cell';
export { default as Wave } from './Wave';
export { default as Graph } from './Graph';
export { default as Cycle } from './Cycle';
export { default as FlowArrow } from './FlowArrow';
export { default as MemoryHook } from './MemoryHook';
export { default as HandText } from './HandText';
export { default as AnimatedPath } from './AnimatedPath';

// Color constants
export const COLORS = {
  // Indian tricolor theme
  saffron: '#FF9933',
  green: '#138808',
  navy: '#000080',
  
  // Extended palette
  gold: '#FFD700',
  red: '#EF4444',
  blue: '#3B82F6',
  purple: '#8B5CF6',
  cyan: '#06B6D4',
  emerald: '#10B981',
  amber: '#F59E0B',
  rose: '#F43F5E',
  
  // Neutrals
  chalk: '#2D3436',
  chalkLight: '#636E72',
  paper: '#FFFBF0',
  paperLines: '#E8DCC8',
  
  // UI
  highlight: '#FEF3C7',
  success: '#10B981',
  warning: '#F59E0B',
  error: '#EF4444',
};

// Subject-specific themes
export const SUBJECT_THEMES = {
  physics: {
    primary: COLORS.saffron,
    secondary: COLORS.blue,
    accent: COLORS.gold,
    background: '#FFF7ED',
  },
  chemistry: {
    primary: COLORS.purple,
    secondary: COLORS.emerald,
    accent: COLORS.amber,
    background: '#FAF5FF',
  },
  biology: {
    primary: COLORS.green,
    secondary: COLORS.cyan,
    accent: COLORS.rose,
    background: '#ECFDF5',
  },
  mathematics: {
    primary: COLORS.blue,
    secondary: COLORS.purple,
    accent: COLORS.cyan,
    background: '#EFF6FF',
  },
};

// Animation presets
export const ANIMATIONS = {
  fadeIn: {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
    transition: { duration: 0.5 },
  },
  slideUp: {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.5 },
  },
  scaleIn: {
    initial: { scale: 0, opacity: 0 },
    animate: { scale: 1, opacity: 1 },
    transition: { type: 'spring', stiffness: 200 },
  },
  drawPath: {
    initial: { pathLength: 0 },
    animate: { pathLength: 1 },
    transition: { duration: 1, ease: 'easeInOut' },
  },
};

