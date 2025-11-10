import React, { useMemo } from 'react';

function sampleSeries(expr, x_min, x_max, samples, params) {
  if (!expr || typeof expr !== 'string') return [];
  const exprClean = expr.replace('y =', '').replace('y=', '');
  const points = [];
  const step = (x_max - x_min) / Math.max((samples || 1) - 1, 1);
  let fn;
  try {
    // eslint-disable-next-line no-new-func
    fn = new Function('x', 'params', 'with(params){ return ' + exprClean + '; }');
  } catch {
    return [];
  }
  for (let i = 0; i < (samples || 1); i++) {
    const x = x_min + i * step;
    let y;
    try { y = fn(x, params || {}); } catch { y = NaN; }
    points.push([x, y]);
  }
  return points.filter((p) => Number.isFinite(p[1]));
}

export default function LivePlot({ x_label, y_label, expr, x_min, x_max, samples = 20, params, series }) {
  // Support either direct expr props or first series item
  const s0 = Array.isArray(series) && series.length > 0 ? series[0] : null;
  const effectiveExpr = expr || (s0 && s0.expr) || '';
  const xmin = (typeof x_min === 'number') ? x_min : (s0 && typeof s0.x_min === 'number' ? s0.x_min : 0);
  const xmax = (typeof x_max === 'number') ? x_max : (s0 && typeof s0.x_max === 'number' ? s0.x_max : 10);
  const step = s0 && typeof s0.step === 'number' ? s0.step : null;
  const effSamples = step ? Math.max(2, Math.floor((xmax - xmin) / Math.max(step, 1e-6)) + 1) : samples;

  const data = useMemo(
    () => sampleSeries(effectiveExpr, xmin, xmax, effSamples, params),
    [effectiveExpr, xmin, xmax, effSamples, params]
  );
  const width = 560, height = 140, pad = 30;
  const xs = data.map(p => p[0]);
  const ys = data.map(p => p[1]);
  const minX = Math.min(xmin, ...xs), maxX = Math.max(xmax, ...xs);
  const minY = Math.min(...ys, 0), maxY = Math.max(...ys, 1);
  const sx = (x) => pad + (x - minX) * (width - 2*pad) / (maxX - minX || 1);
  const sy = (y) => height - pad - (y - minY) * (height - 2*pad) / (maxY - minY || 1);
  const path = data.length ? 'M ' + data.map(([x,y]) => `${sx(x)} ${sy(y)}`).join(' L ') : '';

  return (
    <div className="bg-white rounded-xl border-2 border-blue-200 p-3">
      <svg width={width} height={height} className="text-blue-700">
        <rect x="1" y="1" width={width-2} height={height-2} rx="8" className="fill-white stroke-current opacity-30" />
        {/* axes */}
        <line x1={pad} y1={height-pad} x2={width-pad} y2={height-pad} stroke="currentColor" strokeWidth="1" />
        <line x1={pad} y1={pad} x2={pad} y2={height-pad} stroke="currentColor" strokeWidth="1" />
        <text x={width/2} y={height-6} textAnchor="middle" className="fill-blue-900" fontSize="10">{x_label}</text>
        <text x={12} y={height/2} textAnchor="middle" transform={`rotate(-90 12 ${height/2})`} className="fill-blue-900" fontSize="10">{y_label}</text>
        {path && <path d={path} fill="none" stroke="currentColor" strokeWidth="2" />}
      </svg>
    </div>
  );
}
