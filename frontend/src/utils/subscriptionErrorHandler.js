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
    const errorMessage = (data.message || data.detail || '').toLowerCase();
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
    
    // Force trigger subscription check to show modal
    try {
      const accessInfo = await checkFeatureAccess(featureName);
      if (!accessInfo.has_access) {
        // Modal should appear automatically from SubscriptionContext
        return { handled: true, shouldRetry: false };
      }
    } catch (checkError) {
      console.error('Failed to check feature access:', checkError);
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