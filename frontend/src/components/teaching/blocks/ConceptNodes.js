import React from 'react';

export default function ConceptNodes({ nodes = [], layout = 'row' }) {
  const grid = layout === 'grid';
  return (
    <div className={grid ? 'grid grid-cols-3 gap-3' : 'flex items-center justify-center gap-3 flex-wrap'}>
      {nodes.map((n) => (
        <div key={n.id} className="px-4 py-2 rounded-xl bg-indigo-50 border border-indigo-300 text-indigo-800 font-semibold">
          {n.label}
        </div>
      ))}
    </div>
  );
}

