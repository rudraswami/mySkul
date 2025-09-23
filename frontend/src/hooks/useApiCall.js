import { useState, useCallback } from 'react';

/**
 * Custom hook for robust API calls with retry logic, timeout handling, and proper state management
 * Based on 2024 React best practices for error handling and fetch API usage
 */
export function useApiCall() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const callApi = useCallback(async (url, options = {}, config = {}) => {
    const {
      retries = 3,
      timeout = 30000,
      retryDelay = 1000,
      onRetry = null,
      onSuccess = null,
      onError = null
    } = config;

    setIsLoading(true);
    setError(null);
    
    let attempts = 0;

    while (attempts <= retries) {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => {
        controller.abort();
      }, timeout);

      try {
        const response = await fetch(url, {
          ...options,
          signal: controller.signal
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
          // Handle different error types
          if (response.status >= 500) {
            // Server error - retry if we have attempts left
            attempts++;
            if (attempts > retries) {
              const errorMessage = response.status === 500 
                ? 'Our AI service is temporarily busy. Please try again later.'
                : 'Server is temporarily unavailable. Please try again.';
              throw new Error(errorMessage);
            }
            
            // Call onRetry callback if provided
            if (onRetry) {
              onRetry(attempts, retries + 1);
            }
            
            // Wait before retrying with exponential backoff
            await new Promise(resolve => setTimeout(resolve, retryDelay * attempts));
            continue;
          } else if (response.status === 401) {
            // Authentication error - don't retry
            throw new Error('Please log in again to continue.');
          } else {
            // Other client errors - don't retry
            let errorMessage = 'Request failed. Please try again.';
            try {
              const errorData = await response.json();
              errorMessage = errorData.detail || errorMessage;
            } catch (parseError) {
              // Ignore JSON parsing errors
            }
            throw new Error(errorMessage);
          }
        }

        // Success - parse response
        const data = await response.json();
        setIsLoading(false);
        setError(null);
        
        if (onSuccess) {
          onSuccess(data);
        }
        
        return data;

      } catch (err) {
        clearTimeout(timeoutId);
        
        if (err.name === 'AbortError') {
          // Timeout error
          attempts++;
          if (attempts > retries) {
            const timeoutError = new Error('Request timed out. Please check your internet connection and try again.');
            setError(timeoutError);
            setIsLoading(false);
            if (onError) onError(timeoutError);
            throw timeoutError;
          }
          
          if (onRetry) {
            onRetry(attempts, retries + 1);
          }
          
          // Wait before retrying timeout
          await new Promise(resolve => setTimeout(resolve, retryDelay * attempts));
          continue;
        } else if (err.name === 'TypeError' && err.message.includes('fetch')) {
          // Network error - don't retry
          const networkError = new Error('Network error. Please check your internet connection.');
          setError(networkError);
          setIsLoading(false);
          if (onError) onError(networkError);
          throw networkError;
        } else {
          // Other errors (including our custom error messages)
          attempts++;
          if (attempts > retries) {
            setError(err);
            setIsLoading(false);
            if (onError) onError(err);
            throw err;
          }
          
          if (onRetry) {
            onRetry(attempts, retries + 1);
          }
          
          // Wait before retrying
          await new Promise(resolve => setTimeout(resolve, retryDelay * attempts));
        }
      }
    }
  }, []);

  const reset = useCallback(() => {
    setIsLoading(false);
    setError(null);
  }, []);

  return {
    callApi,
    isLoading,
    error,
    reset
  };
}

export default useApiCall;