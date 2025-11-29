/**
 * AdaptiveMarkdown - Clean markdown renderer
 * 
 * Renders AI responses as clean markdown WITHOUT forcing template sections.
 * Like ChatGPT/Gemini - the AI decides the structure, not the frontend.
 * 
 * FIXED: Now properly renders LaTeX math and tables
 */

import React from 'react';
import { motion } from 'framer-motion';
import { InlineMath, BlockMath } from 'react-katex';
import 'katex/dist/katex.min.css';

/**
 * Parse markdown and render as React elements
 * ENHANCED: Supports LaTeX math and tables
 */
const parseMarkdown = (text) => {
  if (!text) return null;
  
  const lines = text.split('\n');
  const elements = [];
  let currentList = [];
  let listType = null;
  let tableRows = [];
  let inCodeBlock = false;
  let codeBlockContent = [];
  
  const flushList = () => {
    if (currentList.length > 0) {
      const ListTag = listType === 'ol' ? 'ol' : 'ul';
      elements.push(
        <ListTag key={`list-${elements.length}`} className={listType === 'ol' ? 'list-decimal' : 'list-disc'} style={{ marginLeft: '1.5rem', marginBottom: '0.75rem' }}>
          {currentList.map((item, i) => (
            <li key={i} className="text-gray-800 dark:text-gray-200 mb-1">
              {renderInline(item)}
            </li>
          ))}
        </ListTag>
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
            <code>{codeBlockContent.join('\n')}</code>
          </pre>
        );
        codeBlockContent = [];
        inCodeBlock = false;
      } else {
        // Start code block
        flushList();
        flushTable();
        inCodeBlock = true;
      }
      return;
    }
    
    if (inCodeBlock) {
      codeBlockContent.push(line);
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
    
    // Block-level LaTeX (standalone \[...\] or $$...$$)
    if (trimmed.match(/^\\\[[\s\S]*\\\]$/) || trimmed.match(/^\$\$[\s\S]*\$\$$/)) {
      flushList();
      let latex = trimmed;
      if (latex.startsWith('\\[')) latex = latex.slice(2, -2);
      else if (latex.startsWith('$$')) latex = latex.slice(2, -2);
      
      try {
        elements.push(
          <div key={`block-math-${index}`} className="my-4 text-center overflow-x-auto">
            <BlockMath math={latex.trim()} />
          </div>
        );
      } catch (e) {
        elements.push(
          <div key={`block-math-err-${index}`} className="my-4 text-center font-mono text-sm bg-red-50 dark:bg-red-900/20 p-2 rounded text-red-600 dark:text-red-400">
            {latex}
          </div>
        );
      }
      return;
    }
    
    // Headers
    if (trimmed.startsWith('### ')) {
      flushList();
      elements.push(
        <h3 key={`h3-${index}`} className="text-lg font-semibold text-gray-900 dark:text-white mt-4 mb-2">
          {renderInline(trimmed.slice(4))}
        </h3>
      );
      return;
    }
    
    if (trimmed.startsWith('## ')) {
      flushList();
      elements.push(
        <h2 key={`h2-${index}`} className="text-xl font-bold text-gray-900 dark:text-white mt-4 mb-2">
          {renderInline(trimmed.slice(3))}
        </h2>
      );
      return;
    }
    
    if (trimmed.startsWith('# ')) {
      flushList();
      elements.push(
        <h1 key={`h1-${index}`} className="text-2xl font-bold text-gray-900 dark:text-white mt-4 mb-3">
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
    
    // Blockquote
    if (trimmed.startsWith('>')) {
      flushList();
      elements.push(
        <blockquote key={`quote-${index}`} className="border-l-4 border-purple-400 pl-4 py-2 my-3 bg-purple-50 dark:bg-purple-900/20 rounded-r-lg">
          <p className="text-gray-700 dark:text-gray-300 italic">
            {renderInline(trimmed.slice(1).trim())}
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
    
    // Regular paragraph
    flushList();
    elements.push(
      <p key={`p-${index}`} className="text-gray-800 dark:text-gray-200 mb-3 leading-relaxed">
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
 * ENHANCED: Properly handles inline LaTeX expressions
 */
const renderInline = (text) => {
  if (!text) return null;
  
  const parts = [];
  let key = 0;
  
  // Pattern to match all inline elements including LaTeX
  // Order matters: LaTeX first, then markdown
  // FIXED: Use non-greedy matching for LaTeX to handle nested parentheses like \frac{n!}{(n-r)!}
  const patterns = [
    { regex: /\\\((.+?)\\\)/g, type: 'inline-math' },         // \(...\) - non-greedy to handle nested parens
    { regex: /\$([^\$\n]+)\$/g, type: 'inline-math-dollar' }, // $...$
    { regex: /\*\*([^*]+)\*\*/g, type: 'bold' },              // **bold**
    { regex: /\*([^*]+)\*/g, type: 'italic' },                // *italic*
    { regex: /_([^_]+)_/g, type: 'italic' },                  // _italic_
    { regex: /`([^`]+)`/g, type: 'code' },                    // `code`
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
        fullMatch: match[0],
        type
      });
    }
  });
  
  // Sort by position
  matches.sort((a, b) => a.start - b.start);
  
  // Remove overlapping matches (keep first)
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
      case 'inline-math-dollar':
        try {
          parts.push(<InlineMath key={key++} math={m.content.trim()} />);
        } catch (e) {
          parts.push(
            <code key={key++} className="text-red-500 bg-red-50 dark:bg-red-900/20 px-1 rounded text-sm">
              {m.content}
            </code>
          );
        }
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
const AdaptiveMarkdown = ({ content, className = '' }) => {
  if (!content) return null;
  
  return (
    <motion.div
      className={`adaptive-markdown ${className}`}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {parseMarkdown(content)}
    </motion.div>
  );
};

export default AdaptiveMarkdown;

