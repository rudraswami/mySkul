import React from 'react';

export default function RelationArrows({ relations = [] }) {
  // Render a simple horizontal chain with arrows between conceptual IDs (labels not used for positions here).
  // For simplicity, we show them linearly.
  return (
    <div className="w-full flex items-center justify-center">
      <svg width="560" height="80" role="img" aria-label="relations" className="text-indigo-700">
        {relations.map((r, idx) => {
          const x1 = 40 + idx * 170;
          const x2 = x1 + 120;
          const y = 40;
          return (
            <g key={idx}>
              <path d={`M ${x1} ${y} Q ${(x1+x2)/2} ${y-18} ${x2} ${y}`} stroke="currentColor" strokeWidth="2" fill="none" />
              <polygon points={`${x2},${y} ${x2-8},${y-5} ${x2-8},${y+5}`} fill="currentColor" />
              {r.label && (
                <text x={(x1+x2)/2} y={y-10} textAnchor="middle" className="fill-indigo-700" fontSize="10">{r.label}</text>
              )}
            </g>
          );
        })}
      </svg>
    </div>
  );
}

