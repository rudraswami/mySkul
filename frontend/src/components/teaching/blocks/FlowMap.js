import React from 'react';

export default function FlowMap({ nodes = [], edges = [] }) {
  // Map nodes to x positions evenly across
  const width = 560;
  const height = 120;
  const padding = 40;
  const step = nodes.length > 1 ? (width - padding * 2) / (nodes.length - 1) : 0;
  const nodePos = nodes.map((n, i) => ({ id: n.id, label: n.label, x: padding + i * step, y: height / 2 }));
  const pos = Object.fromEntries(nodePos.map(n => [n.id, n]));

  const jitter = (val, idx) => val + Math.sin((idx + 1) * 97) * 1.2;
  return (
    <div className="w-full flex items-center justify-center">
      <svg width={width} height={height} className="text-indigo-700">
        {edges.map((e, i) => {
          const a = pos[e.from_] || { x: padding, y: height/2 };
          const b = pos[e.to] || { x: width - padding, y: height/2 };
          const midx = jitter((a.x + b.x) / 2, i);
          return (
            <g key={i}>
              <path d={`M ${a.x} ${a.y} Q ${midx} ${a.y - 20 + Math.sin((i+2)*53)} ${b.x} ${b.y}`} stroke="currentColor" strokeWidth="2" fill="none" />
              <polygon points={`${b.x},${b.y} ${b.x-8},${b.y-5} ${b.x-8},${b.y+5}`} fill="currentColor" />
              {e.label && <text x={midx} y={a.y-12} textAnchor="middle" className="fill-indigo-700" fontSize="10">{e.label}</text>}
            </g>
          );
        })}
        {nodePos.map((n, i) => (
          <g key={i}>
            <rect x={n.x-50 + Math.sin((i+1)*29)} y={n.y-18 + Math.cos((i+1)*37)} width="100" height="36" rx="10" className="fill-white stroke-current"/>
            <text x={n.x} y={n.y+4} textAnchor="middle" className="fill-indigo-800" fontSize="12">{n.label}</text>
          </g>
        ))}
      </svg>
    </div>
  );
}
