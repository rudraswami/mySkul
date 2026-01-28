/**
 * 🎬 PROCEDURAL SCENE PIPELINE v2.0
 * ==================================
 * 
 * Entry point for the procedural visual generation system.
 * 
 * Architecture:
 * - LLM outputs SemanticIntent + ProceduralScenePlan
 * - QualityGateAutoFixer enhances locally (no API re-calls)
 * - RenderGraph builds tree of renderable nodes
 * - Generators create procedural shapes
 * - ProceduralRenderer executes and displays
 * 
 * INTEGRATION:
 * - Entity atom now supports `generator` param for procedural rendering
 * - DynamicVisualRenderer uses existing atom system + procedural enhancements
 */

// Core classes
export { 
  RenderGraphBuilder, 
  RenderNode, 
  LayerNode, 
  GroupNode, 
  PathNode, 
  ProceduralNode, 
  ParticleSystemNode,
  ShapeNode,
  RectNode,
  EllipseNode,
  CircleNode,
  PolygonNode,
  TextNode,
} from './RenderGraph';

export { default as ProceduralRenderer } from './ProceduralRenderer';
export { default as ProceduralSceneRenderer } from './ProceduralSceneRenderer';

// Generators
export { 
  registerGenerator,
  getGenerator,
  hasGenerator,
  listGenerators,
  generateNodes,
} from './generators/index';

// ============================================
// AVAILABLE GENERATORS
// ============================================
/*
BIOLOGY:
  - organic_shape: Cell-like irregular shape with optional membrane
  - chloroplast: Chloroplast with thylakoid stacks
  - mitochondria: Mitochondria with cristae folds
  - nucleus: Cell nucleus with chromatin and nucleolus
  - leaf: Leaf with veins and optional serration
  - dna_helix: DNA double helix

CHEMISTRY:
  - molecule: Ball-and-stick molecule with bonds
  - atom_orbital: Atom with electron shells
  - reaction_zone: Highlighted reaction area with glow

PHYSICS:
  - surface: Ground/surface with texture
  - wave: Sinusoidal wave (animated optional)
  - force_field: Gradient force field with arrows
  - motion_trail: Motion path with fade trail
  - flow_path: Curved animated flow path
*/

// ============================================
// USAGE IN ENTITY ATOM
// ============================================
/*
// In composition JSON, add generator to Entity params:
{
  "id": "chloroplast_1",
  "type": "Entity",
  "params": {
    "shape": "ellipse",
    "width": 200,
    "height": 120,
    "fill": "#22C55E",
    "generator": "chloroplast",  // <-- PROCEDURAL GENERATOR
    "generatorParams": {
      "stackCount": 5,
      "color": "#22C55E"
    }
  },
  "position": {"x": 360, "y": 280}
}
*/

console.log('🎬 [Procedural] Module v2.0 loaded - Full generator suite available');
