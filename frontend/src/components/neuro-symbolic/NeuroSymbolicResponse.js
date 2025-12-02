/**
 * Neuro-Symbolic Response Container
 * Displays all 8 sections of the AI response
 */
import React from 'react';
import VisualSchema from './VisualSchema';
import ProfessorVerification from './ProfessorVerification';
import MiniPractice from './MiniPractice';
import VisualConceptBlock from '../VisualConceptBlock'; // Importing the VisualConceptBlock from components root
import SmartTeachingVisual from '../SmartTeachingVisual'; // Professor-style storytelling (Chemistry-only rollout)
import TeachingVisualPlayer from '../TeachingVisualPlayer'; // PRIORITY: Visual Professor Engine player
import atomicStructure from '../../teaching/scripts/atomicStructureElectronConfig';
import AtomicInteractiveCard from '../../teaching/AtomicInteractiveCard';
import CovalentInteractiveCard from '../../teaching/CovalentInteractiveCard';
import SketchAnimator from '../SketchAnimator'; // Importing the SketchAnimator from components root
import { useExistingVisualEngine } from '../../hooks/useExistingVisualEngine'; // Importing visual engine hook from src/hooks
import { NeuralThinkingIndicator } from '../chat/NeuralThinkingIndicator';

export default function NeuroSymbolicResponse({ response, isLoading }) {
  if (isLoading) {
    return (
      <div className="flex justify-center w-full py-4">
        <NeuralThinkingIndicator isLoading={true} />
      </div>
    );
  }

  if (!response) return null;

  const {
    practical_explanation,
    indian_example,
    metaphor,
    visual_schema,
    professor_verification,
    mini_practice,
    encouragement,
    ask,
    student_emotion,
    visual_data, // Added visual_data to handle dynamic visuals
    teaching_visual // PRIORITY: Visual Professor Engine teaching visual
  } = response;

  // Debug: Log teaching_visual
  console.log('🎬 NeuroSymbolicResponse - teaching_visual:', teaching_visual);
  console.log('🎬 NeuroSymbolicResponse - visual_data:', visual_data);

  // Prefer backend-provided visual_data; otherwise derive from available fields
  const visualEngineData = useExistingVisualEngine(
    visual_data || { metaphor, practical_explanation, ask }
  );

  const hasRenderableVisual = Boolean(
    visualEngineData && (
      visualEngineData.scene_json?.elements?.length > 0 ||
      ['story_scene', 'svg', 'image'].includes(visualEngineData.type) ||
      visualEngineData.content?.src ||
      visualEngineData.src ||
      (typeof visualEngineData.content === 'string' && visualEngineData.content.trim().length > 0)
    )
  );

  // Chemistry-first rollout for teaching orchestrator
  const subjectGuess = String(
    response?.subject ||
    response?.topic_subject ||
    visualEngineData?.subject ||
    visualEngineData?.domain ||
    visualEngineData?.topic_subject ||
    ''
  ).toLowerCase();
  const topicGuess = response?.topic || response?.concept || (typeof ask === 'string' ? ask : 'Concept');
  const textBlob = [topicGuess, metaphor, practical_explanation, ask].filter(Boolean).join(' ').toLowerCase();
  const teachesChemistry = subjectGuess === 'chemistry' || /(atomic structure|electron(ic)? configuration|bohr|shell|orbital)/i.test(textBlob);
  const shouldUseTeaching = teachesChemistry;
  const isAtomicConfig = /(atomic structure|electron(ic)? configuration|bohr|shell|orbital)/i.test(textBlob);

  return (
    <div className="space-y-4 my-4">
      {/* Emotion indicator (subtle) */}
      {student_emotion && student_emotion !== 'neutral' && (
        <div className="text-xs text-gray-500 italic">
          Tone adapted for: {student_emotion.replace('_', ' ')}
        </div>
      )}

      {/* 1. Practical Explanation */}
      {practical_explanation && (
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center space-x-2 mb-3">
            <span className="text-2xl">👋</span>
            <h3 className="font-semibold text-gray-900">Practical Explanation</h3>
          </div>
          <div className="text-gray-800 leading-relaxed whitespace-pre-wrap">
            {practical_explanation}
          </div>
        </div>
      )}

      {/* 2. Indian Example */}
      {indian_example && (
        <div className="bg-gradient-to-r from-orange-50 to-yellow-50 rounded-xl border border-orange-200 p-6">
          <div className="flex items-center space-x-2 mb-3">
            <span className="text-2xl">🇮🇳</span>
            <h3 className="font-semibold text-gray-900">Indian Practical Example</h3>
          </div>
          <div className="text-gray-800 leading-relaxed whitespace-pre-wrap">
            {indian_example}
          </div>
        </div>
      )}

      {/* 3. Metaphor */}
      {metaphor && (
        <div className="bg-gradient-to-r from-pink-50 to-rose-50 rounded-xl border border-pink-200 p-6">
          <div className="flex items-center space-x-2 mb-3">
            <span className="text-2xl">🎭</span>
            <h3 className="font-semibold text-gray-900">Memory Hook</h3>
          </div>
          <div className="text-gray-800 leading-relaxed italic font-medium whitespace-pre-wrap">
            {metaphor}
          </div>
        </div>
      )}

      {/* 4. Visual Schema */}
      {visual_schema && (
        <VisualSchema schema={visual_schema} />
      )}

      {/* PRIORITY 0: Visual Professor Engine Teaching Visual (ALWAYS USE IF EXISTS) */}
      {teaching_visual && teaching_visual.stages && teaching_visual.stages.length > 0 ? (
        <div className="w-full my-4">
          <div className="bg-gradient-to-r from-purple-50 to-indigo-50 rounded-xl border-2 border-purple-200 p-2">
            <div className="text-xs text-purple-600 font-semibold mb-2 px-2">
              🎓 Professor-Led Visual Explanation
            </div>
            <TeachingVisualPlayer
              visualData={teaching_visual}
              onComplete={(result) => {
                console.log('✅ Teaching visual completed:', result);
              }}
              onInteraction={(interaction) => {
                console.log('👆 Teaching visual interaction:', interaction);
              }}
            />
          </div>
        </div>
      ) : null}

      {/* 5. Dynamic Visual Story Scene (LEGACY - Only if teaching_visual not available) */}
      {!teaching_visual && shouldUseTeaching ? (
        /covalent/i.test(textBlob) ? (
          <CovalentInteractiveCard />
        ) : isAtomicConfig ? (
          <AtomicInteractiveCard visualData={(atomicStructure({ complexity: 'simple' }).scene)} />
        ) : (
          <SmartTeachingVisual
            topic={topicGuess}
            subject={subjectGuess || 'chemistry'}
            visualData={visualEngineData}
            complexity="simple"
          />
        )
      ) : hasRenderableVisual ? (
        <VisualConceptBlock visualData={visualEngineData} />
      ) : (
        <div className="p-4 bg-purple-50 border border-purple-200 rounded">
          <div className="text-sm text-purple-800">
            Learning about {String(metaphor || practical_explanation || 'this concept').slice(0, 50)}
          </div>
        </div>
      )}

      {/* 6. Sketch Animator for real-time explanations */}
      <SketchAnimator explanation={practical_explanation} />

      {/* 7. Professor Verification (Collapsible) */}
      {professor_verification && (
        <ProfessorVerification verification={professor_verification} />
      )}

      {/* 8. Mini Practice */}
      {mini_practice && (
        <MiniPractice practice={mini_practice} />
      )}

      {/* 9. Encouragement */}
      {encouragement && (
        <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl border border-green-200 p-6">
          <div className="flex items-center space-x-2 mb-3">
            <span className="text-2xl">✨</span>
            <h3 className="font-semibold text-gray-900">Encouragement</h3>
          </div>
          <div className="text-gray-800 leading-relaxed whitespace-pre-wrap">
            {encouragement}
          </div>
        </div>
      )}

      {/* 10. Ask / Follow-up */}
      {ask && (
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border border-blue-200 p-6">
          <div className="flex items-center space-x-2 mb-3">
            <span className="text-2xl">➕</span>
            <h3 className="font-semibold text-gray-900">What's Next?</h3>
          </div>
          <div className="text-gray-800 leading-relaxed whitespace-pre-wrap">
            {ask}
          </div>
        </div>
      )}
    </div>
  );
}
