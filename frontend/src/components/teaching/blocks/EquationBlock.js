import React from 'react';
// react-katex is optional at runtime; guard to prevent crash if unavailable
let BlockMathComp = null;
try {
  // Defer requiring to avoid bundler/import-time failures
  // Note: this will be tree-shaken if react-katex is present
  // eslint-disable-next-line global-require
  const rk = require('react-katex');
  BlockMathComp = rk && rk.BlockMath ? rk.BlockMath : null;
  try { require('katex/dist/katex.min.css'); } catch {}
} catch {}

export default function EquationBlock({ tex, highlight }) {
  if (!tex) return null;

  const renderMath = () => {
    if (BlockMathComp) {
      return <BlockMathComp math={tex} />;
    }
    // Fallback: show raw TeX in code style to avoid runtime error
    return (
      <code className="text-blue-800 text-lg bg-blue-50 px-2 py-1 rounded">
        {String(tex)}
      </code>
    );
  };

  return (
    <div className="bg-white rounded-xl p-3 sm:p-4 border-2 border-blue-200 shadow-sm flex items-center justify-center">
      <div className="text-lg sm:text-2xl text-blue-800 max-w-full overflow-x-auto">
        <div className="min-w-0 inline-block">
          {renderMath()}
        </div>
      </div>
      {highlight && (
        <span className="ml-3 px-2 py-1 rounded bg-yellow-100 border border-yellow-300 text-yellow-900 text-xs font-semibold">{highlight}</span>
      )}
    </div>
  );
}
