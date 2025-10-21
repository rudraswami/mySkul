import React from 'react';
import { AlertTriangle, RefreshCw, Home } from 'lucide-react';
import { Button } from './ui/button';

/**
 * Error Boundary Component
 * Catches React component errors and displays fallback UI
 * Prevents white screen of death
 */
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorCount: 0
    };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Log error details
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    
    // Update state with error details
    this.setState(prevState => ({
      error,
      errorInfo,
      errorCount: prevState.errorCount + 1
    }));

    // TODO: Send to error reporting service (Sentry, LogRocket, etc.)
    // if (window.Sentry) {
    //   window.Sentry.captureException(error, { extra: errorInfo });
    // }
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null
    });
  };

  handleReload = () => {
    window.location.reload();
  };

  handleGoHome = () => {
    window.location.href = '/dashboard';
  };

  render() {
    if (this.state.hasError) {
      // Fallback UI
      return (
        <div className="min-h-screen bg-gradient-to-br from-red-50 via-orange-50 to-yellow-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex items-center justify-center p-4">
          <div className="max-w-2xl w-full bg-white dark:bg-gray-800 rounded-2xl shadow-2xl p-8 border-2 border-red-200 dark:border-red-800">
            {/* Error Icon */}
            <div className="flex justify-center mb-6">
              <div className="bg-red-100 dark:bg-red-900/30 rounded-full p-4">
                <AlertTriangle className="h-16 w-16 text-red-600 dark:text-red-400" />
              </div>
            </div>

            {/* Error Message */}
            <h1 className="text-3xl font-bold text-center text-gray-900 dark:text-white mb-4">
              Oops! Something went wrong
            </h1>
            
            <p className="text-center text-gray-600 dark:text-gray-300 mb-6">
              We encountered an unexpected error. Don't worry, your data is safe. 
              Try refreshing the page or going back to the dashboard.
            </p>

            {/* Error Details (Development Mode) */}
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <div className="mb-6 p-4 bg-gray-100 dark:bg-gray-700 rounded-lg overflow-auto max-h-64">
                <p className="text-sm font-mono text-red-600 dark:text-red-400 mb-2">
                  <strong>Error:</strong> {this.state.error.toString()}
                </p>
                {this.state.errorInfo && (
                  <pre className="text-xs font-mono text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                    {this.state.errorInfo.componentStack}
                  </pre>
                )}
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <Button
                onClick={this.handleReset}
                variant="outline"
                className="flex items-center gap-2"
              >
                <RefreshCw className="h-4 w-4" />
                Try Again
              </Button>
              
              <Button
                onClick={this.handleReload}
                variant="outline"
                className="flex items-center gap-2"
              >
                <RefreshCw className="h-4 w-4" />
                Reload Page
              </Button>
              
              <Button
                onClick={this.handleGoHome}
                className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white"
              >
                <Home className="h-4 w-4" />
                Go to Dashboard
              </Button>
            </div>

            {/* Help Text */}
            <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <p className="text-sm text-center text-blue-800 dark:text-blue-300">
                <strong>Still having issues?</strong> Try logging out and back in, 
                or contact support if the problem persists.
              </p>
            </div>

            {/* Error Count Warning */}
            {this.state.errorCount > 2 && (
              <div className="mt-4 p-3 bg-yellow-100 dark:bg-yellow-900/20 rounded-lg border-l-4 border-yellow-500">
                <p className="text-sm text-yellow-800 dark:text-yellow-300">
                  ⚠️ Multiple errors detected ({this.state.errorCount}). 
                  Consider reloading the page or clearing your browser cache.
                </p>
              </div>
            )}
          </div>
        </div>
      );
    }

    // Normal render
    return this.props.children;
  }
}

export default ErrorBoundary;
