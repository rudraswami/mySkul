import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { User, Target, BookOpen, Globe, Calendar, Check } from 'lucide-react';
import '../../styles/auth.css';

export default function ProfileSetup() {
  const navigate = useNavigate();
  const { updateUser } = useAuth();
  const [loading, setLoading] = useState(false);
  const [userInfo, setUserInfo] = useState(null);
  const [formData, setFormData] = useState({
    exam_type: '',
    study_goal: '',
    preferred_mode: 'AI Mentor',
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    country: '',
    target_year: new Date().getFullYear() + 1
  });

  useEffect(() => {
    // Note: Session token from URL is now handled by AuthContext
    
    // Get user info from session storage (set during OAuth callback)
    const storedUser = sessionStorage.getItem('temp_user_info');
    if (storedUser) {
      setUserInfo(JSON.parse(storedUser));
    }
    
    // Auto-detect country from timezone
    const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
    if (timezone.includes('Kolkata') || timezone.includes('India')) {
      setFormData(prev => ({ ...prev, country: 'India' }));
    }
  }, []);

  const examTypes = [
    { value: 'JEE', label: 'JEE (Joint Entrance Examination)', icon: '🎓' },
    { value: 'NEET', label: 'NEET (Medical Entrance)', icon: '⚕️' },
    { value: 'UPSC', label: 'UPSC (Civil Services)', icon: '🏛️' },
    { value: 'Others', label: 'Others', icon: '📚' }
  ];

  const preferredModes = [
    { value: 'AI Mentor', icon: '🤖', description: 'Interactive learning with AI' },
    { value: 'Mock Tests', icon: '📝', description: 'Practice with exam simulations' },
    { value: 'Notes', icon: '📖', description: 'Auto-generated smart notes' }
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.exam_type) {
      alert('Please select your exam type');
      return;
    }

    setLoading(true);

    try {
      console.log('📤 Submitting profile data:', formData);
      
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/auth/profile/complete`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify(formData)
      });

      console.log('📥 Response status:', response.status);
      console.log('📥 Response ok:', response.ok);

      if (response.ok) {
        const data = await response.json();
        console.log('✅ Profile completed successfully:', data);
        
        // Update user context with new profile data
        if (data.user) {
          updateUser(data.user);
          console.log('✅ User context updated with profile_completed:', data.user.profile_completed);
        }
        
        // Clear temp storage
        sessionStorage.removeItem('temp_user_info');
        
        console.log('🔄 Navigating to dashboard...');
        // Navigate to dashboard
        navigate('/dashboard', { replace: true });
      } else {
        const error = await response.json();
        console.error('❌ Profile completion failed:', error);
        alert(error.detail || 'Failed to complete profile setup');
      }
    } catch (error) {
      console.error('❌ Profile setup error:', error);
      alert('An error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSkip = () => {
    // Set default values and submit
    setFormData(prev => ({
      ...prev,
      exam_type: 'Others',
      study_goal: 'General Learning'
    }));
    setTimeout(() => {
      document.getElementById('profile-form').requestSubmit();
    }, 100);
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 gradient-animated">
      <div className="w-full max-w-3xl">
        {/* Profile Card */}
        <div className="glass-card-dark rounded-3xl p-8 md:p-12 shadow-2xl fade-in">
          {/* Header with Avatar */}
          <div className="text-center mb-8">
            {userInfo?.photo_url && (
              <img 
                src={userInfo.photo_url} 
                alt="Profile"
                className="w-24 h-24 rounded-full mx-auto mb-4 border-4 border-white/30 shadow-lg"
              />
            )}
            <h1 className="text-3xl md:text-4xl font-bold text-white mb-2">
              Welcome, {userInfo?.name?.split(' ')[0] || 'Student'}! 👋
            </h1>
            <p className="text-white/80 text-lg">
              Let's personalize your learning experience
            </p>
          </div>

          {/* Form */}
          <form id="profile-form" onSubmit={handleSubmit} className="space-y-6">
            {/* Exam Type Selection */}
            <div className="fade-in-delay-1">
              <label className="flex items-center space-x-2 text-white font-semibold mb-3">
                <Target className="h-5 w-5" />
                <span>What are you preparing for? *</span>
              </label>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {examTypes.map((exam) => (
                  <button
                    key={exam.value}
                    type="button"
                    onClick={() => setFormData(prev => ({ ...prev, exam_type: exam.value }))}
                    className={`p-4 rounded-xl border-2 transition-all text-left ${
                      formData.exam_type === exam.value
                        ? 'border-yellow-400 bg-yellow-400/20 shadow-lg'
                        : 'border-white/30 bg-white/5 hover:bg-white/10'
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <span className="text-3xl">{exam.icon}</span>
                      <div className="flex-1">
                        <div className="text-white font-semibold">{exam.value}</div>
                        <div className="text-white/70 text-sm">{exam.label}</div>
                      </div>
                      {formData.exam_type === exam.value && (
                        <Check className="h-6 w-6 text-yellow-400" />
                      )}
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Study Goal */}
            <div className="fade-in-delay-2">
              <label className="flex items-center space-x-2 text-white font-semibold mb-3">
                <BookOpen className="h-5 w-5" />
                <span>Your Study Goal (Optional)</span>
              </label>
              <input
                type="text"
                value={formData.study_goal}
                onChange={(e) => setFormData(prev => ({ ...prev, study_goal: e.target.value }))}
                placeholder="e.g., Crack JEE Advanced 2025, Score 700+ in NEET"
                className="w-full px-4 py-3 rounded-xl bg-white/10 border border-white/30 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
              />
            </div>

            {/* Preferred Mode */}
            <div className="fade-in-delay-2">
              <label className="flex items-center space-x-2 text-white font-semibold mb-3">
                <User className="h-5 w-5" />
                <span>Preferred Learning Mode</span>
              </label>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {preferredModes.map((mode) => (
                  <button
                    key={mode.value}
                    type="button"
                    onClick={() => setFormData(prev => ({ ...prev, preferred_mode: mode.value }))}
                    className={`p-4 rounded-xl border-2 transition-all ${
                      formData.preferred_mode === mode.value
                        ? 'border-yellow-400 bg-yellow-400/20'
                        : 'border-white/30 bg-white/5 hover:bg-white/10'
                    }`}
                  >
                    <div className="text-center">
                      <div className="text-3xl mb-2">{mode.icon}</div>
                      <div className="text-white font-semibold text-sm">{mode.value}</div>
                      <div className="text-white/70 text-xs mt-1">{mode.description}</div>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Target Year */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 fade-in-delay-3">
              <div>
                <label className="flex items-center space-x-2 text-white font-semibold mb-3">
                  <Calendar className="h-5 w-5" />
                  <span>Target Year</span>
                </label>
                <select
                  value={formData.target_year}
                  onChange={(e) => setFormData(prev => ({ ...prev, target_year: parseInt(e.target.value) }))}
                  className="w-full px-4 py-3 rounded-xl bg-white/10 border border-white/30 text-white focus:outline-none focus:ring-2 focus:ring-yellow-400"
                >
                  {[0, 1, 2, 3].map(offset => {
                    const year = new Date().getFullYear() + offset;
                    return <option key={year} value={year}>{year}</option>;
                  })}
                </select>
              </div>

              <div>
                <label className="flex items-center space-x-2 text-white font-semibold mb-3">
                  <Globe className="h-5 w-5" />
                  <span>Country</span>
                </label>
                <input
                  type="text"
                  value={formData.country}
                  onChange={(e) => setFormData(prev => ({ ...prev, country: e.target.value }))}
                  placeholder="Auto-detected"
                  className="w-full px-4 py-3 rounded-xl bg-white/10 border border-white/30 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-yellow-400"
                />
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col md:flex-row gap-4 pt-6 fade-in-delay-3">
              <button
                type="submit"
                disabled={loading || !formData.exam_type}
                className="flex-1 py-4 px-6 rounded-xl bg-gradient-to-r from-yellow-400 to-orange-500 text-gray-900 font-bold text-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
              >
                {loading ? (
                  <>
                    <div className="spinner border-gray-900"></div>
                    <span>Saving...</span>
                  </>
                ) : (
                  <>
                    <Check className="h-5 w-5" />
                    <span>Continue to Dashboard</span>
                  </>
                )}
              </button>

              <button
                type="button"
                onClick={handleSkip}
                disabled={loading}
                className="md:w-auto px-6 py-4 rounded-xl bg-white/10 text-white font-semibold hover:bg-white/20 transition-all disabled:opacity-50"
              >
                Skip for now
              </button>
            </div>
          </form>

          {/* Info Note */}
          <p className="text-center text-white/60 text-sm mt-6 fade-in-delay-3">
            💡 You can update these preferences anytime from your profile settings
          </p>
        </div>
      </div>
    </div>
  );
}
