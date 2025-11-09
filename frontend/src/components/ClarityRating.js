import React from 'react';

/**
 * ClarityRating
 * 1–5 quick clarity rating, compact UI.
 */
export default function ClarityRating({ value = 0, onRate }) {
  const options = [1, 2, 3, 4, 5];
  return (
    <div className="mt-3">
      <div className="text-sm text-gray-700 mb-1">Did this visual make it clear?</div>
      <div className="flex items-center gap-2">
        {options.map((n) => (
          <button
            key={n}
            aria-label={`Rate clarity ${n}`}
            onClick={() => onRate?.(n)}
            className={`px-2 py-1 rounded border text-sm ${
              value === n ? 'bg-green-600 text-white border-green-700' : 'bg-white border-gray-300 hover:bg-gray-50'
            }`}
          >
            {n}
          </button>
        ))}
      </div>
    </div>
  );
}

