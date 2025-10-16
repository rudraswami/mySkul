/**
 * HTML Sanitization Utility
 * Protects against XSS attacks in AI-generated content
 */
import DOMPurify from 'dompurify';

/**
 * Configure DOMPurify with strict settings for AI responses
 */
const sanitizeConfig = {
  // Allow only safe tags
  ALLOWED_TAGS: [
    'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'ul', 'ol', 'li', 'blockquote', 'code', 'pre', 'a', 'span', 'div',
    'table', 'thead', 'tbody', 'tr', 'th', 'td', 'img', 'hr'
  ],
  
  // Allow only safe attributes
  ALLOWED_ATTR: [
    'href', 'target', 'rel', 'class', 'id', 'src', 'alt', 'title',
    'width', 'height', 'style' // Limited style for formatting
  ],
  
  // Allow only safe URI schemes
  ALLOWED_URI_REGEXP: /^(?:(?:(?:f|ht)tps?|mailto|tel|callto|cid|xmpp|data):|[^a-z]|[a-z+.\-]+(?:[^a-z+.\-:]|$))/i,
  
  // Additional security settings
  KEEP_CONTENT: true, // Keep content even if tags are stripped
  RETURN_DOM: false,
  RETURN_DOM_FRAGMENT: false,
  RETURN_DOM_IMPORT: false,
  FORCE_BODY: false,
  SANITIZE_DOM: true,
  
  // Remove all event handlers and scripts
  FORBID_TAGS: ['script', 'style', 'iframe', 'object', 'embed', 'link'],
  FORBID_ATTR: ['onerror', 'onload', 'onclick', 'onmouseover', 'onfocus'],
};

/**
 * Sanitize HTML content from AI responses
 * @param {string} dirty - Potentially unsafe HTML
 * @param {object} options - Additional DOMPurify options
 * @returns {string} - Safe HTML
 */
export function sanitizeAIResponse(dirty, options = {}) {
  if (!dirty || typeof dirty !== 'string') {
    return '';
  }

  // Merge custom options with default config
  const config = { ...sanitizeConfig, ...options };
  
  // Sanitize with DOMPurify
  return DOMPurify.sanitize(dirty, config);
}

/**
 * Sanitize and render AI response safely
 * @param {string} content - AI response content
 * @returns {object} - Props for dangerouslySetInnerHTML
 */
export function createSafeHTML(content) {
  return {
    __html: sanitizeAIResponse(content)
  };
}

/**
 * Strict sanitization for user-generated content
 * Even more restrictive than AI responses
 */
export function sanitizeUserContent(dirty) {
  const strictConfig = {
    ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'u'],
    ALLOWED_ATTR: [],
    KEEP_CONTENT: true,
  };
  
  return DOMPurify.sanitize(dirty, strictConfig);
}

/**
 * Test if content contains potentially malicious code
 * @param {string} content - Content to test
 * @returns {boolean} - True if suspicious content detected
 */
export function containsMaliciousCode(content) {
  if (!content) return false;
  
  const suspiciousPatterns = [
    /<script[\s\S]*?>[\s\S]*?<\/script>/gi,
    /javascript:/gi,
    /on\w+\s*=/gi, // Event handlers like onclick=
    /<iframe/gi,
    /<object/gi,
    /<embed/gi,
    /eval\(/gi,
    /expression\(/gi,
  ];
  
  return suspiciousPatterns.some(pattern => pattern.test(content));
}

/**
 * Sanitize markdown-like content
 * Converts basic markdown to safe HTML
 */
export function sanitizeMarkdown(markdown) {
  if (!markdown) return '';
  
  // Basic markdown to HTML conversion (simplified)
  let html = markdown
    // Bold
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    // Italic
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    // Code blocks
    .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
    // Inline code
    .replace(/`(.*?)`/g, '<code>$1</code>')
    // Links
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>')
    // Line breaks
    .replace(/\n/g, '<br>');
  
  // Sanitize the converted HTML
  return sanitizeAIResponse(html);
}

export default {
  sanitizeAIResponse,
  createSafeHTML,
  sanitizeUserContent,
  containsMaliciousCode,
  sanitizeMarkdown
};
