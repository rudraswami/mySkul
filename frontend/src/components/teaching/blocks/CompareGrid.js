import React from 'react';

export default function CompareGrid({ left, right }) {
  return (
    <div className="grid grid-cols-2 gap-3">
      <div className="bg-green-50 border-2 border-green-300 rounded-xl p-3">
        <h4 className="font-bold text-green-900 mb-1 truncate" title={left?.title}>{left?.title}</h4>
        <ul className="list-disc ml-5 text-sm text-green-800 space-y-1">
          {(left?.points || []).map((p, i) => (
            <li key={i} className="truncate" title={p}>{p}</li>
          ))}
        </ul>
      </div>
      <div className="bg-blue-50 border-2 border-blue-300 rounded-xl p-3">
        <h4 className="font-bold text-blue-900 mb-1 truncate" title={right?.title}>{right?.title}</h4>
        <ul className="list-disc ml-5 text-sm text-blue-800 space-y-1">
          {(right?.points || []).map((p, i) => (
            <li key={i} className="truncate" title={p}>{p}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
