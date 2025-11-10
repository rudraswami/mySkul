import React from 'react';

export default function EvidenceCallout({ text, source }) {
  return (
    <div className="bg-amber-50 border-2 border-amber-300 rounded-xl p-3 text-sm text-amber-900">
      <div className="font-semibold mb-1">Evidence</div>
      <div>{text}</div>
      {source && <div className="mt-1 text-xs opacity-80">Source: {source}</div>}
    </div>
  );
}

