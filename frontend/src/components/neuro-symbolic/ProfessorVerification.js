/**
 * Professor Verification Component
 * Collapsible section with steps, source, and confidence
 */
import React, { useState } from 'react';
import { ChevronDown, ChevronUp, CheckCircle, AlertCircle } from 'lucide-react';

export default function ProfessorVerification({ verification }) {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!verification) return null;

  const { steps, source, confidence, note } = verification;

  // Determine confidence level
  const getConfidenceColor = () => {
    if (confidence >= 0.9) return 'text-green-600';
    if (confidence >= 0.7) return 'text-blue-600';
    if (confidence >= 0.5) return 'text-yellow-600';
    return 'text-orange-600';
  };

  const getConfidenceLabel = () => {
    if (confidence >= 0.9) return 'Very High';
    if (confidence >= 0.7) return 'High';
    if (confidence >= 0.5) return 'Moderate';
    return 'Needs Verification';
  };

  return (
    <div className="bg-gradient-to-r from-purple-50 to-indigo-50 rounded-xl border border-purple-200 p-4 my-4">
      {/* Header - Always visible */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between hover:bg-white/50 p-2 rounded-lg transition-colors"
      >
        <div className="flex items-center space-x-2">
          <span className="text-2xl">✅</span>
          <h3 className="font-semibold text-gray-900">Professor Verification</h3>
          <span className={`text-sm font-medium ${getConfidenceColor()}`}>
            ({getConfidenceLabel()})
          </span>
        </div>
        {isExpanded ? (
          <ChevronUp className="h-5 w-5 text-gray-600" />
        ) : (
          <ChevronDown className="h-5 w-5 text-gray-600" />
        )}
      </button>

      {/* Confidence indicator - Always visible */}
      <div className="mt-2 mb-3 px-2">
        <div className="flex items-center justify-between text-sm text-gray-600 mb-1">
          <span>Confidence Score</span>
          <span className={`font-semibold ${getConfidenceColor()}`}>
            {(confidence * 100).toFixed(0)}%
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all ${
              confidence >= 0.9 ? 'bg-green-500' :
              confidence >= 0.7 ? 'bg-blue-500' :
              confidence >= 0.5 ? 'bg-yellow-500' : 'bg-orange-500'
            }`}
            style={{ width: `${confidence * 100}%` }}
          />
        </div>
      </div>

      {/* Expanded content */}
      {isExpanded && (
        <div className="mt-4 space-y-4 animate-fadeIn">
          {/* Steps */}
          {steps && steps.length > 0 && (
            <div className="bg-white rounded-lg p-4 border border-purple-100">
              <h4 className="font-medium text-gray-900 mb-3 flex items-center">
                <CheckCircle className="h-4 w-4 mr-2 text-purple-600" />
                Step-by-step Verification
              </h4>
              <ol className="space-y-2">
                {steps.map((step, index) => (
                  <li key={index} className="flex items-start">
                    <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-purple-100 text-purple-700 text-xs font-semibold mr-3 flex-shrink-0 mt-0.5">
                      {index + 1}
                    </span>
                    <span className="text-sm text-gray-700 leading-relaxed">
                      {step}
                    </span>
                  </li>
                ))}
              </ol>
            </div>
          )}

          {/* Source */}
          {source && (
            <div className="bg-white rounded-lg p-4 border border-purple-100">
              <h4 className="font-medium text-gray-900 mb-2 flex items-center">
                <span className="text-lg mr-2">📚</span>
                Reference Source
              </h4>
              <p className="text-sm text-gray-700 leading-relaxed">
                {source}
              </p>
            </div>
          )}

          {/* Note (if present) */}
          {note && (
            <div className="bg-yellow-50 rounded-lg p-4 border border-yellow-200">
              <div className="flex items-start">
                <AlertCircle className="h-5 w-5 text-yellow-600 mr-2 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-yellow-800 leading-relaxed">
                  {note}
                </p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
