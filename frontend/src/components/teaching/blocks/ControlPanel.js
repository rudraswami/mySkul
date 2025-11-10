import React from 'react';

export default function ControlPanel({ sliders = [], toggles = [], params, onChange }) {
  return (
    <div className="bg-white rounded-xl border-2 border-gray-200 p-4">
      <div className="text-sm font-semibold text-gray-700 mb-2">Controls</div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {sliders.map((s) => (
          <div key={s.id}>
            <label className="text-xs text-gray-600 font-medium">{s.label}</label>
            <div className="flex items-center gap-3">
              <input
                type="range"
                min={s.min}
                max={s.max}
                step={s.step}
                value={params[s.id] ?? s.default}
                onChange={(e) => onChange(s.id, parseFloat(e.target.value))}
                className="w-full"
              />
              {(() => {
                const val = params[s.id] ?? s.default;
                const m = /\(([^)]+)\)\s*$/.exec(s.label || '');
                const unit = m ? m[1] : '';
                return (
                  <div className="min-w-[64px] text-right text-sm text-gray-800">
                    {val} {unit && <span className="text-xs text-gray-500">{unit}</span>}
                  </div>
                );
              })()}
            </div>
          </div>
        ))}
        {toggles.map((t) => (
          <div key={t.id} className="flex items-center justify-between border rounded-lg px-3 py-2 bg-gray-50">
            <span className="text-sm text-gray-700">{t.label}</span>
            <button
              type="button"
              onClick={() => onChange(t.id, !(params[t.id] ?? t.default))}
              className={`w-12 h-6 rounded-full transition-colors ${ (params[t.id] ?? t.default) ? 'bg-purple-600' : 'bg-gray-300'}`}
            >
              <span className={`block w-5 h-5 bg-white rounded-full transform transition-transform ${ (params[t.id] ?? t.default) ? 'translate-x-6' : 'translate-x-1'}`}></span>
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
