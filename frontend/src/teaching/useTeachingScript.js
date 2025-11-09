/**
 * useTeachingScript
 * Selects a professor-style, step-by-step teaching script for a topic.
 * Returns a normalized { steps, scene, meta } object the orchestrator can render.
 */
import { useMemo } from 'react';
import covalentBonding from './scripts/covalentBonding';
import atomicStructure from './scripts/atomicStructureElectronConfig';

/**
 * @param {Object} params
 * @param {string} params.topic - e.g., 'Covalent Bonding'
 * @param {string} params.subject - e.g., 'Chemistry'
 * @param {('simple'|'advanced')} params.complexity - adaptive complexity level
 */
export default function useTeachingScript({ topic, subject = 'general', complexity = 'simple' }) {
  return useMemo(() => {
    const t = (topic || '').toLowerCase();
    const s = (subject || 'general').toLowerCase();

    // Route known topics to curated scripts; fallback to a generic framing
    if (s === 'chemistry' && t.includes('covalent')) {
      return covalentBonding({ complexity });
    }
    if (s === 'chemistry' && (t.includes('atomic structure') || t.includes('electron configuration') || t.includes('electronic configuration') || t.includes('bohr') || t.includes('shell') || t.includes('orbital'))) {
      return atomicStructure({ complexity });
    }

    // Generic script fallback
    const steps = [
      {
        id: 'intro',
        title: 'Let’s start with the main idea',
        narration: `We will explore ${topic || 'this concept'} and see why it works.`,
        highlights: [],
      },
      {
        id: 'change',
        title: 'Notice how it changes with input',
        narration: 'We vary one factor to see its effect and understand cause and effect.',
        highlights: [],
      },
      {
        id: 'real',
        title: 'Here’s what it means in real life',
        narration: 'We map the insight to a quick, familiar situation.',
        highlights: [],
      },
    ];

    return { steps, scene: null, meta: { topic, subject, complexity } };
  }, [topic, subject, complexity]);
}
