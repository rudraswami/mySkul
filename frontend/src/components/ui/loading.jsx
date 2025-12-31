/**
 * Loading Components — Unified Dark Theme
 * All loading states use the DRON AI brand colors
 */
import React from 'react';
import { Loader2 } from 'lucide-react';
import BrandLogo, { BrandLoadingScreen, NavigationLoader as BrandNavLoader, PageLoader as BrandPageLoader } from './BrandLogo';

// Re-export brand loaders for consistency
export { BrandLoadingScreen, BrandNavLoader as NavigationLoader, BrandPageLoader as PageLoader };

// =============================================================================
// LOADING SPINNER — Base spinner component
// =============================================================================
export const LoadingSpinner = ({ size = "default", className = "" }) => {
  const sizeClasses = {
    sm: "h-4 w-4",
    default: "h-6 w-6", 
    lg: "h-8 w-8",
    xl: "h-10 w-10"
  };

  return (
    <Loader2 className={`animate-spin ${sizeClasses[size]} ${className}`} />
  );
};

// =============================================================================
// CARD LOADER — Skeleton for cards (Dark Theme)
// =============================================================================
export const CardLoader = () => {
  return (
    <div className="animate-pulse">
      <div className="bg-slate-800 rounded-lg h-32 w-full mb-4"></div>
      <div className="space-y-3">
        <div className="bg-slate-700 rounded h-4 w-3/4"></div>
        <div className="bg-slate-700 rounded h-4 w-1/2"></div>
      </div>
    </div>
  );
};

// =============================================================================
// CONTENT LOADER — Skeleton lines (Dark Theme)
// =============================================================================
export const ContentLoader = ({ lines = 3 }) => {
  return (
    <div className="animate-pulse space-y-3">
      {Array.from({ length: lines }).map((_, index) => (
        <div 
          key={index} 
          className="bg-slate-700 rounded h-4"
          style={{ width: index === lines - 1 ? '60%' : '100%' }}
        ></div>
      ))}
    </div>
  );
};

// =============================================================================
// INLINE LOADER — Small inline loading indicator
// =============================================================================
export const InlineLoader = ({ text = 'Loading...' }) => (
  <div className="flex items-center gap-2 text-slate-400">
    <LoadingSpinner size="sm" className="text-violet-500" />
    <span className="text-sm">{text}</span>
  </div>
);

// =============================================================================
// BUTTON LOADER — For loading state in buttons
// =============================================================================
export const ButtonLoader = () => (
  <LoadingSpinner size="sm" className="text-current" />
);

export default {
  LoadingSpinner,
  CardLoader,
  ContentLoader,
  InlineLoader,
  ButtonLoader,
  BrandLoadingScreen,
  NavigationLoader: BrandNavLoader,
  PageLoader: BrandPageLoader,
};
