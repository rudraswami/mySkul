/**
 * 🎨 DOMAIN PALETTES
 * ==================
 * 
 * Curated color schemes for each subject domain.
 * Beautiful, accessible, and semantically meaningful.
 * 
 * NO LLM-generated colors - these are designer-curated.
 */

// Domain-specific color palettes
export const DOMAIN_PALETTES = {
  physics: {
    name: 'Physics',
    primary: '#3B82F6',      // Electric blue
    secondary: '#1D4ED8',    // Deep blue
    accent: '#F59E0B',       // Energy amber
    highlight: '#10B981',    // Success green
    background: ['#EFF6FF', '#DBEAFE'],  // Soft blue gradient
    surface: '#94A3B8',      // Slate surface
    force: '#EF4444',        // Force red
    motion: '#8B5CF6',       // Velocity purple
    text: '#1E293B',
    textLight: '#64748B'
  },
  
  chemistry: {
    name: 'Chemistry',
    primary: '#8B5CF6',      // Molecular purple
    secondary: '#6D28D9',    // Deep purple
    accent: '#EC4899',       // Bond pink
    highlight: '#14B8A6',    // Reaction teal
    background: ['#FAF5FF', '#EDE9FE'],  // Soft purple gradient
    surface: '#A78BFA',
    element: '#F43F5E',      // Element red
    bond: '#22D3EE',         // Bond cyan
    text: '#1E1B4B',
    textLight: '#6366F1'
  },
  
  biology: {
    name: 'Biology',
    primary: '#10B981',      // Life green
    secondary: '#059669',    // Deep green
    accent: '#F97316',       // Organic orange
    highlight: '#06B6D4',    // Cell cyan
    background: ['#ECFDF5', '#D1FAE5'],  // Soft green gradient
    surface: '#6EE7B7',
    cell: '#34D399',         // Cell membrane
    nucleus: '#8B5CF6',      // Nucleus purple
    text: '#064E3B',
    textLight: '#047857'
  },
  
  math: {
    name: 'Mathematics',
    primary: '#6366F1',      // Elegant indigo
    secondary: '#4F46E5',    // Deep indigo
    accent: '#F59E0B',       // Golden ratio
    highlight: '#EC4899',    // Focus pink
    background: ['#EEF2FF', '#E0E7FF'],  // Soft indigo gradient
    surface: '#A5B4FC',
    positive: '#10B981',     // Positive values
    negative: '#EF4444',     // Negative values
    axis: '#64748B',         // Axis gray
    text: '#1E1B4B',
    textLight: '#4338CA'
  },
  
  geography: {
    name: 'Geography',
    primary: '#0EA5E9',      // Ocean blue
    secondary: '#0284C7',    // Deep ocean
    accent: '#84CC16',       // Land green
    highlight: '#F97316',    // Desert orange
    background: ['#F0F9FF', '#E0F2FE'],  // Sky gradient
    surface: '#22D3EE',
    water: '#06B6D4',
    land: '#65A30D',
    text: '#0C4A6E',
    textLight: '#0369A1'
  },
  
  history: {
    name: 'History',
    primary: '#B45309',      // Parchment amber
    secondary: '#92400E',    // Deep amber
    accent: '#DC2626',       // Important red
    highlight: '#7C3AED',    // Royal purple
    background: ['#FFFBEB', '#FEF3C7'],  // Parchment gradient
    surface: '#D97706',
    timeline: '#78350F',
    event: '#B91C1C',
    text: '#451A03',
    textLight: '#78350F'
  },
  
  general: {
    name: 'General',
    primary: '#6366F1',      // Balanced indigo
    secondary: '#4F46E5',
    accent: '#F59E0B',
    highlight: '#10B981',
    background: ['#F8FAFC', '#F1F5F9'],  // Neutral gradient
    surface: '#94A3B8',
    text: '#1E293B',
    textLight: '#64748B'
  }
};

// Role-based color mapping
export const ROLE_COLORS = {
  subject: 'primary',       // Main entity
  environment: 'surface',   // Background/container
  force: 'force',           // Forces/vectors
  label: 'text',            // Text labels
  indicator: 'accent',      // Indicators/markers
  connector: 'secondary',   // Lines/connections
  highlight: 'highlight'    // Emphasis
};

/**
 * Get palette for a domain
 */
export function getPalette(domain) {
  return DOMAIN_PALETTES[domain] || DOMAIN_PALETTES.general;
}

/**
 * Get color for an entity role within a domain
 */
export function getRoleColor(domain, role) {
  const palette = getPalette(domain);
  const colorKey = ROLE_COLORS[role] || 'primary';
  return palette[colorKey] || palette.primary;
}

/**
 * Get gradient background for a domain
 */
export function getBackgroundGradient(domain) {
  const palette = getPalette(domain);
  return palette.background;
}

/**
 * Generate a color scheme for multiple entities
 */
export function generateEntityColors(domain, count) {
  const palette = getPalette(domain);
  const colors = [
    palette.primary,
    palette.secondary,
    palette.accent,
    palette.highlight,
    palette.surface
  ];
  
  const result = [];
  for (let i = 0; i < count; i++) {
    result.push(colors[i % colors.length]);
  }
  return result;
}

export default DOMAIN_PALETTES;
