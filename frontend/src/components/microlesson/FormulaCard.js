import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Copy, Check } from 'lucide-react';
import { InlineMath, BlockMath } from 'react-katex';
import 'katex/dist/katex.min.css';

/**
 * FormulaCard - Styled card for displaying mathematical formulas with KaTeX
 * AI Tutor 2.1 micro-lesson component
 */
const FormulaCard = ({ formulas, title = 'Key Formula' }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = (formula) => {
    navigator.clipboard.writeText(formula);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (!formulas || formulas.length === 0) return null;

  // Clean formula for KaTeX (remove $$ delimiters if present)
  const cleanFormula = (formula) => {
    return formula.replace(/^\$\$|\$\$$/g, '').replace(/^\$|\$$/g, '').trim();
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: 0.1 }}
      className="p-6 rounded-xl bg-gradient-to-br from-violet-50 to-purple-50 border border-violet-100 shadow-sm mb-4"
    >
      <div className="flex items-start space-x-3">
        <div className="flex-shrink-0 mt-1">
          <div className="w-10 h-10 rounded-lg bg-white flex items-center justify-center shadow-sm">
            <span className="text-2xl">🧮</span>
          </div>
        </div>
        <div className="flex-1">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-lg font-semibold text-gray-900 font-poppins">
              {title}
            </h3>
            <button
              onClick={() => handleCopy(formulas[0])}
              className="p-2 hover:bg-white rounded-lg transition-colors"
              title="Copy formula"
            >
              {copied ? (
                <Check className="w-4 h-4 text-green-600" />
              ) : (
                <Copy className="w-4 h-4 text-gray-500" />
              )}
            </button>
          </div>
          
          <div className="bg-white p-4 rounded-lg">
            {typeof formulas === 'string' ? (
              <div className="text-center text-xl">
                <BlockMath math={cleanFormula(formulas)} />
              </div>
            ) : (
              <div className="space-y-3">
                {formulas.map((formula, index) => (
                  <div key={index} className="text-center text-xl">
                    <BlockMath math={cleanFormula(formula)} />
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default FormulaCard;