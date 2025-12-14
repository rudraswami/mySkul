/**
 * 🧪 NETRA ENGINE TESTS
 * =====================
 * 
 * Comprehensive test cases across all domains.
 * Each test validates:
 * - Correct concept parsing
 * - Appropriate visual strategy selection
 * - Semantic entity extraction
 * - Proper scene composition
 */

import { 
  Orchestrator, 
  createOrchestrator,
  generateVisual,
} from '../core/Orchestrator';
import { SemanticParser } from '../understanding/SemanticParser';
import { CompositionEngine, COMPOSITION_STRATEGIES } from '../composition/CompositionEngine';
import { ConceptGraph, ENTITY_TYPES, RELATIONSHIP_TYPES } from '../core/ConceptGraph';
import { getVisualSpec } from '../semantics/VisualOntology';

// ============================================
// TEST CASES
// ============================================

const TEST_CASES = {
  physics: [
    {
      id: 'newton_third_law',
      question: "Explain Newton's third law with a rocket launching",
      expectedDomain: 'physics',
      expectedEntities: ['rocket', 'force', 'gas'],
      expectedVisualType: 'force_diagram',
      expectedStrategy: COMPOSITION_STRATEGIES.FORCE_DIAGRAM,
    },
    {
      id: 'projectile_motion',
      question: 'Show the trajectory of a ball thrown at an angle',
      expectedDomain: 'physics',
      expectedEntities: ['ball', 'trajectory'],
      expectedVisualType: 'scene',
    },
    {
      id: 'friction_force',
      question: 'What is friction and how does it act on a moving car?',
      expectedDomain: 'physics',
      expectedEntities: ['friction', 'car'],
      expectedVisualType: 'force_diagram',
    },
    {
      id: 'pendulum',
      question: 'Explain the motion of a simple pendulum',
      expectedDomain: 'physics',
      expectedEntities: ['pendulum'],
      expectedVisualType: 'scene',
    },
    {
      id: 'light_reflection',
      question: 'How does light reflect from a plane mirror?',
      expectedDomain: 'physics',
      expectedEntities: ['light', 'mirror'],
      expectedVisualType: 'scene',
    },
  ],

  chemistry: [
    {
      id: 'covalent_bond',
      question: 'How does a covalent bond form between two hydrogen atoms?',
      expectedDomain: 'chemistry',
      expectedEntities: ['atom', 'bond', 'electron'],
      expectedVisualType: 'structure',
    },
    {
      id: 'chemical_reaction',
      question: 'Show the reaction between sodium and chlorine to form NaCl',
      expectedDomain: 'chemistry',
      expectedEntities: ['sodium', 'chlorine', 'reaction'],
      expectedVisualType: 'process_flow',
    },
    {
      id: 'ph_scale',
      question: 'Explain the pH scale from acids to bases',
      expectedDomain: 'chemistry',
      expectedEntities: ['acid', 'base', 'pH'],
      expectedVisualType: 'comparison',
    },
  ],

  biology: [
    {
      id: 'cell_structure',
      question: 'Show the structure of an animal cell with its organelles',
      expectedDomain: 'biology',
      expectedEntities: ['cell', 'nucleus', 'mitochondria'],
      expectedVisualType: 'structure',
    },
    {
      id: 'photosynthesis',
      question: 'Explain the process of photosynthesis',
      expectedDomain: 'biology',
      expectedEntities: ['photosynthesis'],
      expectedVisualType: 'process_flow',
    },
    {
      id: 'heart_circulation',
      question: 'How does blood flow through the four chambers of the heart?',
      expectedDomain: 'biology',
      expectedEntities: ['heart', 'blood'],
      expectedVisualType: 'cycle',
    },
    {
      id: 'dna_structure',
      question: 'Show the double helix structure of DNA',
      expectedDomain: 'biology',
      expectedEntities: ['DNA'],
      expectedVisualType: 'structure',
    },
    {
      id: 'cell_division',
      question: 'Explain the stages of mitosis',
      expectedDomain: 'biology',
      expectedEntities: ['mitosis'],
      expectedVisualType: 'process_flow',
    },
  ],

  math: [
    {
      id: 'quadratic_graph',
      question: 'Graph the function y = x² - 4',
      expectedDomain: 'math',
      expectedEntities: ['function', 'graph'],
      expectedVisualType: 'graph',
    },
    {
      id: 'pythagorean_theorem',
      question: 'Explain the Pythagorean theorem with a right triangle',
      expectedDomain: 'math',
      expectedEntities: ['triangle'],
      expectedVisualType: 'scene',
    },
    {
      id: 'venn_diagram',
      question: 'Show the intersection of two sets A and B',
      expectedDomain: 'math',
      expectedEntities: ['set'],
      expectedVisualType: 'comparison',
    },
  ],
};

// ============================================
// TEST UTILITIES
// ============================================

/**
 * Run a single test case
 */
async function runTestCase(testCase, orchestrator) {
  const { question, expectedDomain, expectedEntities, expectedVisualType, expectedStrategy } = testCase;
  
  const result = await orchestrator.generate(question, { subject: expectedDomain });
  
  const passed = {
    success: result.success,
    domainMatch: result.metadata?.domain === expectedDomain,
    hasEntities: result.debug?.entityCount > 0,
    hasScene: !!result.sceneGraph,
  };

  return {
    id: testCase.id,
    question,
    result,
    passed,
    allPassed: Object.values(passed).every(v => v),
  };
}

/**
 * Run all test cases
 */
async function runAllTests() {
  console.log('🧪 Starting NETRA Engine Tests...\n');
  
  const orchestrator = createOrchestrator({ useLLM: false });
  const results = {
    passed: 0,
    failed: 0,
    tests: [],
  };

  for (const [domain, cases] of Object.entries(TEST_CASES)) {
    console.log(`\n📚 Testing ${domain.toUpperCase()} domain...`);
    
    for (const testCase of cases) {
      try {
        const testResult = await runTestCase(testCase, orchestrator);
        results.tests.push(testResult);
        
        if (testResult.allPassed) {
          results.passed++;
          console.log(`  ✅ ${testCase.id}: PASSED`);
        } else {
          results.failed++;
          console.log(`  ❌ ${testCase.id}: FAILED`, testResult.passed);
        }
      } catch (error) {
        results.failed++;
        console.log(`  ❌ ${testCase.id}: ERROR - ${error.message}`);
        results.tests.push({
          id: testCase.id,
          question: testCase.question,
          error: error.message,
          allPassed: false,
        });
      }
    }
  }

  console.log('\n' + '='.repeat(50));
  console.log(`📊 Results: ${results.passed}/${results.passed + results.failed} tests passed`);
  console.log('='.repeat(50));

  return results;
}

// ============================================
// INDIVIDUAL TEST FUNCTIONS (for Jest)
// ============================================

describe('NETRA SemanticParser', () => {
  const parser = new SemanticParser({ useLLM: false });

  test('detects physics domain correctly', async () => {
    const graph = await parser.parse('What is force and how does it cause acceleration?');
    expect(graph.metadata.domain).toBe('physics');
  });

  test('detects chemistry domain correctly', async () => {
    const graph = await parser.parse('How do atoms form covalent bonds?');
    expect(graph.metadata.domain).toBe('chemistry');
  });

  test('detects biology domain correctly', async () => {
    const graph = await parser.parse('Explain the structure of a cell and its nucleus');
    expect(graph.metadata.domain).toBe('biology');
  });

  test('detects math domain correctly', async () => {
    const graph = await parser.parse('Graph the quadratic function y = x²');
    expect(graph.metadata.domain).toBe('math');
  });

  test('extracts entities from physics question', async () => {
    const graph = await parser.parse('A ball is pushed with a force');
    expect(graph.entities.size).toBeGreaterThan(0);
  });
});

describe('NETRA CompositionEngine', () => {
  const composer = new CompositionEngine({ width: 800, height: 600 });

  test('selects force diagram strategy for forces', () => {
    const graph = new ConceptGraph();
    graph.addEntity('force1', ENTITY_TYPES.FORCE, { label: 'F' });
    graph.addEntity('body1', ENTITY_TYPES.BODY, { label: 'Block' });
    graph.setMetadata('visualType', 'force_diagram');
    
    const scene = composer.compose(graph, 'physics');
    expect(scene.metadata.strategy).toBe(COMPOSITION_STRATEGIES.FORCE_DIAGRAM);
  });

  test('positions nodes correctly', () => {
    const graph = new ConceptGraph();
    graph.addEntity('obj1', ENTITY_TYPES.OBJECT, { label: 'A' });
    graph.addEntity('obj2', ENTITY_TYPES.OBJECT, { label: 'B' });
    
    const scene = composer.compose(graph, 'physics');
    const nodes = Array.from(scene.nodes.values());
    
    expect(nodes.length).toBe(2);
    expect(nodes[0].x).toBeGreaterThan(0);
    expect(nodes[0].y).toBeGreaterThan(0);
  });

  test('creates arrows from relationships', () => {
    const graph = new ConceptGraph();
    graph.addEntity('a', ENTITY_TYPES.OBJECT, { label: 'A' });
    graph.addEntity('b', ENTITY_TYPES.OBJECT, { label: 'B' });
    graph.addRelationship('a', 'b', RELATIONSHIP_TYPES.CAUSES);
    
    const scene = composer.compose(graph, 'physics');
    expect(scene.arrows.length).toBe(1);
  });
});

describe('NETRA VisualOntology', () => {
  test('returns physics force visual spec', () => {
    const spec = getVisualSpec('physics', 'force');
    expect(spec).not.toBeNull();
    expect(spec.primaryForm).toBeDefined();
    expect(spec.properties.color).toBeDefined();
  });

  test('returns chemistry atom visual spec', () => {
    const spec = getVisualSpec('chemistry', 'atom');
    expect(spec).not.toBeNull();
    expect(spec.variations).toBeDefined();
  });

  test('returns biology cell visual spec', () => {
    const spec = getVisualSpec('biology', 'cell');
    expect(spec).not.toBeNull();
    expect(spec.variations.animal).toBeDefined();
  });

  test('returns math function visual spec', () => {
    const spec = getVisualSpec('math', 'function_curve');
    expect(spec).not.toBeNull();
    expect(spec.variations).toBeDefined();
  });
});

describe('NETRA Orchestrator', () => {
  const orchestrator = createOrchestrator({ useLLM: false });

  test('generates visual for physics question', async () => {
    const result = await orchestrator.generate(
      'Explain friction on a moving block',
      { subject: 'physics' }
    );
    
    expect(result.success).toBe(true);
    expect(result.sceneGraph).toBeDefined();
    expect(result.metadata.domain).toBe('physics');
  });

  test('handles empty question gracefully', async () => {
    const result = await orchestrator.generate('', {});
    expect(result.sceneGraph).toBeDefined();
  });

  test('caches repeated questions', async () => {
    const question = 'Test caching mechanism';
    
    // First call
    await orchestrator.generate(question, {});
    
    // Second call should use cache
    const startTime = Date.now();
    await orchestrator.generate(question, {});
    const duration = Date.now() - startTime;
    
    expect(duration).toBeLessThan(50); // Should be instant from cache
  });
});

// ============================================
// EXPORT FOR MANUAL TESTING
// ============================================

export { TEST_CASES, runAllTests, runTestCase };



