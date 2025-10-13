import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { PageLoader } from '../ui/loading';

export default function OAuthCallback() {
  const navigate = useNavigate();
  const { loginWithGoogle } = useAuth();
  const [error, setError] = useState('');

  useEffect(() => {
    const processCallback = async () => {
      // Get session_id from URL fragment
      const fragment = window.location.hash.substring(1);
      const params = new URLSearchParams(fragment);
      const sessionId = params.get('session_id');

      if (!sessionId) {
        console.error('❌ No session_id found in URL');
        setError('Authentication failed: No session ID received');
        setTimeout(() => navigate('/login'), 3000);
        return;
      }

      console.log('🔐 Processing OAuth callback with session_id...');

      try {
        // Exchange session_id for user data with Emergent
        const response = await fetch('https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data', {
          headers: {
            'X-Session-ID': sessionId
          }
        });

        if (!response.ok) {
          throw new Error(`Emergent API responded with status ${response.status}`);
        }

        const sessionData = await response.json();
        console.log('✅ Session data received from Emergent');

        // Send to our backend
        const result = await loginWithGoogle(sessionData);

        if (result.success) {
          console.log('✅ Login successful');
          
          // Clean URL fragment
          window.history.replaceState({}, document.title, window.location.pathname);

          // Redirect based on profile completion
          if (result.needsProfileSetup) {
            console.log('→ Redirecting to profile setup...');
            navigate('/profile-setup', { replace: true });
          } else {
            console.log('→ Redirecting to dashboard...');
            navigate('/dashboard', { replace: true });
          }
        } else {
          throw new Error(result.error || 'Backend login failed');
        }
      } catch (error) {
        console.error('❌ OAuth callback error:', error);
        setError(`Authentication failed: ${error.message}`);
        setTimeout(() => navigate('/login'), 3000);
      }
    };

    processCallback();
  }, [loginWithGoogle, navigate]);

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
