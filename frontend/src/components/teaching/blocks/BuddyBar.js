import React from 'react';

const SUBJECT_EMOJI = {
  physics: '⚙️',
  chemistry: '🧪',
  biology: '🌿',
  mathematics: '📐',
  math: '📐',
  english: '📚',
};

export default function BuddyBar({ text, subject }) {
  const emoji = SUBJECT_EMOJI[(subject || '').toLowerCase()] || '👋';
  if (!text) return null;
  return (
    <div className="w-full max-w-2xl bg-white/85 backdrop-blur-sm border border-gray-200 rounded-xl px-4 py-3 shadow-sm">
      <div className="flex items-start gap-2 text-sm text-gray-800">
        <div className="w-6 h-6 rounded-full bg-purple-100 flex items-center justify-center flex-shrink-0">
          <span style={{fontSize:'14px'}}>{emoji}</span>
        </div>
        <p className="leading-relaxed">{text}</p>
      </div>
    </div>
  );
}

