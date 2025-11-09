import React from 'react';

/**
 * MicroEngagementOverlay
 * Small, optional quiz/reflection card to reinforce understanding.
 * Non-blocking; emits analytics via onEvent.
 */
export default function MicroEngagementOverlay({ check, onAnswer, compact = true }) {
  if (!check) return null;

  return (
    <div className={`mt-3 ${compact ? 'text-sm' : ''}`}>
      <div className="rounded-xl border border-amber-200 bg-amber-50 p-3">
        <div className="font-medium text-amber-900 mb-2">Quick Check</div>
        <div className="text-amber-900 mb-3">{check.prompt}</div>
        <div className="flex flex-wrap gap-2">
          {(check.options || []).map((opt) => (
            <button
              key={opt.id}
              onClick={() => onAnswer?.(opt.id)}
              className="px-3 py-1.5 rounded-lg bg-white border border-amber-200 hover:bg-amber-100"
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

