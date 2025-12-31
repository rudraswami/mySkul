/**
 * 🧠 DRON AI — Unified Brand Logo Component (v2)
 * ===============================================
 * 
 * Modern, clean, iconic logo design.
 * 
 * Design Inspiration:
 * - Notion: Clean, simple, memorable
 * - Linear: Geometric precision
 * - Vercel: Iconic simplicity
 * 
 * Concept: "D" monogram with neural spark
 * - The "D" represents DRON
 * - Neural spark represents AI intelligence
 * - Violet gradient represents premium EdTech
 */

import React from 'react';
import { motion } from 'framer-motion';
import { Loader2 } from 'lucide-react';

// =============================================================================
// BRAND COLORS - Single Source of Truth
// =============================================================================
export const BRAND_COLORS = {
  primary: {
    from: '#7c3aed',    // violet-600
    via: '#8b5cf6',     // violet-500
    to: '#6366f1',      // indigo-500
  },
  glow: 'rgba(139, 92, 246, 0.4)',
};

// =============================================================================
// DRON AI LOGO SVG — Clean "D" Monogram with Neural Spark
// =============================================================================
const LogoSVG = ({ size = 32, className = '' }) => (
  <svg
    viewBox="0 0 32 32"
    width={size}
    height={size}
    className={className}
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <defs>
      <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor={BRAND_COLORS.primary.from} />
        <stop offset="50%" stopColor={BRAND_COLORS.primary.via} />
        <stop offset="100%" stopColor={BRAND_COLORS.primary.to} />
      </linearGradient>
      <filter id="logoGlow" x="-50%" y="-50%" width="200%" height="200%">
        <feGaussianBlur stdDeviation="1.5" result="blur"/>
        <feMerge>
          <feMergeNode in="blur"/>
          <feMergeNode in="SourceGraphic"/>
        </feMerge>
      </filter>
    </defs>

    {/* Background rounded square */}
    <rect 
      x="2" y="2" 
      width="28" height="28" 
      rx="8" 
      fill="url(#logoGradient)"
    />

    {/* Stylized "D" letterform */}
    <path
      d="M10 8h4c4.418 0 8 3.582 8 8s-3.582 8-8 8h-4V8z"
      fill="none"
      stroke="white"
      strokeWidth="2.5"
      strokeLinecap="round"
      strokeLinejoin="round"
    />

    {/* Neural spark / AI element - three small dots representing intelligence */}
    <circle cx="15" cy="13" r="1.2" fill="white" opacity="0.9"/>
    <circle cx="18" cy="16" r="1.2" fill="white" opacity="0.9"/>
    <circle cx="15" cy="19" r="1.2" fill="white" opacity="0.9"/>

    {/* Connecting lines for neural effect */}
    <path
      d="M15 13 L18 16 L15 19"
      stroke="white"
      strokeWidth="0.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      opacity="0.7"
      fill="none"
    />
  </svg>
);

// =============================================================================
// MINIMAL ICON (for favicon/small sizes)
// =============================================================================
const LogoIconMinimal = ({ size = 24 }) => (
  <svg
    viewBox="0 0 24 24"
    width={size}
    height={size}
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <defs>
      <linearGradient id="miniGradient" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor={BRAND_COLORS.primary.from} />
        <stop offset="100%" stopColor={BRAND_COLORS.primary.to} />
      </linearGradient>
    </defs>
    <rect x="1" y="1" width="22" height="22" rx="6" fill="url(#miniGradient)"/>
    <path
      d="M7 6h3c3 0 5.5 2.5 5.5 6s-2.5 6-5.5 6H7V6z"
      fill="none"
      stroke="white"
      strokeWidth="2"
      strokeLinecap="round"
    />
    <circle cx="11" cy="10" r="0.9" fill="white"/>
    <circle cx="13" cy="12" r="0.9" fill="white"/>
    <circle cx="11" cy="14" r="0.9" fill="white"/>
  </svg>
);

// =============================================================================
// MAIN BRAND LOGO COMPONENT
// =============================================================================
const BrandLogo = ({
  size = 'md',
  variant = 'full',        // 'full' | 'icon' | 'text' | 'loading'
  showTagline = false,
  tagline = 'Your AI Study Partner',
  className = '',
  onClick,
}) => {
  // Size configurations
  const sizes = {
    xs: { icon: 20, text: 'text-sm', container: 'gap-1.5' },
    sm: { icon: 28, text: 'text-base', container: 'gap-2' },
    md: { icon: 36, text: 'text-lg', container: 'gap-2.5' },
    lg: { icon: 44, text: 'text-xl', container: 'gap-3' },
    xl: { icon: 56, text: 'text-2xl', container: 'gap-3.5' },
  };

  const config = sizes[size] || sizes.md;

  // Text logo
  const TextLogo = () => (
    <div className="flex flex-col">
      <h1 className={`font-bold tracking-tight text-white ${config.text}`}>
        DRON <span className="text-violet-400">AI</span>
      </h1>
      {showTagline && (
        <span className="text-[11px] text-slate-500 font-medium">
          {tagline}
        </span>
      )}
    </div>
  );

  // Loading variant with spinner
  if (variant === 'loading') {
    return (
      <div className={`flex items-center ${config.container} ${className}`}>
        <LogoSVG size={config.icon} />
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
        >
          <Loader2 className="w-5 h-5 text-violet-400" />
        </motion.div>
      </div>
    );
  }

  // Icon only variant
  if (variant === 'icon') {
    return (
      <div 
        className={className} 
        onClick={onClick} 
        style={{ cursor: onClick ? 'pointer' : 'default' }}
      >
        <LogoSVG size={config.icon} />
      </div>
    );
  }

  // Text only variant
  if (variant === 'text') {
    return (
      <div 
        className={className} 
        onClick={onClick} 
        style={{ cursor: onClick ? 'pointer' : 'default' }}
      >
        <TextLogo />
      </div>
    );
  }

  // Full variant (icon + text)
  return (
    <div 
      className={`flex items-center ${config.container} ${className}`}
      onClick={onClick}
      style={{ cursor: onClick ? 'pointer' : 'default' }}
    >
      <LogoSVG size={config.icon} />
      <TextLogo />
    </div>
  );
};

// =============================================================================
// SATHI PERSONA BADGE — For AI Chat Interface (smaller, with status)
// =============================================================================
export const SathiPersonaBadge = ({ 
  size = 'md',
  status = 'ready',  // 'ready' | 'thinking' | 'listening' | 'explaining'
  className = ''
}) => {
  const sizes = {
    sm: 24,
    md: 32,
    lg: 40,
  };

  const statusConfig = {
    ready: { color: 'bg-emerald-500', pulse: false },
    thinking: { color: 'bg-violet-500', pulse: true },
    listening: { color: 'bg-blue-500', pulse: true },
    explaining: { color: 'bg-amber-500', pulse: false },
  };

  const iconSize = sizes[size] || sizes.md;
  const statusInfo = statusConfig[status] || statusConfig.ready;

  return (
    <div className={`relative ${className}`}>
      <LogoSVG size={iconSize} />
      {/* Status indicator */}
      <span 
        className={`absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full border-2 border-slate-900 ${statusInfo.color} ${statusInfo.pulse ? 'animate-pulse' : ''}`}
      />
    </div>
  );
};

// =============================================================================
// APP LOADING SCREEN — Full Page Loader with Brand (Dark Theme)
// =============================================================================
export const BrandLoadingScreen = ({ message = 'Loading...' }) => (
  <div className="fixed inset-0 bg-slate-950 flex flex-col items-center justify-center z-50">
    {/* Subtle background glow */}
    <div className="absolute inset-0 pointer-events-none overflow-hidden">
      <div className="absolute top-1/3 left-1/2 -translate-x-1/2 w-96 h-96 bg-violet-600/20 blur-[100px] rounded-full" />
    </div>

    <div className="relative flex flex-col items-center">
      <BrandLogo size="xl" variant="loading" />
      
      <motion.div
        className="mt-6 flex flex-col items-center"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
      >
        <h2 className="text-lg font-semibold text-white mb-1">DRON AI</h2>
        <p className="text-sm text-slate-400">{message}</p>
      </motion.div>
    </div>
  </div>
);

// =============================================================================
// NAVIGATION LOADING OVERLAY (Dark Theme)
// =============================================================================
export const NavigationLoader = ({ message = 'Loading...' }) => (
  <div className="fixed inset-0 bg-slate-950/95 backdrop-blur-sm flex items-center justify-center z-50">
    <div className="flex flex-col items-center">
      <BrandLogo size="lg" variant="loading" />
      <p className="text-sm text-slate-400 mt-4">{message}</p>
    </div>
  </div>
);

// =============================================================================
// PAGE LOADER (Dark Theme, non-fixed)
// =============================================================================
export const PageLoader = ({ message = 'Loading...' }) => (
  <div className="min-h-screen bg-slate-950 flex items-center justify-center">
    <div className="flex flex-col items-center">
      <BrandLogo size="lg" variant="loading" />
      <p className="text-sm text-slate-400 mt-4">{message}</p>
    </div>
  </div>
);

export default BrandLogo;
