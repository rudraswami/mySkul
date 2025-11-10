import React, { useState } from 'react';

export default function PredictCard({ question, expected }) {
  const [revealed, setRevealed] = useState(false);
  return (
    <div className="bg-white rounded-xl border-2 border-amber-200 p-4">
      <div className="text-sm font-semibold text-amber-700 mb-2">Predict</div>
      <p className="text-gray-900 text-sm mb-3">{question}</p>
      {!revealed ? (
        <button
          onClick={() => setRevealed(true)}
          className="px-3 py-1.5 rounded-lg bg-amber-500 text-white hover:bg-amber-600 text-sm"
        >
          Check
        </button>
      ) : (
        <div className="mt-2 bg-amber-50 border border-amber-300 text-amber-900 rounded-lg px-3 py-2 text-sm">
          {expected}
        </div>
      )}
    </div>
  );
}

