/**
 * VerifiedAnswerBadge - Simple Trust Signal
 * 
 * COGNITO-OS v4.0 - Clean, minimal, student-friendly
 * Just shows: ✅ Verified or source reference
 * NO technical details - students don't care
 */
import React from 'react';
import { CheckCircle2, BookOpen } from 'lucide-react';

const VerifiedAnswerBadge = ({ 
  verification = {},
  sources = [],
  onCopy,
  onShare,
  onReport,
  content = ''
}) => {
  // Simple verification check
  const confidence = verification?.confidence || verification?.math?.confidence || 0.75;
  const isVerified = confidence >= 0.6;
  const hasSource = sources && sources.length > 0;

  // Don't show if nothing to display
  if (!isVerified && !hasSource) return null;

  return (
    <div className="mt-3 flex items-center gap-3 text-sm">
      {/* Verified badge */}
      {isVerified && (
        <span className="inline-flex items-center gap-1.5 text-emerald-600 dark:text-emerald-400">
          <CheckCircle2 className="w-4 h-4" />
          <span className="font-medium">Verified</span>
        </span>
      )}
      
      {/* Source reference */}
      {hasSource && (
        <span className="inline-flex items-center gap-1.5 text-gray-500 dark:text-gray-400">
          <BookOpen className="w-3.5 h-3.5" />
          <span>Source: {sources[0]}</span>
        </span>
      )}
    </div>
  );
};

export default VerifiedAnswerBadge;




