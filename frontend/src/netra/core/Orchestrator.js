/**
 * 🎯 NETRA ORCHESTRATOR v3.0
 * ==========================
 * 
 * The central brain that coordinates all NETRA subsystems.
 * 
 * INTENT-DRIVEN PIPELINE (v3.0):
 * 1. Question → IntentClassifier → Intent (WHY is student asking?)
 * 2. Intent → FormSelector → Visual Form (WHAT structure?)
 * 3. Question → SemanticParser → ConceptGraph (WHAT content?)
 * 4. Form + Content → ContentMapper → Filled Form
 * 5. Form → LayoutVariator → Layout (HOW to arrange?)
 * 6. Intent → AnimationDirector → Animation Strategy (HOW to reveal?)
 * 7. All → Renderer → Dynamic Visual
 * 
 * KEY INSIGHT: Same topic + different intent = different visual.
 * This is subject-agnostic, question-driven visual intelligence.
 */

import { SemanticParser } from '../understanding/SemanticParser';
import { CompositionEngine, SceneGraph } from '../composition/CompositionEngine';
import { ConceptGraph } from './ConceptGraph';
import { getVisualSpec, findVisualSpec } from '../semantics/VisualOntology';

// Narrative & Positioning layers
import { TeachingBeatEngine } from '../narrative/TeachingBeatEngine';
import { SemanticPositioner } from '../composition/SemanticPositioner';

// NEW: Visual Reasoning Layer (v3.0)
import {
  IntentClassifier,
  FormSelector,
  ContentMapper,
  LayoutVariator,
  AnimationDirector,
} from '../reasoning';

// ============================================
// ORCHESTRATOR CLASS
// ============================================

export class Orchestrator {
  constructor(options = {}) {
    this.options = {
      width: 800,
      height: 600,
      style: 'sketch',                 // sketch, technical, minimal
      animationEnabled: true,
      useLLM: true,                    // Use LLM for deep understanding
      fallbackToRules: true,           // Fall back to rule-based parsing
      apiClient: options.apiClient || null,
      ...options,
    };

    // Initialize subsystems
    this.parser = new SemanticParser({
      useLLM: this.options.useLLM,
      fallbackToRules: this.options.fallbackToRules,
      apiClient: this.options.apiClient,
    });

    this.composer = new CompositionEngine({
      width: this.options.width,
      height: this.options.height,
      style: this.options.style,
      animationEnabled: this.options.animationEnabled,
    });

    // Teaching narrative engine - creates beat-by-beat teaching sequence
    this.narrativeEngine = new TeachingBeatEngine({
      enableNarration: true,
    });

    // Semantic positioner - places elements based on physics meaning
    this.positioner = new SemanticPositioner({
      width: this.options.width,
      height: this.options.height,
    });

    // ============================================
    // NEW: VISUAL REASONING LAYER (v3.0)
    // ============================================
    
    // Intent Classifier - analyzes WHY the student is asking
    this.intentClassifier = new IntentClassifier();
    
    // Form Selector - chooses WHAT visual structure to use
    this.formSelector = new FormSelector();
    
    // Content Mapper - fills form slots with entities
    this.contentMapper = new ContentMapper();
    
    // Layout Variator - ensures visual DIVERSITY
    this.layoutVariator = new LayoutVariator();
    
    // Animation Director - decides HOW to reveal
    this.animationDirector = new AnimationDirector();

    // Cache for repeated questions
    this.cache = new Map();
  }

  /**
   * Generate a visual from a question using INTENT-DRIVEN pipeline
   * @param {string} question - Natural language question
   * @param {Object} context - Additional context (subject, level, etc.)
   * @returns {Promise<Object>} Complete visual specification
   */
  async generate(question, context = {}) {
    const startTime = Date.now();

    // Check cache - disabled for variation testing
    // const cacheKey = this.getCacheKey(question, context);
    // if (this.cache.has(cacheKey)) {
    //   console.log('🎯 [Orchestrator] Cache hit');
    //   return this.cache.get(cacheKey);
    // }

    try {
      console.log('═══════════════════════════════════════════════════');
      console.log('🎯 [Orchestrator v3.0] INTENT-DRIVEN VISUAL GENERATION');
      console.log('🎯 Question:', question);
      console.log('═══════════════════════════════════════════════════');

      // ============================================
      // STEP 1: INTENT CLASSIFICATION (NEW!)
      // WHY is the student asking this?
      // ============================================
      console.log('🧠 [Step 1] Classifying intent...');
      const intentResult = this.intentClassifier.classify(question);
      console.log('🧠 [Step 1] Intent:', {
        primary: intentResult.primary,
        confidence: intentResult.confidence.toFixed(2),
        secondary: intentResult.secondary,
      });

      // ============================================
      // STEP 2: FORM SELECTION (NEW!)
      // WHAT visual structure to use?
      // ============================================
      console.log('🎨 [Step 2] Selecting visual form...');
      const formResult = this.formSelector.select(intentResult, context);
      console.log('🎨 [Step 2] Form:', {
        form: formResult.form,
        name: formResult.specification.name,
      });

      // ============================================
      // STEP 3: CONTENT PARSING
      // WHAT entities and relationships?
      // ============================================
      console.log('📚 [Step 3] Parsing content...');
      const conceptGraph = await this.parser.parse(question, context);
      const domain = conceptGraph.metadata.domain || context.subject || 'physics';
      console.log('📚 [Step 3] Content:', conceptGraph.getSummary());

      // ============================================
      // STEP 4: CONTENT MAPPING (NEW!)
      // Fill form slots with content
      // ============================================
      console.log('📦 [Step 4] Mapping content to form...');
      const filledForm = this.contentMapper.map(conceptGraph, formResult, intentResult);
      console.log('📦 [Step 4] Filled slots:', Object.keys(filledForm.slots).length);

      // ============================================
      // STEP 5: LAYOUT SELECTION (NEW!)
      // HOW to arrange spatially?
      // ============================================
      console.log('🎲 [Step 5] Choosing layout variant...');
      const layoutResult = this.layoutVariator.choose(formResult, filledForm);
      console.log('🎲 [Step 5] Layout:', layoutResult.name);

      // ============================================
      // STEP 6: SCENE COMPOSITION
      // Build the actual scene graph
      // ============================================
      console.log('🏗️ [Step 6] Composing scene...');
      const sceneGraph = this.composer.compose(conceptGraph, domain);
      
      // Apply semantic positioning
      this.positioner.positionElements(conceptGraph, sceneGraph);
      console.log('🏗️ [Step 6] Scene:', {
        nodes: sceneGraph.nodes.size,
        arrows: sceneGraph.arrows.length,
      });

      // ============================================
      // STEP 7: ANIMATION DIRECTION (NEW!)
      // HOW to reveal over time?
      // ============================================
      console.log('🎬 [Step 7] Directing animation...');
      const animationResult = this.animationDirector.direct(intentResult, formResult, layoutResult);
      const animationBeats = animationResult.generateBeats(filledForm);
      console.log('🎬 [Step 7] Animation:', {
        strategy: animationResult.name,
        beats: animationBeats.length,
      });

      // ============================================
      // STEP 8: BUILD FINAL OUTPUT
      // ============================================
      const result = {
        success: true,
        question,
        context,
        
        // Visual output
        sceneGraph,
        
        // Reasoning results (NEW!)
        reasoning: {
          intent: intentResult,
          form: formResult,
          layout: layoutResult,
          animation: animationResult,
          filledForm,
        },
        
        // Animation
        animationBeats,
        teachingSequence: this.narrativeEngine.generateSequence(conceptGraph, context),
        
        // Metadata
        metadata: {
          domain,
          topic: conceptGraph.metadata.topic,
          visualType: formResult.form,
          intent: intentResult.primary,
          layout: layoutResult.layout,
          animationStrategy: animationResult.strategy,
          generationTime: Date.now() - startTime,
        },
        
        // Debug
        debug: {
          conceptGraph: conceptGraph.toJSON(),
          entityCount: conceptGraph.entities.size,
          relationshipCount: conceptGraph.relationships.length,
        },
      };
      
      console.log('═══════════════════════════════════════════════════');
      console.log('✅ [Orchestrator] Generation complete in', Date.now() - startTime, 'ms');
      console.log('✅ Intent:', intentResult.primary, '→ Form:', formResult.form, '→ Layout:', layoutResult.layout);
      console.log('═══════════════════════════════════════════════════');

      // Cache result
      this.cache.set(cacheKey, result);

      console.log('✅ [Orchestrator] Generation complete in', result.metadata.generationTime, 'ms');
      
      return result;

    } catch (error) {
      console.error('❌ [Orchestrator] Generation failed:', error);
      
      return {
        success: false,
        question,
        context,
        error: error.message,
        sceneGraph: this.createFallbackScene(question),
      };
    }
  }

  /**
   * Generate from pre-built ConceptGraph (for advanced use)
   */
  generateFromGraph(conceptGraph, context = {}) {
    const domain = conceptGraph.metadata.domain || context.subject || 'physics';
    const sceneGraph = this.composer.compose(conceptGraph, domain);
    
    return {
      success: true,
      sceneGraph,
      metadata: {
        domain,
        topic: conceptGraph.metadata.topic,
        visualType: conceptGraph.metadata.visualType,
        strategy: sceneGraph.metadata.strategy,
      },
    };
  }

  /**
   * Create a fallback scene for error cases
   */
  createFallbackScene(question) {
    const scene = new SceneGraph();
    scene.setBounds(this.options.width, this.options.height);
    
    // Add a simple placeholder
    const node = scene.addNode('fallback', {
      type: 'object',
      label: 'Concept',
      properties: { visualHint: 'generic' },
    });
    
    node.setPosition(
      this.options.width / 2 - 50,
      this.options.height / 2 - 30
    );
    node.setSize(100, 60);
    node.primitive = 'generic';
    
    scene.addAnnotation('Could not generate visual', {
      x: this.options.width / 2,
      y: this.options.height - 40,
    }, {
      fontSize: 14,
      color: '#E74C3C',
      textAnchor: 'middle',
    });
    
    return scene;
  }

  /**
   * Get cache key for question + context
   */
  getCacheKey(question, context) {
    return `${question.toLowerCase().trim()}_${context.subject || ''}_${context.level || ''}`;
  }

  /**
   * Clear cache
   */
  clearCache() {
    this.cache.clear();
  }

  /**
   * Update options
   */
  updateOptions(newOptions) {
    this.options = { ...this.options, ...newOptions };
    
    // Reinitialize composer with new options
    this.composer = new CompositionEngine({
      width: this.options.width,
      height: this.options.height,
      style: this.options.style,
      animationEnabled: this.options.animationEnabled,
    });
  }
}

// ============================================
// SINGLETON INSTANCE
// ============================================

let defaultOrchestrator = null;

/**
 * Get or create the default orchestrator
 */
export function getOrchestrator(options = {}) {
  if (!defaultOrchestrator) {
    defaultOrchestrator = new Orchestrator(options);
  }
  return defaultOrchestrator;
}

/**
 * Create a new orchestrator instance
 */
export function createOrchestrator(options = {}) {
  return new Orchestrator(options);
}

/**
 * Quick generate helper
 */
export async function generateVisual(question, context = {}, options = {}) {
  const orchestrator = new Orchestrator(options);
  return await orchestrator.generate(question, context);
}

export default Orchestrator;



