import React from 'react';

export default function LawList({ laws = [] }) {
  return (
    <div className="bg-indigo-50 border-2 border-indigo-200 rounded-xl p-3">
      <div className="text-sm font-semibold text-indigo-800 mb-1">Named Laws</div>
      <ul className="space-y-1 text-sm">
        {laws.map((l, i) => (
          <li key={i} className="flex items-start gap-2">
            <span className="text-indigo-700 font-bold whitespace-nowrap truncate" title={l.name}>{l.name}</span>
            <span className="text-gray-800 truncate" title={l.summary}>{l.summary}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
