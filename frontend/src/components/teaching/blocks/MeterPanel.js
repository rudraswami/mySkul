import React from 'react';
import { motion } from 'framer-motion';

function evalExpr(expr, params) {
  try {
    const fn = new Function('x', 'params', 'with(params){ return ' + expr.replace('y =', '').replace('y=', '') + '; }');
    return fn(0, params);
  } catch {
    return NaN;
  }
}

export default function MeterPanel({ meters = [], params }) {
  return (
    <div className="bg-white rounded-xl border-2 border-emerald-200 p-4">
      <div className="text-sm font-semibold text-emerald-700 mb-2">Meters</div>
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
        {meters.map((m) => {
          const val = evalExpr(m.expr, params);
          return (
            <div key={m.id} className="rounded-lg border border-emerald-300 p-3 bg-emerald-50 text-emerald-900">
              <div className="text-xs opacity-80">{m.label}</div>
              <motion.div
                key={Number.isFinite(val) ? val.toFixed(2) : 'nan'}
                initial={{ scale: 0.95, opacity: 0.7 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ duration: 0.2 }}
                className="text-lg font-bold"
              >
                {Number.isFinite(val) ? val.toFixed(2) : '—'} <span className="text-xs font-medium">{m.unit}</span>
              </motion.div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
