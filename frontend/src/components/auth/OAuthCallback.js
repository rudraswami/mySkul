import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { PageLoader } from '../ui/loading';

export default function OAuthCallback() {
  const navigate = useNavigate();
  const [error, setError] = useState('');

  useEffect(() => {
    const processCallback = async () => {
      // Get session_id from URL fragment
      const fragment = window.location.hash.substring(1);
      const params = new URLSearchParams(fragment);
      const sessionId = params.get('session_id');

      console.log('🔍 OAuth Callback - Full URL:', window.location.href);
      console.log('🔍 URL Fragment:', fragment);
      console.log('🔍 Session ID:', sessionId);

      if (!sessionId) {
        console.error('❌ No session_id found in URL');
        setError('Authentication failed: No session ID received');
        setTimeout(() => navigate('/login'), 3000);
        return;
      }

      console.log('🔐 Processing OAuth callback with session_id:', sessionId);

      try {
        // Call our backend which will proxy to Emergent (avoids CORS issues)
        console.log('📡 Calling backend proxy...');
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/auth/google/session`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          credentials: 'include',
          body: JSON.stringify({ session_id: sessionId })
        });

        console.log('📥 Backend Response Status:', response.status);

        if (!response.ok) {
          const errorData = await response.json();
          console.error('❌ Backend Error Response:', errorData);
          throw new Error(errorData.detail || `Backend responded with status ${response.status}`);
        }

        const result = await response.json();
        console.log('✅ Authentication successful:', {
          email: result.user?.email,
          profile_completed: result.user?.profile_completed
        });

        // Clean URL fragment
        window.history.replaceState({}, document.title, window.location.pathname);

        // Redirect based on profile completion
        if (!result.user.profile_completed) {
          console.log('→ Redirecting to profile setup...');
          
          // Store user info for profile setup screen
          sessionStorage.setItem('temp_user_info', JSON.stringify({
            name: result.user.full_name,
            email: result.user.email,
            photo_url: result.user.photo_url
          }));
          
          navigate('/profile-setup', { replace: true });
        } else {
          console.log('→ Redirecting to dashboard...');
          navigate('/dashboard', { replace: true });
        }
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
  }, [navigate]);

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
