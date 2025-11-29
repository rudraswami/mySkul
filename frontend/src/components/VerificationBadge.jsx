/**
 * VerificationBadge - Shows trust signals for AI responses
 * 
 * Part of the Cognitive OS integration - displays verification status
 * to help students trust the accuracy of AI responses.
 */

import React from 'react';

const BADGE_STYLES = {
  verified: {
    bg: 'bg-emerald-50',
    border: 'border-emerald-200',
    text: 'text-emerald-700',
    icon: '✓',
    label: 'Verified'
  },
  high_confidence: {
    bg: 'bg-blue-50',
    border: 'border-blue-200',
    text: 'text-blue-700',
    icon: '◉',
    label: 'High Confidence'
  },
  needs_review: {
    bg: 'bg-amber-50',
    border: 'border-amber-200',
    text: 'text-amber-700',
    icon: '⚠',
    label: 'Review Suggested'
  },
  unverified: {
    bg: 'bg-gray-50',
    border: 'border-gray-200',
    text: 'text-gray-600',
    icon: '○',
    label: 'AI Generated'
  }
};

/**
 * Determine badge type from verification data
 */
function getBadgeType(verification) {
  if (!verification) return 'unverified';
  
  const { is_verified, confidence, status } = verification;
  
  if (status === 'verified' && is_verified && confidence >= 0.9) {
    return 'verified';
  }
  if (is_verified && confidence >= 0.7) {
    return 'high_confidence';
  }
  if (!is_verified || confidence < 0.5) {
    return 'needs_review';
  }
  
  return 'unverified';
}

/**
 * VerificationBadge Component
 * 
 * Props:
 * - verification: Object with { is_verified, confidence, status, issues }
 * - showDetails: Boolean to show expanded details
 * - className: Additional CSS classes
 */
export default function VerificationBadge({ 
  verification, 
  showDetails = false,
  className = '' 
}) {
  const badgeType = getBadgeType(verification);
  const style = BADGE_STYLES[badgeType];
  
  const confidence = verification?.confidence 
    ? Math.round(verification.confidence * 100) 
    : null;
  
  return (
    <div className={`inline-flex items-center gap-2 ${className}`}>
      {/* Main Badge */}
      <span 
        className={`
          inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium
          ${style.bg} ${style.border} ${style.text} border
          transition-all duration-200 hover:shadow-sm
        `}
        title={verification ? `Confidence: ${confidence}%` : 'Not verified'}
      >
        <span className="text-sm">{style.icon}</span>
        <span>{style.label}</span>
        {confidence !== null && showDetails && (
          <span className="opacity-75">({confidence}%)</span>
        )}
      </span>
      
      {/* Curriculum Sources Indicator */}
      {verification?.sources_used?.length > 0 && (
        <span 
          className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs 
                     bg-indigo-50 text-indigo-600 border border-indigo-100"
          title={`Based on ${verification.sources_used.length} curriculum sources`}
        >
          <span>📚</span>
          <span>Curriculum Grounded</span>
        </span>
      )}
    </div>
  );
}

/**
 * Compact version for inline use
 */
export function VerificationBadgeCompact({ verification }) {
  const badgeType = getBadgeType(verification);
  const style = BADGE_STYLES[badgeType];
  
  return (
    <span 
      className={`
        inline-flex items-center justify-center w-5 h-5 rounded-full text-xs
        ${style.bg} ${style.text}
      `}
      title={style.label}
    >
      {style.icon}
    </span>
  );
}

/**
 * Detailed verification card for expanded view
 */
export function VerificationDetails({ verification }) {
  if (!verification) {
    return (
      <div className="p-3 bg-gray-50 rounded-lg text-sm text-gray-600">
        Verification not available for this response.
      </div>
    );
  }
  
  const { is_verified, confidence, issues, corrections, time_ms } = verification;
  
  return (
    <div className="p-4 bg-white rounded-lg border border-gray-100 shadow-sm space-y-3">
      <div className="flex items-center justify-between">
        <VerificationBadge verification={verification} showDetails />
        {time_ms && (
          <span className="text-xs text-gray-400">
            Verified in {Math.round(time_ms)}ms
          </span>
        )}
      </div>
      
      {/* Issues Found */}
      {issues && issues.length > 0 && (
        <div className="space-y-1">
          <p className="text-xs font-medium text-amber-700">⚠️ Potential Issues:</p>
          <ul className="text-xs text-amber-600 space-y-1 pl-4">
            {issues.slice(0, 3).map((issue, idx) => (
              <li key={idx} className="list-disc">
                {issue.message || issue}
              </li>
            ))}
          </ul>
        </div>
      )}
      
      {/* Corrections Suggested */}
      {corrections && corrections.length > 0 && (
        <div className="space-y-1">
          <p className="text-xs font-medium text-blue-700">💡 Suggestions:</p>
          <ul className="text-xs text-blue-600 space-y-1 pl-4">
            {corrections.slice(0, 3).map((correction, idx) => (
              <li key={idx} className="list-disc">
                {correction.suggestion || correction}
              </li>
            ))}
          </ul>
        </div>
      )}
      
      {/* All Clear */}
      {is_verified && (!issues || issues.length === 0) && (
        <p className="text-xs text-emerald-600 flex items-center gap-1">
          <span>✓</span>
          <span>No issues detected. Response verified against curriculum.</span>
        </p>
      )}
    </div>
  );
}

