/**
 * Intelligent subscription error handler for market-standard UX
 * Detects subscription limits vs server errors and triggers appropriate UI
 */

// Helper to detect if error is subscription-related
export const isSubscriptionLimitError = (error) => {
  if (!error.response) return false;
  
  const { status, data } = error.response;
  
  // Direct subscription status codes
  if (status === 402 || status === 429) return true;
  
  // Check for subscription limit keywords in error message
  if (data?.message || data?.detail) {
    // Ensure we have a string before calling toLowerCase - defensive coercion
    let errorText = '';
    try {
      if (typeof data.message === 'string') {
        errorText = data.message;
      } else if (typeof data.detail === 'string') {
        errorText = data.detail;
      } else if (Array.isArray(data.detail)) {
        // Handle Pydantic validation errors which come as arrays
        errorText = data.detail.map(err => err.msg || err.message || '').join(' ');
      } else if (data.message !== null && data.message !== undefined) {
        // Fallback: convert any non-null/undefined to string
        errorText = String(data.message);
      } else if (data.detail !== null && data.detail !== undefined) {
        // Fallback: convert any non-null/undefined to string
        errorText = String(data.detail);
      }
    } catch (conversionError) {
      console.error('Error converting message to string:', conversionError);
      errorText = '';
    }
    
    const errorMessage = String(errorText || '').toLowerCase();
    const limitKeywords = [
      'limit reached',
      'quota exceeded',
      'subscription required',
      'upgrade required',
      'daily limit',
      'weekly limit',
      'monthly limit',
      'usage limit',
      'feature limit',
      'access denied',
      'subscription expired',
      'plan limit'
    ];
    
    return limitKeywords.some(keyword => errorMessage.includes(keyword));
  }
  
  // Check error code field
  if (data?.code) {
    const limitCodes = ['LIMIT_REACHED', 'QUOTA_EXCEEDED', 'SUBSCRIPTION_REQUIRED'];
    return limitCodes.includes(data.code);
  }
  
  return false;
};

// Main subscription error handler
export const handleSubscriptionError = async (error, featureName, checkFeatureAccess, setMessages) => {
  console.log('Handling subscription error:', error);
  
  if (isSubscriptionLimitError(error)) {
    console.log('Subscription limit detected - triggering modal');
    
    // If this is a direct 402 error with upsell_info, trigger modal directly
    if (error.response?.status === 402 && error.response?.data?.detail?.upsell_info) {
      console.log('Direct 402 error with upsell_info - triggering modal immediately');
      
      // Force trigger subscription check to show modal with the error data
      try {
        const accessInfo = await checkFeatureAccess(featureName);
        return { handled: true, shouldRetry: false };
      } catch (checkError) {
        // If checkFeatureAccess also fails, we know the modal should appear
        console.log('checkFeatureAccess failed as expected - modal should appear');
        return { handled: true, shouldRetry: false };
      }
    } else {
      // Fallback to normal access check
      try {
        const accessInfo = await checkFeatureAccess(featureName);
        if (!accessInfo.has_access) {
          return { handled: true, shouldRetry: false };
        }
      } catch (checkError) {
        console.log('Feature access check failed - treating as subscription limit');
        return { handled: true, shouldRetry: false };
      }
    }
    
    return { handled: true, shouldRetry: false };
  }
  
  // Handle server errors with user-friendly message
  if (error.response?.status >= 500) {
    const errorMessage = {
      type: 'system_error',
      message: "I'm temporarily having trouble processing your message. Please try again in a moment, or contact support if the issue persists.",
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, errorMessage]);
    return { handled: true, shouldRetry: false };
  }
  
  // Unhandled error - let calling component decide
  return { handled: false, shouldRetry: true };
};

// Success handler for after subscription upgrade
export const handlePostUpgradeRetry = async (originalAction, showToast) => {
  try {
    showToast('🎉 Upgrade successful! Retrying your action...', 'success');
    
    // Add small delay for better UX
    setTimeout(async () => {
      await originalAction();
      showToast('✅ Action completed successfully!', 'success');
    }, 1000);
    
  } catch (error) {
    console.error('Post-upgrade retry failed:', error);
    showToast('❌ Please try your action again', 'error');
  }
};

// Animate subscription unlock (scale/fade effect)
export const animateSubscriptionUnlock = (element) => {
  if (!element) return;
  
  element.style.transform = 'scale(0.95)';
  element.style.opacity = '0.7';
  element.style.transition = 'all 0.3s ease-in-out';
  
  setTimeout(() => {
    element.style.transform = 'scale(1.05)';
    element.style.opacity = '1';
    
    setTimeout(() => {
      element.style.transform = 'scale(1)';
    }, 200);
  }, 100);
};