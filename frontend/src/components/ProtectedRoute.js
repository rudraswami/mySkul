import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useSubscription } from '../contexts/SubscriptionContext';
import { PageLoader } from './ui/loading';

/**
 * Unified Route Guard Component
 * Checks both authentication and subscription state before rendering
 * Prevents unauthenticated users from seeing restricted content
 */
export function ProtectedRoute({ children, requireSubscription = false, minTier = 'free' }) {
  const { user, loading: authLoading } = useAuth();
  const { subscriptionInfo, loading: subLoading } = useSubscription();
  const location = useLocation();

  // Show loader while checking authentication and subscription
  if (authLoading || (requireSubscription && subLoading)) {
    return <PageLoader message="Verifying access..." />;
  }

  // Redirect to login if not authenticated
  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Redirect to profile setup if profile not completed
  if (!user.profile_completed) {
    return <Navigate to="/profile-setup" replace />;
  }

  // Check subscription tier if required
  if (requireSubscription && subscriptionInfo) {
    const currentTier = subscriptionInfo.subscription_tier?.toLowerCase() || 'free';
    const requiredTier = minTier.toLowerCase();
    
    const tierHierarchy = {
      'free': 0,
      'starter': 1,
      'scholar': 2,
      'genius': 3,
      'basic': 1,
      'premium': 3
    };

    const currentLevel = tierHierarchy[currentTier] || 0;
    const requiredLevel = tierHierarchy[requiredTier] || 0;

    if (currentLevel < requiredLevel) {
      // Redirect to subscription page if insufficient tier
      return <Navigate to="/subscription" state={{ requiredTier: minTier }} replace />;
    }
  }

  // All checks passed - render children
  return <>{children}</>;
}

/**
 * Public Route Component
 * Redirects authenticated users away from login/register pages
 */
export function PublicRoute({ children }) {
  const { user, loading } = useAuth();
  
  if (loading) {
    return <PageLoader message="Loading..." />;
  }

  // Redirect authenticated users to dashboard
  if (user && user.profile_completed) {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
}

export default ProtectedRoute;
