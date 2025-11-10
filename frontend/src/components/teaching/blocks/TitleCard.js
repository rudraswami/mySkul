import React from 'react';

export default function TitleCard({ title, subtitle }) {
  return (
    <div className="bg-white/90 backdrop-blur-sm rounded-2xl p-5 shadow-lg border-2 border-purple-200 text-center">
      <h3 className="text-lg font-extrabold text-purple-800">{title}</h3>
      {subtitle && (
        <p className="text-sm mt-1 text-purple-600">{subtitle}</p>
      )}
    </div>
  );
}

