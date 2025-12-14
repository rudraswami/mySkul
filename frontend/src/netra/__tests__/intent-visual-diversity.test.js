/**
 * 🧪 INTENT-DRIVEN VISUAL DIVERSITY TEST
 * =======================================
 * 
 * This test validates the core promise of NETRA v3.0:
 * Same topic + Different intent = Different visual
 * 
 * Test Case: FRICTION
 * We ask 5 different questions about friction.
 * Each should produce a DIFFERENT visual form/layout/animation.
 */

import { IntentClassifier, INTENT_TYPES } from '../reasoning/IntentClassifier';
import { FormSelector, STRUCTURAL_FORMS } from '../reasoning/FormSelector';
import { LayoutVariator } from '../reasoning/LayoutVariator';
import { AnimationDirector, ANIMATION_STRATEGIES } from '../reasoning/AnimationDirector';
import { ContentMapper } from '../reasoning/ContentMapper';

describe('Intent-Driven Visual Diversity', () => {
  let intentClassifier;
  let formSelector;
  let layoutVariator;
  let animationDirector;
  let contentMapper;

  beforeEach(() => {
    intentClassifier = new IntentClassifier();
    formSelector = new FormSelector();
    layoutVariator = new LayoutVariator();
    animationDirector = new AnimationDirector();
    contentMapper = new ContentMapper();
    
    // Reset history for consistent tests
    layoutVariator.resetHistory();
  });

  // ============================================
  // TEST: 5 FRICTION QUESTIONS → 5 DIFFERENT INTENTS
  // ============================================
  
  describe('Friction Questions - Intent Classification', () => {
    const frictionQuestions = [
      { question: 'Explain friction', expectedIntent: INTENT_TYPES.CONCEPTUAL },
      { question: 'Why does friction exist?', expectedIntent: INTENT_TYPES.CAUSAL_INQUIRY },
      { question: 'What if there was no friction?', expectedIntent: INTENT_TYPES.COUNTERFACTUAL },
      { question: 'Compare static vs kinetic friction', expectedIntent: INTENT_TYPES.COMPARATIVE },
      { question: 'Show friction intuitively', expectedIntent: INTENT_TYPES.INTUITIVE },
    ];

    frictionQuestions.forEach(({ question, expectedIntent }) => {
      it(`should classify "${question}" as ${expectedIntent}`, () => {
        const result = intentClassifier.classify(question);
        expect(result.primary).toBe(expectedIntent);
        expect(result.confidence).toBeGreaterThan(0.3);
      });
    });

    it('should produce 5 unique intents for 5 friction questions', () => {
      const intents = frictionQuestions.map(q => 
        intentClassifier.classify(q.question).primary
      );
      const uniqueIntents = new Set(intents);
      expect(uniqueIntents.size).toBe(5);
    });
  });

  // ============================================
  // TEST: DIFFERENT INTENTS → DIFFERENT FORMS
  // ============================================

  describe('Intent to Form Mapping', () => {
    it('CONCEPTUAL → CAUSE_EFFECT form', () => {
      const intent = intentClassifier.classify('Explain friction');
      const form = formSelector.select(intent);
      expect(form.form).toBe(STRUCTURAL_FORMS.CAUSE_EFFECT);
    });

    it('CAUSAL_INQUIRY → CAUSAL_CHAIN form', () => {
      const intent = intentClassifier.classify('Why does friction exist?');
      const form = formSelector.select(intent);
      expect(form.form).toBe(STRUCTURAL_FORMS.CAUSAL_CHAIN);
    });

    it('COUNTERFACTUAL → COUNTERFACTUAL form', () => {
      const intent = intentClassifier.classify('What if there was no friction?');
      const form = formSelector.select(intent);
      expect(form.form).toBe(STRUCTURAL_FORMS.COUNTERFACTUAL);
    });

    it('COMPARATIVE → COMPARISON form', () => {
      const intent = intentClassifier.classify('Compare static vs kinetic friction');
      const form = formSelector.select(intent);
      expect(form.form).toBe(STRUCTURAL_FORMS.COMPARISON);
    });

    it('INTUITIVE → METAPHOR_SCENE form', () => {
      const intent = intentClassifier.classify('Show friction intuitively');
      const form = formSelector.select(intent);
      expect(form.form).toBe(STRUCTURAL_FORMS.METAPHOR_SCENE);
    });
  });

  // ============================================
  // TEST: DIFFERENT INTENTS → DIFFERENT ANIMATIONS
  // ============================================

  describe('Intent to Animation Mapping', () => {
    it('CONCEPTUAL → TEACHER_DRAWING animation', () => {
      const intent = intentClassifier.classify('Explain friction');
      const form = formSelector.select(intent);
      const animation = animationDirector.direct(intent, form);
      expect([
        ANIMATION_STRATEGIES.TEACHER_DRAWING,
        ANIMATION_STRATEGIES.SEQUENTIAL_BUILD,
        ANIMATION_STRATEGIES.PROGRESSIVE_REVEAL,
      ]).toContain(animation.strategy);
    });

    it('COUNTERFACTUAL → CONTRAST_FLASH animation', () => {
      const intent = intentClassifier.classify('What if there was no friction?');
      const form = formSelector.select(intent);
      const animation = animationDirector.direct(intent, form);
      expect([
        ANIMATION_STRATEGIES.CONTRAST_FLASH,
        ANIMATION_STRATEGIES.SIDE_BY_SIDE_GROW,
        ANIMATION_STRATEGIES.ALTERNATE_FOCUS,
      ]).toContain(animation.strategy);
    });

    it('COMPARATIVE → SIDE_BY_SIDE_GROW animation', () => {
      const intent = intentClassifier.classify('Compare static vs kinetic friction');
      const form = formSelector.select(intent);
      const animation = animationDirector.direct(intent, form);
      expect([
        ANIMATION_STRATEGIES.SIDE_BY_SIDE_GROW,
        ANIMATION_STRATEGIES.ALTERNATE_FOCUS,
      ]).toContain(animation.strategy);
    });

    it('INTUITIVE → STORY_BEATS animation', () => {
      const intent = intentClassifier.classify('Show friction intuitively');
      const form = formSelector.select(intent);
      const animation = animationDirector.direct(intent, form);
      expect([
        ANIMATION_STRATEGIES.STORY_BEATS,
        ANIMATION_STRATEGIES.TEACHER_DRAWING,
        ANIMATION_STRATEGIES.CINEMATIC,
      ]).toContain(animation.strategy);
    });
  });

  // ============================================
  // TEST: FULL PIPELINE PRODUCES DIVERSE OUTPUT
  // ============================================

  describe('Full Pipeline Diversity', () => {
    const runPipeline = (question) => {
      const intent = intentClassifier.classify(question);
      const form = formSelector.select(intent);
      const layout = layoutVariator.choose(form, { metadata: { entityCount: 4 } });
      const animation = animationDirector.direct(intent, form, layout);

      return {
        intent: intent.primary,
        form: form.form,
        layout: layout.layout,
        animation: animation.strategy,
      };
    };

    it('5 friction questions produce 5 different intent+form combinations', () => {
      const questions = [
        'Explain friction',
        'Why does friction exist?',
        'What if there was no friction?',
        'Compare static vs kinetic friction',
        'Show friction intuitively',
      ];

      const results = questions.map(runPipeline);
      
      // Each should have unique intent
      const intents = results.map(r => r.intent);
      expect(new Set(intents).size).toBe(5);

      // Should have at least 3 unique forms (some forms may overlap)
      const forms = results.map(r => r.form);
      expect(new Set(forms).size).toBeGreaterThanOrEqual(3);

      // Log results for visual inspection
      console.log('📊 Pipeline Results:');
      questions.forEach((q, i) => {
        console.log(`  "${q}"`);
        console.log(`    → Intent: ${results[i].intent}`);
        console.log(`    → Form: ${results[i].form}`);
        console.log(`    → Layout: ${results[i].layout}`);
        console.log(`    → Animation: ${results[i].animation}`);
      });
    });

    it('asking same question twice can produce different layouts', () => {
      const question = 'Explain friction';
      
      layoutVariator.resetHistory();
      const result1 = runPipeline(question);
      
      // Don't reset - should try to avoid repetition
      const result2 = runPipeline(question);

      // Intent and form should be same
      expect(result1.intent).toBe(result2.intent);
      expect(result1.form).toBe(result2.form);
      
      // Layout should potentially be different (variation)
      // Note: This may sometimes be same due to random selection
      console.log('Layout 1:', result1.layout, 'Layout 2:', result2.layout);
    });
  });

  // ============================================
  // TEST: CROSS-DOMAIN WORKS (Subject-Agnostic)
  // ============================================

  describe('Subject-Agnostic Classification', () => {
    it('classifies physics question correctly', () => {
      const result = intentClassifier.classify('What if gravity was stronger?');
      expect(result.primary).toBe(INTENT_TYPES.COUNTERFACTUAL);
    });

    it('classifies chemistry question correctly', () => {
      const result = intentClassifier.classify('Compare ionic vs covalent bonds');
      expect(result.primary).toBe(INTENT_TYPES.COMPARATIVE);
    });

    it('classifies biology question correctly', () => {
      const result = intentClassifier.classify('Why does photosynthesis happen?');
      expect(result.primary).toBe(INTENT_TYPES.CAUSAL_INQUIRY);
    });

    it('classifies math question correctly', () => {
      const result = intentClassifier.classify('Explain the quadratic formula');
      expect(result.primary).toBe(INTENT_TYPES.CONCEPTUAL);
    });

    it('classifies history question correctly', () => {
      const result = intentClassifier.classify('Types of government systems');
      expect(result.primary).toBe(INTENT_TYPES.CLASSIFICATORY);
    });
  });
});

