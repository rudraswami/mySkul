/**
 * AdaptiveMarkdown - Universal markdown + LaTeX renderer
 * 
 * Renders AI responses with full support for:
 * - LaTeX math (inline and block, multi-line)
 * - Markdown (headers, lists, bold, italic, code)
 * - Tables
 * - Chemical formulas
 * - Code blocks
 * 
 * Works across all AI response types (mentor, professor, unified)
 * 
 * PERFORMANCE OPTIMIZED:
 * - Memoized parsing (only re-parse when content changes)
 * - Lazy load KaTeX CSS (only when math content detected)
 */

import React, { useMemo, lazy, Suspense } from 'react';
import { motion } from 'framer-motion';

// Lazy load KaTeX components and CSS
const InlineMath = lazy(() => 
  import('react-katex').then(module => {
    import('katex/dist/katex.min.css');
    return { default: module.InlineMath };
  })
);

const BlockMath = lazy(() => 
  import('react-katex').then(module => {
    import('katex/dist/katex.min.css');
    return { default: module.BlockMath };
  })
);

/**
 * Pre-process text to extract and protect block math BEFORE line splitting
 * This handles multi-line \[...\] and $$...$$ blocks
 */
const extractBlockMath = (text) => {
  if (!text) return { processedText: text, blockMathMap: {} };
  
  const blockMathMap = {};
  let counter = 0;
  
  // Handle \[...\] block math (including multi-line)
  let processedText = text.replace(/\\\[([\s\S]*?)\\\]/g, (match, content) => {
    const placeholder = `__BLOCK_MATH_${counter}__`;
    blockMathMap[placeholder] = content.trim();
    counter++;
    return `\n${placeholder}\n`;
  });
  
  // Handle $$...$$ block math (including multi-line)
  processedText = processedText.replace(/\$\$([\s\S]*?)\$\$/g, (match, content) => {
    const placeholder = `__BLOCK_MATH_${counter}__`;
    blockMathMap[placeholder] = content.trim();
    counter++;
    return `\n${placeholder}\n`;
  });
  
  // Handle \begin{equation}...\end{equation}
  processedText = processedText.replace(/\\begin\{equation\}([\s\S]*?)\\end\{equation\}/g, (match, content) => {
    const placeholder = `__BLOCK_MATH_${counter}__`;
    blockMathMap[placeholder] = content.trim();
    counter++;
    return `\n${placeholder}\n`;
  });
  
  // Handle \begin{align}...\end{align}
  processedText = processedText.replace(/\\begin\{align\*?\}([\s\S]*?)\\end\{align\*?\}/g, (match, content) => {
    const placeholder = `__BLOCK_MATH_${counter}__`;
    blockMathMap[placeholder] = content.trim();
    counter++;
    return `\n${placeholder}\n`;
  });
  
  return { processedText, blockMathMap };
};

/**
 * Parse markdown and render as React elements
 * ENHANCED: Full LaTeX support including multi-line blocks
 */
const parseMarkdown = (text, blockMathMap) => {
  if (!text) return null;
  
  const lines = text.split('\n');
  const elements = [];
  let currentList = [];
  let listType = null;
  let tableRows = [];
  let inCodeBlock = false;
  let codeBlockContent = [];
  let codeLanguage = '';
  
  const flushList = () => {
    if (currentList.length > 0) {
      const isOrdered = listType === 'ol';
      elements.push(
        <div key={`list-${elements.length}`} className="my-4 space-y-2">
          {currentList.map((item, i) => (
            <div 
              key={i} 
              className="flex items-start gap-3 group"
            >
              {/* Custom bullet/number styling - FIXED: Larger bullets, responsive text */}
              <span className={`flex-shrink-0 ${
                isOrdered 
                  ? 'w-6 h-6 sm:w-7 sm:h-7 rounded-full bg-gradient-to-br from-purple-500 to-indigo-600 text-white text-xs font-bold flex items-center justify-center shadow-sm'
                  : 'w-2.5 h-2.5 mt-1.5 sm:mt-2 rounded-full bg-gradient-to-br from-purple-400 to-indigo-500'
              }`}>
                {isOrdered ? i + 1 : ''}
              </span>
              <span className="text-sm sm:text-[15px] text-gray-700 dark:text-gray-200 leading-relaxed sm:leading-[1.7] flex-1">
                {renderInline(item)}
              </span>
            </div>
          ))}
        </div>
      );
      currentList = [];
      listType = null;
    }
  };
  
  const flushTable = () => {
    if (tableRows.length > 0) {
      // Filter out separator rows (|---|---|)
      const dataRows = tableRows.filter(row => !row.match(/^\|[\s\-:|]+\|$/));
      
      if (dataRows.length > 0) {
        const headerCells = dataRows[0].split('|').filter(c => c.trim());
        const bodyRows = dataRows.slice(1);
        
        elements.push(
          <div key={`table-${elements.length}`} className="relative overflow-x-auto my-4 rounded-lg border border-gray-200 dark:border-gray-700">
            {/* FIXED: Added border container for scroll visibility hint */}
            <table className="w-full border-collapse text-sm min-w-max">
              <thead>
                <tr className="bg-gradient-to-r from-purple-50 to-indigo-50 dark:from-purple-900/30 dark:to-indigo-900/30">
                  {headerCells.map((cell, i) => (
                    <th key={i} className="border border-gray-200 dark:border-gray-700 px-4 py-2 text-left font-semibold text-gray-800 dark:text-gray-200">
                      {renderInline(cell.trim())}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {bodyRows.map((row, rowIdx) => (
                  <tr key={rowIdx} className={rowIdx % 2 === 0 ? 'bg-white dark:bg-gray-900' : 'bg-gray-50 dark:bg-gray-800/50'}>
                    {row.split('|').filter(c => c.trim()).map((cell, cellIdx) => (
                      <td key={cellIdx} className="border border-gray-200 dark:border-gray-700 px-4 py-2 text-gray-700 dark:text-gray-300">
                        {renderInline(cell.trim())}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        );
      }
      tableRows = [];
    }
  };
  
  lines.forEach((line, index) => {
    const trimmed = line.trim();
    
    // Handle code blocks
    if (trimmed.startsWith('```')) {
      if (inCodeBlock) {
        // End code block - FIXED: Added copy button wrapper
        const codeContent = codeBlockContent.join('\n');
        const codeKey = `code-${elements.length}`;
        elements.push(
          <div key={codeKey} className="relative group my-3">
            <button
              onClick={() => {
                navigator.clipboard.writeText(codeContent);
              }}
              className="absolute top-2 right-2 px-2 py-1 text-xs bg-gray-700 hover:bg-gray-600 text-gray-300 rounded opacity-0 group-hover:opacity-100 transition-opacity"
              title="Copy code"
            >
              Copy
            </button>
            <pre className="bg-gray-900 text-gray-100 p-4 pr-16 rounded-lg overflow-x-auto text-sm font-mono">
              <code className={codeLanguage ? `language-${codeLanguage}` : ''}>
                {codeContent}
              </code>
            </pre>
          </div>
        );
        codeBlockContent = [];
        codeLanguage = '';
        inCodeBlock = false;
      } else {
        // Start code block
        flushList();
        flushTable();
        codeLanguage = trimmed.slice(3).trim();
        inCodeBlock = true;
      }
      return;
    }
    
    if (inCodeBlock) {
      codeBlockContent.push(line);
      return;
    }
    
    // Check for block math placeholder - Math-First Formatting: Each formula on separate line
    if (trimmed.match(/^__BLOCK_MATH_\d+__$/)) {
      flushList();
      flushTable();
      const latex = blockMathMap[trimmed];
      if (latex) {
        try {
          elements.push(
            <div key={`block-math-${index}`} className="my-4 py-3 px-4 overflow-x-auto bg-gray-50 dark:bg-gray-900/50 rounded-lg border-l-4 border-purple-400">
              <BlockMath math={latex} />
            </div>
          );
        } catch (e) {
          elements.push(
            <div key={`block-math-err-${index}`} className="my-4 text-center font-mono text-sm bg-red-50 dark:bg-red-900/20 p-3 rounded-lg text-red-600 dark:text-red-400 border-l-4 border-red-400">
              <span className="block text-xs mb-1 opacity-70">Math rendering error:</span>
              {latex}
            </div>
          );
        }
      }
      return;
    }
    
    // Empty line - flush list/table and add spacing
    if (!trimmed) {
      flushList();
      flushTable();
      return;
    }
    
    // Table row detection
    if (trimmed.startsWith('|') && trimmed.endsWith('|')) {
      flushList();
      tableRows.push(trimmed);
      return;
    } else if (tableRows.length > 0) {
      // End of table
      flushTable();
    }
    
    // Headers - FIXED: Responsive font sizes for mobile
    if (trimmed.startsWith('#### ')) {
      flushList();
      elements.push(
        <h4 key={`h4-${index}`} className="text-sm sm:text-[15px] font-semibold text-gray-700 dark:text-gray-200 mt-4 sm:mt-5 mb-2 flex items-center gap-2">
          <span className="w-1 h-3.5 sm:h-4 bg-gradient-to-b from-purple-400 to-purple-600 rounded-full"></span>
          {renderInline(trimmed.slice(5))}
        </h4>
      );
      return;
    }
    
    if (trimmed.startsWith('### ')) {
      flushList();
      elements.push(
        <h3 key={`h3-${index}`} className="text-[15px] sm:text-[16px] font-semibold text-gray-800 dark:text-white mt-5 sm:mt-6 mb-2 sm:mb-3 flex items-center gap-2">
          <span className="w-1.5 h-4 sm:h-5 bg-gradient-to-b from-indigo-400 to-indigo-600 rounded-full"></span>
          {renderInline(trimmed.slice(4))}
        </h3>
      );
      return;
    }
    
    if (trimmed.startsWith('## ')) {
      flushList();
      elements.push(
        <h2 key={`h2-${index}`} className="text-base sm:text-[18px] font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-indigo-600 dark:from-purple-400 dark:to-indigo-400 mt-5 sm:mt-6 mb-2 sm:mb-3 pb-2 border-b border-purple-100 dark:border-purple-900/30">
          {renderInline(trimmed.slice(3))}
        </h2>
      );
      return;
    }
    
    if (trimmed.startsWith('# ')) {
      flushList();
      elements.push(
        <h1 key={`h1-${index}`} className="text-lg sm:text-[20px] font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-700 to-indigo-700 dark:from-purple-300 dark:to-indigo-300 mt-5 sm:mt-6 mb-3 sm:mb-4 pb-2 border-b-2 border-purple-200 dark:border-purple-800">
          {renderInline(trimmed.slice(2))}
        </h1>
      );
      return;
    }
    
    // Bullet list
    if (trimmed.match(/^[-*•]\s+/)) {
      if (listType !== 'ul') {
        flushList();
        listType = 'ul';
      }
      currentList.push(trimmed.replace(/^[-*•]\s+/, ''));
      return;
    }
    
    // Numbered list
    if (trimmed.match(/^\d+[.)]\s+/)) {
      if (listType !== 'ol') {
        flushList();
        listType = 'ol';
      }
      currentList.push(trimmed.replace(/^\d+[.)]\s+/, ''));
      return;
    }
    
    // Blockquote - ENHANCED: Better visual callout style
    if (trimmed.startsWith('>')) {
      flushList();
      // Check if it's a special callout type - FIXED: Use word boundaries to avoid false matches
      const calloutContent = trimmed.slice(1).trim();
      const lowerContent = calloutContent.toLowerCase();
      const isRemember = /\b(remember|key point|important)\b/.test(lowerContent);
      const isTip = /\b(tip|exam tip|hint|pro tip)\b/.test(lowerContent);
      const isWarning = /\b(warning|caution|avoid|don't|do not|never)\b/.test(lowerContent);
      
      let borderColor = 'border-purple-400 dark:border-purple-500';
      let bgColor = 'bg-purple-50 dark:bg-purple-900/20';
      let icon = '💡';
      
      if (isRemember) {
        borderColor = 'border-amber-400 dark:border-amber-500';
        bgColor = 'bg-amber-50 dark:bg-amber-900/20';
        icon = '🔑';
      } else if (isTip) {
        borderColor = 'border-emerald-400 dark:border-emerald-500';
        bgColor = 'bg-emerald-50 dark:bg-emerald-900/20';
        icon = '✨';
      } else if (isWarning) {
        borderColor = 'border-red-400 dark:border-red-500';
        bgColor = 'bg-red-50 dark:bg-red-900/20';
        icon = '⚠️';
      }
      
      elements.push(
        <blockquote key={`quote-${index}`} className={`border-l-4 ${borderColor} pl-4 py-3 my-4 ${bgColor} rounded-r-xl shadow-sm`}>
          <p className="text-gray-700 dark:text-gray-200 font-medium flex items-start gap-2">
            <span className="text-lg flex-shrink-0">{icon}</span>
            <span>{renderInline(calloutContent)}</span>
          </p>
        </blockquote>
      );
      return;
    }
    
    // Horizontal rule
    if (trimmed.match(/^[-*_]{3,}$/)) {
      flushList();
      elements.push(<hr key={`hr-${index}`} className="my-4 border-gray-200 dark:border-gray-700" />);
      return;
    }
    
    // Math-first formatting: Check if line contains math formulas
    const hasBlockMath = trimmed.match(/^\$\$|^\\\[|^\\begin\{(equation|align)/);
    const hasInlineMath = trimmed.match(/\$[^$]+\$|\\\([^)]+\\\)/);
    
    // If line contains block math or starts with formula, render separately
    if (hasBlockMath || (hasInlineMath && trimmed.length < 100)) {
      flushList();
      elements.push(
        <div key={`math-line-${index}`} className="my-4 py-2 px-3 bg-gray-50 dark:bg-gray-900/50 rounded-lg border-l-4 border-purple-400">
          {renderInline(trimmed)}
        </div>
      );
      return;
    }
    
    // Step labels detection - ENHANCED to catch more formats
    // Matches: "Step 1", "Step 2:", "1.", "1)", "Part A", "Phase 1", etc.
    const stepMatch = trimmed.match(/^(step\s*\d+[.:]?|step\s*[a-z][.:]?|part\s*[a-z\d][.:]?|phase\s*\d+[.:]?|\d{1,2}[.)]\s+|\([a-z\d]\)\s*)/i);
    if (stepMatch) {
      flushList();
      const stepLabel = stepMatch[0].trim();
      const stepContent = trimmed.slice(stepMatch[0].length).trim();
      // Extract step number/letter for badge
      const stepNum = stepMatch[1]?.match(/\d+/)?.[0] || stepMatch[1]?.match(/[a-z]/i)?.[0] || '';
      elements.push(
        <div key={`step-${index}`} className="my-4 flex items-start gap-3">
          <span className="flex-shrink-0 w-7 h-7 sm:w-8 sm:h-8 rounded-full bg-gradient-to-br from-purple-500 to-indigo-600 text-white text-xs font-bold flex items-center justify-center shadow-sm">
            {stepNum}
          </span>
          <div className="flex-1">
            <p className="text-sm sm:text-[15px] text-gray-700 dark:text-gray-200 mb-2 leading-relaxed sm:leading-[1.75]">
              {renderInline(stepContent)}
            </p>
          </div>
        </div>
      );
      return;
    }
    
    // Regular paragraph - FIXED: Responsive font sizes for mobile
    flushList();
    elements.push(
      <p key={`p-${index}`} className="text-sm sm:text-[15px] text-gray-700 dark:text-gray-200 mb-3 sm:mb-3.5 leading-relaxed sm:leading-[1.75]">
        {renderInline(trimmed)}
      </p>
    );
  });
  
  flushList();
  flushTable();
  return elements;
};

/**
 * Render inline markdown (bold, italic, code, links, LaTeX)
 * ENHANCED: Properly handles all inline LaTeX and special characters
 */
const renderInline = (text) => {
  if (!text) return null;
  
  const parts = [];
  let key = 0;
  
  // Pattern to match all inline elements including LaTeX
  // Order matters: more specific patterns first
  const patterns = [
    // LaTeX inline math
    { regex: /\\\((.+?)\\\)/g, type: 'inline-math' },         // \(...\)
    { regex: /\$([^\$\n]+)\$/g, type: 'inline-math' },        // $...$
    // Markdown formatting
    { regex: /\*\*\*([^*]+)\*\*\*/g, type: 'bold-italic' },   // ***bold italic***
    { regex: /\*\*([^*]+)\*\*/g, type: 'bold' },              // **bold**
    { regex: /__([^_]+)__/g, type: 'bold' },                  // __bold__
    { regex: /\*([^*]+)\*/g, type: 'italic' },                // *italic*
    { regex: /_([^_\s][^_]*[^_\s])_/g, type: 'italic' },      // _italic_ (not matching subscripts)
    { regex: /`([^`]+)`/g, type: 'code' },                    // `code`
    // Chemical subscripts/superscripts (like H₂O, CO₂)
    { regex: /([A-Z][a-z]?)(\d+)/g, type: 'chemical' },       // H2O, CO2, etc.
  ];
  
  // Find all matches with their positions
  const matches = [];
  
  patterns.forEach(({ regex, type }) => {
    let match;
    const r = new RegExp(regex.source, 'g');
    while ((match = r.exec(text)) !== null) {
      matches.push({
        start: match.index,
        end: match.index + match[0].length,
        content: match[1],
        extra: match[2], // For chemical formulas
        fullMatch: match[0],
        type
      });
    }
  });
  
  // Sort by position
  matches.sort((a, b) => a.start - b.start);
  
  // Remove overlapping matches (keep first/longest)
  const filteredMatches = [];
  let lastEnd = 0;
  matches.forEach(m => {
    if (m.start >= lastEnd) {
      filteredMatches.push(m);
      lastEnd = m.end;
    }
  });
  
  // Build result
  let currentPos = 0;
  
  filteredMatches.forEach(m => {
    // Add text before this match
    if (m.start > currentPos) {
      parts.push(<span key={key++}>{text.slice(currentPos, m.start)}</span>);
    }
    
    // Render the match based on type
    switch (m.type) {
      case 'inline-math':
        try {
          // FIXED: Reduced visual boxing - formulas should flow naturally in text
          // Only add subtle spacing, no background/border for inline formulas
          parts.push(
            <span key={key++} className="mx-0.5 text-purple-700 dark:text-purple-300 font-medium">
              <InlineMath math={m.content.trim()} />
            </span>
          );
        } catch (e) {
          parts.push(
            <code key={key++} className="text-red-500 bg-red-50 dark:bg-red-900/20 px-1 rounded text-sm">
              {m.content}
            </code>
          );
        }
        break;
      case 'bold-italic':
        parts.push(
          <strong key={key++} className="font-bold italic text-gray-900 dark:text-white">
            {m.content}
          </strong>
        );
        break;
      case 'bold':
        parts.push(
          <strong key={key++} className="font-bold text-gray-900 dark:text-white">
            {m.content}
          </strong>
        );
        break;
      case 'italic':
        parts.push(
          <em key={key++} className="italic text-gray-700 dark:text-gray-300">
            {m.content}
          </em>
        );
        break;
      case 'code':
        parts.push(
          <code key={key++} className="bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded text-sm font-mono text-purple-600 dark:text-purple-400">
            {m.content}
          </code>
        );
        break;
      case 'chemical':
        // Render chemical formula with subscript
        parts.push(
          <span key={key++} className="font-medium">
            {m.content}<sub className="text-xs">{m.extra}</sub>
          </span>
        );
        break;
      default:
        parts.push(<span key={key++}>{m.fullMatch}</span>);
    }
    
    currentPos = m.end;
  });
  
  // Add remaining text
  if (currentPos < text.length) {
    parts.push(<span key={key++}>{text.slice(currentPos)}</span>);
  }
  
  return parts.length > 0 ? parts : text;
};

/**
 * Main AdaptiveMarkdown component
 * PERFORMANCE OPTIMIZED: Memoized parsing
 */
const AdaptiveMarkdown = ({ content, className = '', animate = true }) => {
  // CRITICAL: Ensure content is a string, never an object
  const contentString = useMemo(() => {
    if (!content) return null;
    
    // If content is an object, try to extract string from it
    if (typeof content === 'object' && !Array.isArray(content)) {
      // PRIORITY ORDER for content extraction (handles all AI response formats)
      const extracted = 
        // Neuro-symbolic format: {default_view: {main_content: {content: "..."}}}
        content.default_view?.main_content?.content ||
        content.default_view?.greeting ||
        // Response wrapper: {response: {default_view: ...}}
        content.response?.default_view?.main_content?.content ||
        content.response?.main_response ||
        content.response?.content ||
        content.response?.text ||
        // Simple formats
        content.main_response ||
        content.text || 
        content.content || 
        content.message || 
        content.mainContent ||
        content.answer ||
        content.explanation ||
        // Progressive sections fallback
        content.progressive_sections?.explanation ||
        null;
      
      if (!extracted || typeof extracted !== 'string') {
        // Last resort: try to stringify if it's a simple value
        if (typeof content.response === 'string') {
          return content.response;
        }
        console.warn('⚠️ AdaptiveMarkdown: Could not extract string from object:', Object.keys(content));
        return null;
      }
      return extracted;
    } else if (typeof content !== 'string') {
      // Convert to string if possible
      if (typeof content === 'number' || Array.isArray(content)) {
        return String(content);
      } else {
        console.warn('⚠️ AdaptiveMarkdown: Invalid content type:', typeof content);
        return null;
      }
    }
    
    return content;
  }, [content]);
  
  // PERFORMANCE FIX: Memoize parsing - only re-parse when content changes
  const parsedContent = useMemo(() => {
    if (!contentString) return null;
    
    // Pre-process to extract block math
    const { processedText, blockMathMap } = extractBlockMath(contentString);
    
    // Parse markdown
    return parseMarkdown(processedText, blockMathMap);
  }, [contentString]);
  
  if (!parsedContent) return null;
  
  const Container = animate ? motion.div : 'div';
  const animationProps = animate ? {
    initial: { opacity: 0, y: 10 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.3 }
  } : {};
  
  return (
    <Suspense fallback={<div className="animate-pulse">Loading...</div>}>
      <Container
        className={`adaptive-markdown prose prose-gray dark:prose-invert max-w-none ${className}`}
        {...animationProps}
      >
        {parsedContent}
      </Container>
    </Suspense>
  );
};

export default AdaptiveMarkdown;
