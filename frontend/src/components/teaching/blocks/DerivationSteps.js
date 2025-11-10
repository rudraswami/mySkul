import React from 'react';

export default function DerivationSteps({ steps = [] }) {
  return (
    <div className="bg-white rounded-xl border-2 border-blue-200 p-4">
      <div className="text-sm font-semibold text-blue-700 mb-2">Derivation</div>
      <ol className="list-decimal ml-5 space-y-1 text-sm">
        {steps.map((s, i) => (
          <li key={i}>
            <span className="text-gray-800">{s.text}</span>
            {s.highlight && <span className="ml-2 px-2 py-0.5 rounded bg-yellow-100 border border-yellow-300 text-yellow-900 text-xs">{s.highlight}</span>}
          </li>
        ))}
      </ol>
    </div>
  );
}

