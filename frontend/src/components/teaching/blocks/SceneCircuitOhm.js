import React from 'react';

export default function SceneCircuitOhm({ params }) {
  const V = params.V ?? 0;
  const R = params.R ?? 1;
  const I = V / R;
  const width = 560, height = 120;
  const brightness = Math.max(0, Math.min(1, I / 5)); // normalize
  const bulbFill = `rgba(245, 158, 11, ${0.2 + 0.6*brightness})`;

  return (
    <div className="bg-gradient-to-br from-yellow-50 to-orange-50 rounded-xl border-2 border-orange-200 p-3">
      <svg width={width} height={height}>
        {/* simple circuit line */}
        <polyline points="40,60 200,60 200,80 360,80 360,60 520,60" fill="none" stroke="#7C2D12" strokeWidth="2" />
        {/* battery */}
        <line x1="60" y1="48" x2="60" y2="72" stroke="#1F2937" strokeWidth="2" />
        <line x1="70" y1="44" x2="70" y2="76" stroke="#1F2937" strokeWidth="4" />
        <text x="50" y="30" fontSize="10" fill="#111">V={V}</text>
        {/* resistor */}
        <rect x="280" y="52" width="60" height="16" rx="4" fill="#FDE68A" stroke="#92400E" />
        <text x="280" y="45" fontSize="10" fill="#111">R={R}Ω</text>
        {/* bulb */}
        <circle cx="440" cy="60" r="16" fill={bulbFill} stroke="#92400E" />
        <text x="430" y="95" fontSize="10" fill="#111">I={I.toFixed(2)}A</text>
      </svg>
    </div>
  );
}

