import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { PageLoader } from '../ui/loading';

export default function OAuthCallback() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [error, setError] = useState('');

  useEffect(() => {
    const processCallback = async () => {
      // Get session_token from URL query parameters
      const sessionToken = searchParams.get('session_token');

      console.log('🔍 OAuth Callback - Full URL:', window.location.href);
      console.log('🔍 Session Token:', sessionToken ? '✓ Found' : '✗ Missing');

      if (!sessionToken) {
        console.error('❌ No session_token found in URL');
        setError('Authentication failed: No session token received');
        setTimeout(() => navigate('/login'), 3000);
        return;
      }

      console.log('🔐 Processing OAuth callback with session_token');

      try {
        // Set session cookie client-side
        const domain = window.location.hostname.includes('emergent.host') 
          ? '.emergent.host' 
          : window.location.hostname;
        
        const cookieString = `dhruv_ai_session=${sessionToken}; path=/; domain=${domain}; secure; samesite=none; max-age=604800`;
        document.cookie = cookieString;
        
        console.log('🍪 Session cookie set with domain:', domain);

        // Now fetch user session to verify and get user data
        console.log('📡 Fetching user session...');
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/auth/session`, {
          method: 'GET',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json'
          }
        });

        console.log('📥 Session Response Status:', response.status);

        if (!response.ok) {
          const errorData = await response.json();
          console.error('❌ Session Verification Failed:', errorData);
          throw new Error(errorData.detail || `Failed to verify session: ${response.status}`);
        }

        const result = await response.json();
        console.log('✅ Session verified:', {
          email: result.user?.email,
          profile_completed: result.user?.profile_completed
        });

        // Clean URL query parameters
        window.history.replaceState({}, document.title, window.location.pathname);

        // Cognito OS: AI companion first - redirect to tutor
        console.log('→ Redirecting to tutor...');
        navigate('/tutor', { replace: true });
      } catch (error) {
        console.error('❌ OAuth callback error:', error);
        console.error('Error details:', {
          name: error.name,
          message: error.message,
          stack: error.stack
        });
        setError(`Authentication failed: ${error.message}`);
        setTimeout(() => navigate('/login'), 3000);
      }
    };

    processCallback();
  }, [navigate, searchParams]);

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-purple-50">
        <div className="bg-white p-8 rounded-2xl shadow-xl max-w-md text-center">
          <div className="text-red-500 text-5xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Authentication Failed</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <p className="text-sm text-gray-500">Redirecting to login...</p>
        </div>
      </div>
    );
  }

  return <PageLoader message="Completing sign in with Google..." />;
}
