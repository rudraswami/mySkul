import React from 'react';

export default function TeachingCard({ title, subtitle, icon = null, children }) {
  return (
    <div className="w-full rounded-3xl border border-slate-200 bg-white/95 shadow-xl overflow-hidden">
      {(title || subtitle) && (
        <div className="px-5 pt-5 pb-3 bg-gradient-to-r from-slate-50 to-white border-b border-slate-100">
          <div className="flex items-center gap-3">
            {icon && <div className="w-7 h-7 text-indigo-600">{icon}</div>}
            <div>
              {title && <div className="text-base font-semibold text-slate-900">{title}</div>}
              {subtitle && <div className="text-xs text-slate-600 mt-0.5">{subtitle}</div>}
            </div>
          </div>
        </div>
      )}
      <div className="p-4">
        {children}
      </div>
    </div>
  );
}




