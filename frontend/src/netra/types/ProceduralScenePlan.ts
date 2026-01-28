/**
 * 🎬 PROCEDURAL SCENE PLAN SCHEMA v1.0
 * ====================================
 * 
 * Defines the structure for LLM-generated procedural scene descriptions.
 * The LLM outputs semantic intent + procedural drawing instructions.
 * Our renderer interprets these to create cinematic simulations.
 * 
 * KEY PRINCIPLE: LLM describes HOW to draw, not WHAT shapes to use.
 */

// ============================================
// TOP-LEVEL SCHEMA
// ============================================

export interface ProceduralScenePlan {
  version: '1.0';
  intent: SemanticIntent;
  canvas: CanvasSpec;
  layers: Layer[];
  effects?: GlobalEffect[];
  particles?: ParticleSystem[];
  choreography: ChoreographyBeat[];
  interactions: Interaction[];
}

// ============================================
// SEMANTIC INTENT
// ============================================

export interface SemanticIntent {
  concept: string;
  domain: Domain;
  processType: ProcessType;
  inputs: string[];
  transformer: string;
  outputs: string[];
  story: StoryStructure;
}

export type Domain = 'biology' | 'physics' | 'chemistry' | 'math' | 'general';

export type ProcessType = 
  | 'transformation'  // Input becomes output (photosynthesis, digestion)
  | 'flow'           // Something moves through system (circuits, blood flow)
  | 'comparison'     // Side-by-side differences
  | 'sequence'       // Ordered steps (cell division, algorithm)
  | 'structure'      // Parts of a whole (anatomy, architecture)
  | 'causation';     // Cause and effect chain

export interface StoryStructure {
  setup: string;    // Act 1: What we're looking at
  action: string;   // Act 2: What happens / transformation
  result: string;   // Act 3: What we learned / outcome
}

// ============================================
// CANVAS SPECIFICATION
// ============================================

export interface CanvasSpec {
  width: number;   // Default 720
  height: number;  // Default 520
  background: BackgroundSpec;
}

export interface BackgroundSpec {
  type: 'solid' | 'gradient' | 'procedural';
  color?: string;
  gradient?: GradientSpec;
  procedural?: ProceduralBackgroundSpec;
}

export interface GradientSpec {
  type: 'linear' | 'radial';
  direction?: 'vertical' | 'horizontal' | 'diagonal';
  colors: string[];
  stops?: number[];
}

export interface ProceduralBackgroundSpec {
  generator: string;
  params: Record<string, unknown>;
}

// ============================================
// LAYERS
// ============================================

export interface Layer {
  id: string;
  zIndex: number;
  elements: Element[];
  mask?: MaskSpec;
  blendMode?: BlendMode;
  opacity?: number;
}

export interface MaskSpec {
  type: 'path' | 'element';
  path?: string;
  elementId?: string;
}

export type BlendMode = 'normal' | 'multiply' | 'screen' | 'overlay' | 'soft-light';

// ============================================
// ELEMENTS
// ============================================

export interface Element {
  id: string;
  type: ElementType;
  position: Position;
  role: ElementRole;
  transform?: TransformSpec;
  fill?: FillSpec;
  stroke?: StrokeSpec;
  effects?: ElementEffect[];
  initialState?: InitialState;
  
  // Type-specific fields
  shape?: ShapeType;
  width?: number;
  height?: number;
  d?: string;  // SVG path data
  children?: Element[];
  generator?: GeneratorSpec;
  text?: string;
  fontSize?: number;
  fontWeight?: 'normal' | 'bold';
}

export type ElementType = 'path' | 'shape' | 'group' | 'procedural' | 'text';

export type ElementRole = 
  | 'hero'        // Main focus - large, centered, glowing
  | 'input'       // Entering element - left side, animated inward
  | 'output'      // Exiting element - right side, animated outward
  | 'environment' // Context/background - behind hero
  | 'connector'   // Shows relationship - lines/arrows
  | 'label'       // Text annotation
  | 'effect';     // Visual decoration

export type ShapeType = 'rect' | 'ellipse' | 'circle' | 'polygon' | 'hexagon' | 'triangle';

export interface Position {
  x: number;
  y: number;
}

export interface TransformSpec {
  scale?: number | { x: number; y: number };
  rotation?: number;  // Degrees
  skew?: { x: number; y: number };
  origin?: Position;
}

export interface InitialState {
  visible?: boolean;
  opacity?: number;
  scale?: number;
}

// ============================================
// FILL & STROKE
// ============================================

export interface FillSpec {
  type: 'solid' | 'gradient' | 'pattern';
  color?: string;
  gradient?: GradientSpec;
  pattern?: PatternSpec;
}

export interface PatternSpec {
  element: 'dots' | 'lines' | 'crosshatch' | 'waves' | 'custom';
  scale: number;
  spacing: number;
  color: string;
  rotation?: number;
}

export interface StrokeSpec {
  color: string;
  width: number;
  dash?: number[];
  lineCap?: 'butt' | 'round' | 'square';
  lineJoin?: 'miter' | 'round' | 'bevel';
}

// ============================================
// PROCEDURAL GENERATORS
// ============================================

export interface GeneratorSpec {
  type: GeneratorType;
  params: GeneratorParams;
}

export type GeneratorType = 
  // Biology
  | 'organic_shape'    // Cell-like irregular shape with optional internal structures
  | 'membrane'         // Double-line membrane boundary
  | 'leaf'             // Leaf with veins and optional serration
  | 'chloroplast'      // Organelle with thylakoid stacks
  | 'mitochondria'     // Organelle with cristae
  | 'nucleus'          // Cell nucleus with chromatin
  
  // Chemistry
  | 'molecule'         // Atoms connected by bonds
  | 'atom'             // Single atom with electron shells
  | 'reaction_zone'    // Highlighted area for reactions
  
  // Physics
  | 'surface'          // Ground/surface with texture
  | 'wave'             // Sinusoidal wave
  | 'force_field'      // Gradient field visualization
  | 'motion_trail'     // Path showing movement
  
  // Universal
  | 'flow_path'        // Curved path for flow visualization
  | 'arrow'            // Directional arrow
  | 'bracket'          // Grouping bracket
  | 'highlight_zone';  // Semi-transparent highlight area

export type GeneratorParams = 
  | OrganicShapeParams
  | LeafParams
  | MoleculeParams
  | SurfaceParams
  | WaveParams
  | FlowPathParams;

export interface OrganicShapeParams {
  baseShape: 'ellipse' | 'circle' | 'blob';
  width: number;
  height: number;
  irregularity: number;  // 0-1, how wavy the edge is
  membrane?: {
    thickness: number;
    double: boolean;
    color: string;
  };
  innerStructures?: {
    type: 'dots' | 'strands' | 'organelles';
    count: number;
    color: string;
  };
}

export interface LeafParams {
  width: number;
  height: number;
  veins: boolean;
  veinColor: string;
  serration: number;  // 0 = smooth, 1 = highly serrated
  color: string;
  stemLength: number;
}

export interface MoleculeParams {
  atoms: AtomSpec[];
  bonds: BondSpec[];
  style: '2d' | 'ball-stick' | 'space-fill';
}

export interface AtomSpec {
  id: string;
  element: string;  // e.g., "C", "O", "H", "N"
  position: Position;
  radius?: number;
  color?: string;
  label?: boolean;
}

export interface BondSpec {
  from: string;  // Atom ID
  to: string;    // Atom ID
  type: 'single' | 'double' | 'triple';
}

export interface SurfaceParams {
  width: number;
  height: number;
  texture: 'smooth' | 'rough' | 'grass' | 'ice' | 'wood' | 'metal';
  friction?: number;  // 0-1
  color: string;
  perspective?: boolean;  // Add slight 3D perspective
}

export interface WaveParams {
  width: number;
  amplitude: number;
  frequency: number;
  phase: number;
  animated: boolean;
  color: string;
  fill?: boolean;
}

export interface FlowPathParams {
  points: Position[];
  curvature: number;  // 0 = straight, 1 = very curved
  animated: boolean;
  dashPattern?: number[];
  particleFlow?: boolean;
}

// ============================================
// EFFECTS
// ============================================

export interface GlobalEffect {
  id: string;
  type: GlobalEffectType;
  params: Record<string, unknown>;
}

export type GlobalEffectType = 
  | 'ambient_particles'  // Floating particles in background
  | 'light_rays'         // Sunlight rays
  | 'vignette'           // Edge darkening
  | 'color_grade';       // Overall color adjustment

export interface ElementEffect {
  type: ElementEffectType;
  params: EffectParams;
}

export type ElementEffectType = 
  | 'glow'
  | 'shadow'
  | 'blur'
  | 'outline'
  | 'inner_shadow';

export interface EffectParams {
  color?: string;
  intensity?: number;
  radius?: number;
  offsetX?: number;
  offsetY?: number;
}

// ============================================
// PARTICLE SYSTEMS
// ============================================

export interface ParticleSystem {
  id: string;
  type: ParticleSystemType;
  emitter: EmitterSpec;
  particle: ParticleSpec;
  physics?: ParticlePhysics;
  lifetime: number;
  rate: number;
  trigger?: string;  // Event or 'auto'
}

export type ParticleSystemType = 
  | 'flow'      // Continuous stream
  | 'burst'     // Single explosion
  | 'ambient'   // Random floating
  | 'trail';    // Following an element

export interface EmitterSpec {
  type: 'point' | 'line' | 'area' | 'element';
  position?: Position;
  size?: { width: number; height: number };
  elementId?: string;
  direction?: number;  // Angle in degrees
  spread?: number;     // Cone spread angle
}

export interface ParticleSpec {
  shape: 'circle' | 'square' | 'star' | 'custom';
  size: [number, number];  // Min, max
  color: string | string[];  // Single or random from array
  opacity: [number, number];  // Start, end
  rotation?: boolean;
}

export interface ParticlePhysics {
  gravity?: Position;
  wind?: Position;
  friction?: number;
  bounce?: number;
}

// ============================================
// CHOREOGRAPHY
// ============================================

export interface ChoreographyBeat {
  id: string;
  act: 1 | 2 | 3;  // Which act this belongs to
  delay: number;   // Ms from scene start
  duration: number;
  target: string | string[];  // Element ID(s) or '*' for all
  action: ActionSpec;
  narration?: NarrationSpec;
}

export interface ActionSpec {
  type: ActionType;
  params: ActionParams;
}

export type ActionType = 
  | 'fadeIn'
  | 'fadeOut'
  | 'scaleIn'
  | 'scaleOut'
  | 'moveTo'
  | 'moveBy'
  | 'morph'
  | 'pulse'
  | 'glow'
  | 'highlight'
  | 'shake'
  | 'rotate'
  | 'emit'       // Start particle system
  | 'show'
  | 'hide';

export interface ActionParams {
  // Position
  x?: number;
  y?: number;
  
  // Scale
  scale?: number;
  fromScale?: number;
  
  // Timing
  duration?: number;
  easing?: EasingType;
  
  // Effects
  color?: string;
  intensity?: number;
  
  // Loops
  loop?: boolean;
  loopCount?: number;
  
  // Particles
  particleSystemId?: string;
}

export type EasingType = 
  | 'linear'
  | 'easeIn'
  | 'easeOut'
  | 'easeInOut'
  | 'bounce'
  | 'elastic';

export interface NarrationSpec {
  text: string;
  emphasis?: 'normal' | 'high' | 'whisper';
  position?: 'top' | 'bottom' | 'center';
}

// ============================================
// INTERACTIONS
// ============================================

export interface Interaction {
  id: string;
  type: InteractionType;
  target: string;  // Element ID
  property: string;  // Property to modify
  range?: RangeSpec;
  label: string;
  position?: 'auto' | Position;
  effects?: InteractionEffect[];
}

export type InteractionType = 
  | 'slider'    // Continuous value
  | 'drag'      // Move element
  | 'toggle'    // On/off
  | 'tap'       // Single action
  | 'scrub';    // Timeline scrub

export interface RangeSpec {
  min: number;
  max: number;
  step?: number;
  default: number;
}

export interface InteractionEffect {
  target: string;
  property: string;
  mapping: 'direct' | 'inverse' | 'custom';
  customFn?: string;  // Expression
}

// ============================================
// QUALITY GATE VALIDATION
// ============================================

export interface QualityGateResult {
  passed: boolean;
  violations: QualityViolation[];
  autoFixApplied: string[];
}

export interface QualityViolation {
  ruleId: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  message: string;
  autoFixAvailable: boolean;
}

// ============================================
// CONSTANTS
// ============================================

export const DEFAULT_CANVAS: CanvasSpec = {
  width: 720,
  height: 520,
  background: {
    type: 'gradient',
    gradient: {
      type: 'linear',
      direction: 'vertical',
      colors: ['#F8FAFC', '#E2E8F0'],
    },
  },
};

export const DOMAIN_COLORS: Record<Domain, { primary: string; secondary: string; accent: string }> = {
  biology: { primary: '#10B981', secondary: '#34D399', accent: '#FCD34D' },
  physics: { primary: '#3B82F6', secondary: '#60A5FA', accent: '#F472B6' },
  chemistry: { primary: '#8B5CF6', secondary: '#A78BFA', accent: '#F59E0B' },
  math: { primary: '#6366F1', secondary: '#818CF8', accent: '#14B8A6' },
  general: { primary: '#6B7280', secondary: '#9CA3AF', accent: '#F59E0B' },
};

export const ROLE_POSITIONS: Record<ElementRole, { xRange: [number, number]; yRange: [number, number] }> = {
  hero: { xRange: [280, 440], yRange: [180, 340] },
  input: { xRange: [60, 180], yRange: [100, 420] },
  output: { xRange: [540, 660], yRange: [100, 420] },
  environment: { xRange: [0, 720], yRange: [0, 520] },
  connector: { xRange: [180, 540], yRange: [100, 420] },
  label: { xRange: [0, 720], yRange: [0, 520] },
  effect: { xRange: [0, 720], yRange: [0, 520] },
};

export const MIN_HERO_SIZE = { width: 200, height: 150 };
export const MIN_CANVAS_COVERAGE = 0.6;
export const MIN_EFFECTS_COUNT = 2;
export const MIN_CHOREOGRAPHY_BEATS = 3;
