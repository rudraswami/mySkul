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
 */

import React from 'react';
import { motion } from 'framer-motion';
import { InlineMath, BlockMath } from 'react-katex';
import 'katex/dist/katex.min.css';

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
              {/* Custom bullet/number styling */}
              <span className={`flex-shrink-0 ${
                isOrdered 
                  ? 'w-6 h-6 rounded-full bg-gradient-to-br from-purple-500 to-indigo-600 text-white text-xs font-bold flex items-center justify-center shadow-sm'
                  : 'w-2 h-2 mt-2 rounded-full bg-gradient-to-br from-purple-400 to-indigo-500'
              }`}>
                {isOrdered ? i + 1 : ''}
              </span>
              <span className="text-[15px] text-gray-700 dark:text-gray-200 leading-[1.7] flex-1">
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
          <div key={`table-${elements.length}`} className="overflow-x-auto my-4">
            <table className="w-full border-collapse text-sm">
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
        // End code block
        elements.push(
          <pre key={`code-${elements.length}`} className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto my-3 text-sm font-mono">
            <code className={codeLanguage ? `language-${codeLanguage}` : ''}>
              {codeBlockContent.join('\n')}
            </code>
          </pre>
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
    
    // Check for block math placeholder
    if (trimmed.match(/^__BLOCK_MATH_\d+__$/)) {
      flushList();
      flushTable();
      const latex = blockMathMap[trimmed];
      if (latex) {
        try {
          elements.push(
            <div key={`block-math-${index}`} className="my-4 py-3 overflow-x-auto bg-gradient-to-r from-blue-50/50 to-purple-50/50 dark:from-blue-900/10 dark:to-purple-900/10 rounded-lg">
              <BlockMath math={latex} />
            </div>
          );
        } catch (e) {
          elements.push(
            <div key={`block-math-err-${index}`} className="my-4 text-center font-mono text-sm bg-red-50 dark:bg-red-900/20 p-3 rounded-lg text-red-600 dark:text-red-400 border border-red-200 dark:border-red-800">
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
    
    // Headers - ENHANCED: Beautiful, visually appealing headers
    if (trimmed.startsWith('#### ')) {
      flushList();
      elements.push(
        <h4 key={`h4-${index}`} className="text-[15px] font-semibold text-gray-700 dark:text-gray-200 mt-5 mb-2 flex items-center gap-2">
          <span className="w-1 h-4 bg-gradient-to-b from-purple-400 to-purple-600 rounded-full"></span>
          {renderInline(trimmed.slice(5))}
        </h4>
      );
      return;
    }
    
    if (trimmed.startsWith('### ')) {
      flushList();
      elements.push(
        <h3 key={`h3-${index}`} className="text-[16px] font-semibold text-gray-800 dark:text-white mt-6 mb-3 flex items-center gap-2">
          <span className="w-1.5 h-5 bg-gradient-to-b from-indigo-400 to-indigo-600 rounded-full"></span>
          {renderInline(trimmed.slice(4))}
        </h3>
      );
      return;
    }
    
    if (trimmed.startsWith('## ')) {
      flushList();
      elements.push(
        <h2 key={`h2-${index}`} className="text-[18px] font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-indigo-600 dark:from-purple-400 dark:to-indigo-400 mt-6 mb-3 pb-2 border-b border-purple-100 dark:border-purple-900/30">
          {renderInline(trimmed.slice(3))}
        </h2>
      );
      return;
    }
    
    if (trimmed.startsWith('# ')) {
      flushList();
      elements.push(
        <h1 key={`h1-${index}`} className="text-[20px] font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-700 to-indigo-700 dark:from-purple-300 dark:to-indigo-300 mt-6 mb-4 pb-2 border-b-2 border-purple-200 dark:border-purple-800">
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
      // Check if it's a special callout type
      const calloutContent = trimmed.slice(1).trim();
      const isRemember = calloutContent.toLowerCase().includes('remember') || calloutContent.toLowerCase().includes('key');
      const isTip = calloutContent.toLowerCase().includes('tip') || calloutContent.toLowerCase().includes('exam');
      const isWarning = calloutContent.toLowerCase().includes('warning') || calloutContent.toLowerCase().includes('avoid') || calloutContent.toLowerCase().includes('don\'t');
      
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
    
    // Regular paragraph - IMPROVED: Better font size and line height
    flushList();
    elements.push(
      <p key={`p-${index}`} className="text-[15px] text-gray-700 dark:text-gray-200 mb-3.5 leading-[1.75]">
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
          parts.push(
            <span key={key++} className="mx-0.5">
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
 */
const AdaptiveMarkdown = ({ content, className = '', animate = true }) => {
  // CRITICAL: Ensure content is a string, never an object
  if (!content) return null;
  
  // If content is an object, try to extract string from it
  let contentString = content;
  if (typeof content === 'object' && !Array.isArray(content)) {
    // Try common fields
    contentString = content.text || content.content || content.message || content.mainContent || null;
    if (!contentString || typeof contentString !== 'string') {
      console.warn('⚠️ AdaptiveMarkdown: Received object instead of string, cannot render:', content);
      return null;
    }
  } else if (typeof content !== 'string') {
    // Convert to string if possible
    if (typeof content === 'number' || Array.isArray(content)) {
      contentString = String(content);
    } else {
      console.warn('⚠️ AdaptiveMarkdown: Invalid content type:', typeof content);
      return null;
    }
  }
  
  // Pre-process to extract block math
  const { processedText, blockMathMap } = extractBlockMath(contentString);
  
  const Container = animate ? motion.div : 'div';
  const animationProps = animate ? {
    initial: { opacity: 0, y: 10 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.3 }
  } : {};
  
  return (
    <Container
      className={`adaptive-markdown prose prose-gray dark:prose-invert max-w-none ${className}`}
      {...animationProps}
    >
      {parseMarkdown(processedText, blockMathMap)}
    </Container>
  );
};

export default AdaptiveMarkdown;
