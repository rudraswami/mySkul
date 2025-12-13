/**
 * 🎨 ASSET LIBRARY
 * =================
 * 
 * SVG assets for Indian cultural metaphors
 * Hand-drawn style assets for Magic Notebook
 */

// ============================================
// SVG ASSETS (Inline for now, can be externalized)
// ============================================

export const SVG_ASSETS = {
  // Cricket
  cricket_ball: `
    <svg width="40" height="40" viewBox="0 0 40 40">
      <circle cx="20" cy="20" r="18" fill="#D32F2F" stroke="#B71C1C" stroke-width="2"/>
      <path d="M 8 20 Q 20 15, 32 20" stroke="#fff" stroke-width="1.5" fill="none"/>
      <path d="M 8 20 Q 20 25, 32 20" stroke="#fff" stroke-width="1.5" fill="none"/>
    </svg>
  `,
  
  cricket_bat: `
    <svg width="60" height="100" viewBox="0 0 60 100">
      <rect x="20" y="10" width="20" height="60" fill="#D2691E" stroke="#8B4513" stroke-width="2" rx="2"/>
      <rect x="25" y="70" width="10" height="25" fill="#654321" stroke="#4B3621" stroke-width="1.5"/>
    </svg>
  `,
  
  wickets: `
    <svg width="60" height="80" viewBox="0 0 60 80">
      <line x1="15" y1="20" x2="15" y2="70" stroke="#8B4513" stroke-width="3"/>
      <line x1="30" y1="20" x2="30" y2="70" stroke="#8B4513" stroke-width="3"/>
      <line x1="45" y1="20" x2="45" y2="70" stroke="#8B4513" stroke-width="3"/>
      <rect x="10" y="15" width="40" height="5" fill="#CD853F" stroke="#8B4513" stroke-width="1"/>
      <rect x="10" y="70" width="40" height="3" fill="#8B4513"/>
    </svg>
  `,
  
  // Transport
  auto_rickshaw: `
    <svg width="80" height="60" viewBox="0 0 80 60">
      <path d="M 10 40 L 20 20 L 60 20 L 70 40 Z" fill="#FFD700" stroke="#B8860B" stroke-width="2"/>
      <rect x="15" y="25" width="35" height="15" fill="#87CEEB" stroke="#4682B4" stroke-width="1.5"/>
      <circle cx="25" cy="50" r="8" fill="#333" stroke="#000" stroke-width="2"/>
      <circle cx="55" cy="50" r="8" fill="#333" stroke="#000" stroke-width="2"/>
      <path d="M 60 25 L 68 25 L 68 35 L 60 35" fill="#FFD700" stroke="#B8860B" stroke-width="1.5"/>
    </svg>
  `,
  
  local_train: `
    <svg width="100" height="70" viewBox="0 0 100 70">
      <rect x="10" y="15" width="80" height="40" fill="#E91E63" stroke="#C2185B" stroke-width="2" rx="3"/>
      <rect x="15" y="20" width="30" height="20" fill="#FFF9C4" stroke="#F57F17" stroke-width="1.5"/>
      <rect x="55" y="20" width="30" height="20" fill="#FFF9C4" stroke="#F57F17" stroke-width="1.5"/>
      <circle cx="30" cy="60" r="5" fill="#424242" stroke="#212121" stroke-width="1.5"/>
      <circle cx="70" cy="60" r="5" fill="#424242" stroke="#212121" stroke-width="1.5"/>
      <text x="50" y="50" text-anchor="middle" fill="#fff" font-size="10" font-weight="bold">LOCAL</text>
    </svg>
  `,
  
  // Food
  chai_cup: `
    <svg width="50" height="60" viewBox="0 0 50 60">
      <ellipse cx="25" cy="30" rx="18" ry="20" fill="#FFF8DC" stroke="#D2691E" stroke-width="2"/>
      <ellipse cx="25" cy="28" rx="16" ry="3" fill="#8B4513"/>
      <path d="M 43 30 Q 50 30, 50 35 Q 50 40, 43 40" stroke="#D2691E" stroke-width="2" fill="none"/>
      <path d="M 20 15 Q 25 10, 30 15" stroke="#999" stroke-width="1.5" fill="none" opacity="0.6"/>
    </svg>
  `,
  
  dosa: `
    <svg width="80" height="40" viewBox="0 0 80 40">
      <ellipse cx="40" cy="25" rx="35" ry="12" fill="#F4A460" stroke="#D2691E" stroke-width="1.5"/>
      <ellipse cx="40" cy="20" rx="35" ry="12" fill="#FFE4B5" stroke="#DEB887" stroke-width="1.5"/>
      <path d="M 10 20 Q 15 18, 20 20" stroke="#CD853F" stroke-width="1" fill="none"/>
      <path d="M 60 20 Q 65 22, 70 20" stroke="#CD853F" stroke-width="1" fill="none"/>
    </svg>
  `,
  
  // Festivals
  diya: `
    <svg width="50" height="60" viewBox="0 0 50 60">
      <ellipse cx="25" cy="40" rx="20" ry="8" fill="#CD853F" stroke="#8B4513" stroke-width="1.5"/>
      <path d="M 10 40 L 15 30 L 35 30 L 40 40" fill="#D2691E" stroke="#8B4513" stroke-width="1.5"/>
      <ellipse cx="25" cy="30" rx="10" ry="3" fill="#FFD700"/>
      <path d="M 25 25 Q 23 15, 25 10" stroke="#FFA500" stroke-width="2" fill="none"/>
      <path d="M 25 25 Q 27 18, 30 15" stroke="#FF6347" stroke-width="1.5" fill="none"/>
      <circle cx="25" cy="15" r="4" fill="#FFD700" opacity="0.7"/>
    </svg>
  `,
  
  // Nature
  rain_drop: `
    <svg width="20" height="30" viewBox="0 0 20 30">
      <path d="M 10 5 Q 5 10, 5 18 Q 5 25, 10 28 Q 15 25, 15 18 Q 15 10, 10 5 Z" 
            fill="#4FC3F7" stroke="#0288D1" stroke-width="1.5"/>
      <ellipse cx="8" cy="15" rx="2" ry="4" fill="#E1F5FE" opacity="0.6"/>
    </svg>
  `,
  
  monsoon_cloud: `
    <svg width="80" height="50" viewBox="0 0 80 50">
      <ellipse cx="25" cy="25" rx="20" ry="15" fill="#90A4AE" stroke="#546E7A" stroke-width="1.5"/>
      <ellipse cx="50" cy="28" rx="25" ry="18" fill="#78909C" stroke="#455A64" stroke-width="1.5"/>
      <ellipse cx="40" cy="20" rx="18" ry="12" fill="#B0BEC5" stroke="#78909C" stroke-width="1.5"/>
    </svg>
  `,
  
  // Generic elements
  stick_figure: `
    <svg width="40" height="80" viewBox="0 0 40 80">
      <circle cx="20" cy="12" r="8" fill="#FFE0B2" stroke="#F57C00" stroke-width="2"/>
      <line x1="20" y1="20" x2="20" y2="50" stroke="#424242" stroke-width="3"/>
      <line x1="20" y1="30" x2="8" y2="45" stroke="#424242" stroke-width="2.5"/>
      <line x1="20" y1="30" x2="32" y2="45" stroke="#424242" stroke-width="2.5"/>
      <line x1="20" y1="50" x2="10" y2="75" stroke="#424242" stroke-width="2.5"/>
      <line x1="20" y1="50" x2="30" y2="75" stroke="#424242" stroke-width="2.5"/>
    </svg>
  `,
};

// ============================================
// ASSET HELPERS
// ============================================

/**
 * Get SVG asset by ID
 */
export function getAsset(assetId) {
  return SVG_ASSETS[assetId] || null;
}

/**
 * Get asset data URL
 */
export function getAssetDataUrl(assetId) {
  const svg = getAsset(assetId);
  if (!svg) return null;
  
  const encoded = btoa(svg.trim());
  return `data:image/svg+xml;base64,${encoded}`;
}

/**
 * Render asset as React component
 */
export function renderAsset(assetId, props = {}) {
  const svg = getAsset(assetId);
  if (!svg) return null;
  
  return (
    <div
      dangerouslySetInnerHTML={{ __html: svg }}
      style={{
        display: 'inline-block',
        width: props.width || 'auto',
        height: props.height || 'auto',
        ...props.style,
      }}
    />
  );
}

/**
 * Get all available asset IDs
 */
export function getAllAssetIds() {
  return Object.keys(SVG_ASSETS);
}

/**
 * Check if asset exists
 */
export function hasAsset(assetId) {
  return assetId in SVG_ASSETS;
}

export default SVG_ASSETS;

