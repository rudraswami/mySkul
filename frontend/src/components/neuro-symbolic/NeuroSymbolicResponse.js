/**
 * Neuro-Symbolic Response Container
 * Displays all 8 sections of the AI response
 */
import React from 'react';
import VisualSchema from './VisualSchema';
import ProfessorVerification from './ProfessorVerification';
import MiniPractice from './MiniPractice';
import VisualConceptBlock from './VisualConceptBlock'; // Importing the VisualConceptBlock
import SketchAnimator from './SketchAnimator'; // Importing the SketchAnimator
import { useExistingVisualEngine } from '../hooks/useExistingVisualEngine'; // Importing existing visual engine hook

export default function NeuroSymbolicResponse({ response, isLoading }) {
  if (isLoading) {
    return (
      <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-xl p-8 my-4">
        <div className="flex items-center justify-center space-x-3">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-purple-600"></div>
          <span className="text-gray-600">AI is thinking...</span>
        </div>
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
    visual_data // Added visual_data to handle dynamic visuals
  } = response;

  const visualEngineData = useExistingVisualEngine(visual_data); // Using existing visual engine

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

      {/* 5. Dynamic Visual Concept Block */}
      {visualEngineData && (
        <VisualConceptBlock visualData={visualEngineData} /> // Using the VisualConceptBlock for dynamic visuals
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
