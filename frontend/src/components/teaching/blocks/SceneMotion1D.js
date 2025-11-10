import React, { useMemo } from 'react';
import { motion } from 'framer-motion';

export default function SceneMotion1D({ params, tMax = 2, style = 'cart' }) {
  const u = params.u ?? 0;
  const a = params.a ?? (params.a === 0 ? 0 : params.a) ?? (params.F && params.m ? params.F/params.m : 0);
  const v2 = u + a * tMax;

  const width = 560, height = 120;
  const cartX = 80;
  return (
    <div className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-xl border-2 border-purple-200 p-3">
      <svg width={width} height={height}>
        {/* ground */}
        <line x1="20" y1="90" x2={width-20} y2="90" stroke="#848" strokeWidth="1.5" />
        {/* object */}
        {style === 'ball' ? (
          <circle cx={cartX+30} cy="70" r="14" fill="#F59E0B" stroke="#92400E" />
        ) : (
          <rect x={cartX} y="60" width="60" height="25" rx="6" fill="#6EE7B7" stroke="#065F46" />
        )}
        {/* velocity arrow */}
        <Arrow x={cartX+30} y={55} len={Math.min(80, u*12)} color="#2563EB" label={`u=${u.toFixed(1)} m/s`} />
        {/* accel arrow with tiny wiggle when a changes */}
        <Arrow x={cartX+30} y={30} len={Math.min(80, a*12)} color="#F59E0B" label={`a=${a.toFixed(1)} m/s²`} wiggleKey={Math.round(a*100)} />
        {/* v after t */}
        <text x={cartX+140} y={40} fontSize="11" fill="#111">v@{tMax}s = {v2.toFixed(1)} m/s</text>
      </svg>
    </div>
  );
}

function Arrow({ x, y, len, color, label, wiggleKey }) {
  const x2 = x + len;
  const content = (
    <g>
      <line x1={x} y1={y} x2={x2} y2={y} stroke={color} strokeWidth="3" />
      <polygon points={`${x2},${y} ${x2-8},${y-5} ${x2-8},${y+5}`} fill={color} />
      <text x={x2+6} y={y+4} fontSize="10" fill="#111">{label}</text>
    </g>
  );
  if (typeof wiggleKey !== 'undefined') {
    return (
      <motion.g
        key={wiggleKey}
        initial={{ rotate: 0 }}
        animate={{ rotate: [0, -2, 2, 0] }}
        transition={{ duration: 0.35 }}
        style={{ transformOrigin: `${x}px ${y}px` }}
      >
        {content}
      </motion.g>
    );
  }
  return content;
}
