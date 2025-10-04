import React from 'react';
import { Loader2, Brain } from 'lucide-react';

export const LoadingSpinner = ({ size = "default", className = "" }) => {
  const sizeClasses = {
    sm: "h-4 w-4",
    default: "h-6 w-6", 
    lg: "h-8 w-8"
  };

  return (
    <Loader2 className={`animate-spin ${sizeClasses[size]} ${className}`} />
  );
};

export const PageLoader = ({ message = "Loading..." }) => {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <div className="flex items-center justify-center mb-4">
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-3 rounded-xl mr-4">
            <Brain className="h-8 w-8 text-white" />
          </div>
          <LoadingSpinner size="lg" className="text-blue-600" />
        </div>
        <h2 className="text-lg font-semibold text-gray-900 mb-2">Dhruv AI</h2>
        <p className="text-gray-600">{message}</p>
      </div>
    </div>
  );
};

export const NavigationLoader = ({ message = "Loading..." }) => {
  return (
    <div className="fixed inset-0 bg-white bg-opacity-90 flex items-center justify-center z-50">
      <div className="text-center">
        <div className="flex items-center justify-center mb-4">
          <LoadingSpinner size="lg" className="text-blue-600" />
        </div>
        <p className="text-gray-600">{message}</p>
      </div>
    </div>
  );
};

export const CardLoader = () => {
  return (
    <div className="animate-pulse">
      <div className="bg-gray-200 rounded-lg h-32 w-full mb-4"></div>
      <div className="space-y-3">
        <div className="bg-gray-200 rounded h-4 w-3/4"></div>
        <div className="bg-gray-200 rounded h-4 w-1/2"></div>
      </div>
    </div>
  );
};

export const ContentLoader = ({ lines = 3 }) => {
  return (
    <div className="animate-pulse space-y-3">
      {Array.from({ length: lines }).map((_, index) => (
        <div key={index} className="bg-gray-200 rounded h-4 w-full"></div>
      ))}
    </div>
  );
};