import React, { useEffect, useMemo, useState, useCallback } from 'react';
import DynamicSceneComposer from '../components/DynamicSceneComposer';
import ProgressiveExplanation from '../components/ProgressiveExplanation';
import MicroEngagementOverlay from '../components/MicroEngagementOverlay';
import ClarityRating from '../components/ClarityRating';
import useTeachingScript from './useTeachingScript';
import { useExistingVisualEngine } from '../hooks/useExistingVisualEngine';
import { teachingAnalytics } from '../utils/teachingAnalytics';

/**
 * TeachingOrchestrator
 * Converts a teaching script into a DynamicSceneComposer story with professor-style sequencing.
 * - Does not change existing layout logic
 * - Caps visual height at 50vh per new design
 * - Tracks micro-engagement events silently
 */
export default function TeachingOrchestrator({ topic, subject, complexity = 'simple', visualData, onComplete }) {
  const { steps, scene, meta } = useTeachingScript({ topic, subject, complexity });
  // Prefer backend/engine visual first, else script-provided scene
  const passThrough = useExistingVisualEngine(visualData);
  const t = String(topic || '').toLowerCase();
  const preferScript = (meta?.subject || subject || '').toLowerCase() === 'chemistry' && (
    t.includes('atomic structure') || t.includes('electron configuration') || t.includes('electronic configuration') || t.includes('bohr') || t.includes('shell') || t.includes('orbital')
  );
  const baseScene = preferScript && scene ? scene : (passThrough || scene);

  const [stepIndex, setStepIndex] = useState(0);
  const current = steps[stepIndex] || null;
  const isLastStep = stepIndex === (steps?.length || 1) - 1;
  const [clarity, setClarity] = useState(0);

  // Build a story_scene visualData decorated with captain/higlights for current step
  const teachingScene = useMemo(() => {
    if (!baseScene || baseScene.type !== 'story_scene') return baseScene || null;
    const flow = Array.isArray(baseScene.interaction_flow) ? baseScene.interaction_flow : [];
    // If step references a flow id, ensure it exists; otherwise just show base
    const caption_text = current?.title || baseScene.caption_text || '';
    return { ...baseScene, caption_text, interaction_flow: flow };
  }, [baseScene, current]);

  useEffect(() => {
    teachingAnalytics.track({ kind: 'teaching_step_view', stepId: current?.id, topic, subject, complexity });
  }, [current, topic, subject, complexity]);

  const next = useCallback(() => {
    teachingAnalytics.track({ kind: 'teaching_next', stepId: current?.id, topic, subject, complexity });
    const last = stepIndex >= steps.length - 1;
    if (last) {
      teachingAnalytics.track({ kind: 'teaching_complete', topic, subject, complexity, steps: steps.length, clarity });
      onComplete?.();
    } else {
      setStepIndex((i) => Math.min(i + 1, steps.length - 1));
    }
  }, [current, stepIndex, steps.length, onComplete, topic, subject, complexity]);

  const prev = useCallback(() => {
    teachingAnalytics.track({ kind: 'teaching_prev', stepId: current?.id, topic, subject, complexity });
    setStepIndex((i) => Math.max(i - 1, 0));
  }, [current, topic, subject, complexity]);

  const onAnswer = useCallback((optionId) => {
    const correct = current?.microCheck?.correct;
    teachingAnalytics.track({ kind: 'micro_check_answer', stepId: current?.id, optionId, correct: optionId === correct, topic, subject, complexity });
  }, [current, topic, subject, complexity]);

  const onRateClarity = useCallback((score) => {
    setClarity(score);
    teachingAnalytics.track({ kind: 'clarity_rating', stepId: current?.id, topic, subject, complexity, score });
  }, [current, topic, subject, complexity]);

  if (!steps?.length) return null;

  return (
    <div className="w-full">
      {/* Visual container at max 50vh without altering existing containers */}
      <div className="w-full flex justify-center">
        <div className="w-full max-w-5xl rounded-3xl border border-purple-100 bg-white/95 p-4 shadow-lg">
          <DynamicSceneComposer visualData={teachingScene} />
        </div>
      </div>

      {/* Professor-style sequencing and narration */}
      <div className="w-full max-w-5xl mx-auto mt-3">
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-600">Step {stepIndex + 1} of {steps.length}</div>
          <div className="space-x-2">
            <button onClick={prev} disabled={stepIndex === 0} className="px-3 py-1.5 rounded-lg border border-gray-200 bg-white disabled:opacity-50">Back</button>
            <button onClick={next} className="px-3 py-1.5 rounded-lg border border-purple-200 bg-purple-50 hover:bg-purple-100">Next</button>
          </div>
        </div>

        <div className="mt-2">
          <ProgressiveExplanation
            sections={{
              foundation: current?.title || '',
              step_by_step: current?.narration || '',
              real_life: meta?.subject ? `Subject: ${meta.subject}` : '',
              key_points: teachingScene?.caption_text || '',
            }}
          />
        </div>

        <MicroEngagementOverlay check={current?.microCheck} onAnswer={onAnswer} />
        {isLastStep && (
          <ClarityRating value={clarity} onRate={onRateClarity} />
        )}
      </div>
    </div>
  );
}
