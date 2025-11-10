import React from 'react';

export default function WorkedExample({ steps = [], icon }) {
  return (
    <div className="bg-gradient-to-br from-yellow-50 to-orange-50 border-2 border-orange-200 rounded-xl p-4">
      <div className="flex items-center gap-2 mb-3">
        <span className="text-orange-600 text-sm font-semibold">Worked Example</span>
        {icon && <span className="text-xs text-orange-500">({icon})</span>}
      </div>
      <ol className="list-decimal ml-5 text-sm text-orange-900 space-y-1">
        {steps.map((s, i) => (
          <li key={i}>
            <span className="font-semibold">{s.label}:</span> <span>{s.detail}</span>
          </li>
        ))}
      </ol>
    </div>
  );
}

