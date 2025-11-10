import React from 'react';

export default function DefinitionCard({ term, definition }) {
  return (
    <div className="bg-white rounded-xl border-2 border-purple-200 p-4 shadow-sm">
      <div className="text-sm text-purple-700 font-semibold">Definition</div>
      <div className="mt-1">
        <span className="font-bold text-gray-900">{term}:</span>
        <span className="ml-2 text-gray-700">{definition}</span>
      </div>
    </div>
  );
}

