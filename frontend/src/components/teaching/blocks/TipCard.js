import React from 'react';

export default function TipCard({ text, tip_type }) {
  const tone = {
    mistake: 'bg-red-50 border-red-300 text-red-900',
    hack: 'bg-purple-50 border-purple-300 text-purple-900',
    pyq: 'bg-amber-50 border-amber-300 text-amber-900',
    exam: 'bg-green-50 border-green-300 text-green-900',
  }[tip_type || 'exam'];

  return (
    <div className={`rounded-xl border-2 p-3 text-sm ${tone}`}>
      {text}
    </div>
  );
}

