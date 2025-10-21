import React from 'react';
import { AlertCircle, RefreshCw, AlertTriangle } from 'lucide-react';

/**
 * APIErrorDisplay - User-friendly error messages for API failures
 * Handles different error types with appropriate messaging and actions
 */
const APIErrorDisplay = ({ error, onRetry, className = '' }) => {
  if (!error) return null;

  // Determine error type and message
  const getErrorInfo = () => {
    const status = error.response?.status;
    const detail = error.response?.data?.detail;
    const userMessage = error.userMessage;

    // Use custom user message if available
    if (userMessage) {
      return {
        type: 'warning',
        title: 'Something went wrong',
        message: userMessage,
        canRetry: status === 500 || status === 503
      };
    }

    // Handle specific status codes
    switch (status) {
      case 500:
        return {
          type: 'error',
          title: 'Server Error',
          message: 'Something went wrong on our end. Our team has been notified. Please try again in a moment.',
          canRetry: true
        };
      
      case 503:
        return {
          type: 'error',
          title: 'Service Unavailable',
          message: 'The service is temporarily unavailable. Please try again in a few moments.',
          canRetry: true
        };
      
      case 401:
        return {
          type: 'warning',
          title: 'Session Expired',
          message: 'Your session has expired. Please log in again to continue.',
          canRetry: false,
          action: 'login'
        };
      
      case 402:
        return {
          type: 'info',
          title: 'Upgrade Required',
          message: 'Please upgrade your plan to access this feature.',
          canRetry: false,
          action: 'upgrade'
        };
      
      case 429:
        return {
          type: 'warning',
          title: 'Too Many Requests',
          message: 'Please slow down and try again in a moment.',
          canRetry: true
        };
      
      case 404:
        return {
          type: 'warning',
          title: 'Not Found',
          message: 'The requested resource could not be found.',
          canRetry: false
        };
      
      default:
        return {
          type: 'error',
          title: 'Error',
          message: typeof detail === 'string' ? detail : 'An unexpected error occurred. Please try again.',
          canRetry: true
        };
    }
  };

  const errorInfo = getErrorInfo();

  // Icon based on error type
  const Icon = errorInfo.type === 'error' ? AlertCircle : AlertTriangle;

  // Color classes based on error type
  const colorClasses = {
    error: 'bg-red-50 border-red-200 text-red-800',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    info: 'bg-blue-50 border-blue-200 text-blue-800'
  };

  return (
    <div className={`rounded-lg border-2 p-4 ${colorClasses[errorInfo.type]} ${className}`}>
      <div className="flex items-start gap-3">
        <Icon className="h-5 w-5 flex-shrink-0 mt-0.5" />
        <div className="flex-1">
          <h3 className="font-semibold mb-1">{errorInfo.title}</h3>
          <p className="text-sm opacity-90">{errorInfo.message}</p>
          
          {/* Action buttons */}
          <div className="mt-3 flex gap-2">
            {errorInfo.canRetry && onRetry && (
              <button
                onClick={onRetry}
                className="inline-flex items-center gap-2 px-3 py-1.5 text-sm font-medium rounded-md bg-white/50 hover:bg-white/80 transition-colors"
              >
                <RefreshCw className="h-4 w-4" />
                Try Again
              </button>
            )}
            
            {errorInfo.action === 'login' && (
              <button
                onClick={() => window.location.href = '/login'}
                className="inline-flex items-center gap-2 px-3 py-1.5 text-sm font-medium rounded-md bg-white/50 hover:bg-white/80 transition-colors"
              >
                Log In
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * LoadingStateDisplay - Consistent loading indicator
 */
export const LoadingStateDisplay = ({ message = 'Loading...' }) => (
  <div className="flex items-center justify-center gap-3 py-8">
    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
    <p className="text-gray-600">{message}</p>
  </div>
);

/**
 * EmptyStateDisplay - Empty state with optional action
 */
export const EmptyStateDisplay = ({ 
  title = 'No data available', 
  message = '',
  action = null,
  icon: Icon = null
}) => (
  <div className="flex flex-col items-center justify-center gap-3 py-12 text-center">
    {Icon && <Icon className="h-12 w-12 text-gray-400" />}
    <h3 className="text-lg font-medium text-gray-900">{title}</h3>
    {message && <p className="text-sm text-gray-600 max-w-sm">{message}</p>}
    {action && <div className="mt-4">{action}</div>}
  </div>
);

export default APIErrorDisplay;
