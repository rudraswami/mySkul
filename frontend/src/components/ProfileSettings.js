import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useSubscription } from '../contexts/SubscriptionContext';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { 
  User,
  Mail,
  Phone,
  Calendar,
  BookOpen,
  CreditCard,
  Settings,
  Save,
  AlertCircle,
  CheckCircle,
  ArrowLeft,
  Crown,
  Clock
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function ProfileSettings() {
  const { user, updateUser } = useAuth();
  const { 
    subscriptionInfo, 
    dailyUsage, 
    upgradeSubscription,
    fetchSubscriptionInfo,
    currentTier,
    planInfo 
  } = useSubscription();
  const [profileData, setProfileData] = useState({
    full_name: '',
    email: '',
    phone: '',
    exam_type: '',
    target_year: '',
    current_standard: '',
    institution: ''
  });
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [subscriptionData, setSubscriptionData] = useState(null);
  const [upgradingTier, setUpgradingTier] = useState(null);

  useEffect(() => {
    if (user) {
      setProfileData({
        full_name: user.full_name || '',
        email: user.email || '',
        phone: user.phone || '',
        exam_type: user.exam_type || '',
        target_year: user.target_year || new Date().getFullYear() + 1,
        current_standard: user.current_standard || '',
        institution: user.institution || ''
      });
      loadSubscriptionData();
    }
  }, [user]);

  const loadSubscriptionData = async () => {
    try {
      await fetchSubscriptionInfo();
      setSubscriptionData(subscriptionInfo);
    } catch (error) {
      console.error('Failed to load subscription data:', error);
    }
  };

  const handleUpgrade = async (targetTier, billingCycle = 'monthly') => {
    setUpgradingTier(targetTier);
    try {
      const result = await upgradeSubscription(targetTier, billingCycle);
      if (result.success) {
        setSuccess(true);
        setTimeout(() => setSuccess(false), 3000);
      } else {
        setError(result.message || 'Upgrade failed');
      }
    } catch (error) {
      setError('Failed to upgrade subscription');
    } finally {
      setUpgradingTier(null);
    }
  };

  const handleInputChange = (field, value) => {
    setProfileData(prev => ({
      ...prev,
      [field]: value
    }));
    setError(null);
    setSuccess(false);
  };

  const handleSave = async () => {
    if (!profileData.full_name || !profileData.email) {
      setError('Name and email are required');
      return;
    }

    setSaving(true);
    setError(null);

    try {
      const token = localStorage.getItem('dhruv_ai_token');
      const response = await fetch(`${API}/user/profile`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(profileData)
      });

      if (response.ok) {
        const updatedUser = await response.json();
        updateUser(updatedUser.user);
        setSuccess(true);
        setTimeout(() => setSuccess(false), 3000);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to update profile');
      }
    } catch (error) {
      setError('Failed to update profile. Please check your connection.');
    } finally {
      setSaving(false);
    }
  };

  const navigateBack = () => {
    window.history.back();
  };

  return (
    <div className="p-8 bg-gradient-to-br from-slate-900 via-slate-900 to-slate-950 min-h-screen">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center mb-4">
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={navigateBack}
              className="mr-4 text-slate-400 hover:text-white hover:bg-slate-800"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
            <div className="bg-gradient-to-r from-violet-600 to-indigo-600 p-3 rounded-xl mr-4">
              <User className="h-8 w-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white mb-1">
                Profile Settings
              </h1>
              <p className="text-slate-400">
                Manage your account information and preferences
              </p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Profile Information */}
          <div className="lg:col-span-2">
            <Card className="border border-slate-700/50 shadow-md bg-slate-800/40 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center text-white">
                  <Settings className="h-5 w-5 mr-2 text-violet-400" />
                  Personal Information
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {error && (
                  <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
                    <div className="flex items-start">
                      <AlertCircle className="h-5 w-5 text-red-400 mr-2 mt-0.5" />
                      <p className="text-red-300 text-sm">{error}</p>
                    </div>
                  </div>
                )}

                {success && (
                  <div className="p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-lg">
                    <div className="flex items-start">
                      <CheckCircle className="h-5 w-5 text-emerald-400 mr-2 mt-0.5" />
                      <p className="text-emerald-300 text-sm">Profile updated successfully!</p>
                    </div>
                  </div>
                )}

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Full Name */}
                  <div>
                    <label className="text-sm font-medium text-slate-300 mb-2 block">
                      Full Name
                    </label>
                    <Input
                      value={profileData.full_name}
                      onChange={(e) => handleInputChange('full_name', e.target.value)}
                      placeholder="Enter your full name"
                      className="bg-slate-900/50 border-slate-600/50 text-white placeholder-slate-500 focus:ring-violet-500 focus:border-violet-500"
                    />
                  </div>

                  {/* Email */}
                  <div>
                    <label className="text-sm font-medium text-slate-300 mb-2 block">
                      Email Address
                    </label>
                    <Input
                      type="email"
                      value={profileData.email}
                      onChange={(e) => handleInputChange('email', e.target.value)}
                      placeholder="Enter your email"
                      className="bg-slate-900/50 border-slate-600/50 text-white placeholder-slate-500 focus:ring-violet-500 focus:border-violet-500"
                    />
                  </div>

                  {/* Phone */}
                  <div>
                    <label className="text-sm font-medium text-slate-300 mb-2 block">
                      Phone Number
                    </label>
                    <Input
                      type="tel"
                      value={profileData.phone}
                      onChange={(e) => handleInputChange('phone', e.target.value)}
                      placeholder="Enter your phone number"
                      className="bg-slate-900/50 border-slate-600/50 text-white placeholder-slate-500 focus:ring-violet-500 focus:border-violet-500"
                    />
                  </div>

                  {/* Exam Type */}
                  <div>
                    <label className="text-sm font-medium text-slate-300 mb-2 block">
                      Target Exam
                    </label>
                    <select
                      value={profileData.exam_type}
                      onChange={(e) => handleInputChange('exam_type', e.target.value)}
                      className="w-full p-2 bg-slate-900/50 border border-slate-600/50 rounded-md text-white focus:ring-2 focus:ring-violet-500 focus:border-violet-500"
                    >
                      <option value="">Select your target exam</option>
                      <option value="JEE">JEE (Engineering)</option>
                      <option value="NEET">NEET (Medical)</option>
                      <option value="UPSC">UPSC (Civil Services)</option>
                      <option value="Others">Others</option>
                    </select>
                  </div>

                  {/* Target Year */}
                  <div>
                    <label className="text-sm font-medium text-slate-300 mb-2 block">
                      Target Year
                    </label>
                    <Input
                      type="number"
                      value={profileData.target_year}
                      onChange={(e) => handleInputChange('target_year', parseInt(e.target.value))}
                      min={new Date().getFullYear()}
                      max={new Date().getFullYear() + 5}
                      className="bg-slate-900/50 border-slate-600/50 text-white placeholder-slate-500 focus:ring-violet-500 focus:border-violet-500"
                    />
                  </div>

                  {/* Current Standard */}
                  <div>
                    <label className="text-sm font-medium text-slate-300 mb-2 block">
                      Current Class/Standard
                    </label>
                    <Input
                      value={profileData.current_standard}
                      onChange={(e) => handleInputChange('current_standard', e.target.value)}
                      placeholder="e.g., Class 12, Graduate"
                      className="bg-slate-900/50 border-slate-600/50 text-white placeholder-slate-500 focus:ring-violet-500 focus:border-violet-500"
                    />
                  </div>
                </div>

                {/* Institution */}
                <div>
                  <label className="text-sm font-medium text-slate-300 mb-2 block">
                    Institution/School/College
                  </label>
                  <Input
                    value={profileData.institution}
                    onChange={(e) => handleInputChange('institution', e.target.value)}
                    placeholder="Enter your institution name"
                    className="bg-slate-900/50 border-slate-600/50 text-white placeholder-slate-500 focus:ring-violet-500 focus:border-violet-500"
                  />
                </div>

                {/* Save Button */}
                <div className="pt-4">
                  <Button 
                    onClick={handleSave}
                    disabled={saving}
                    className="w-full md:w-auto bg-gradient-to-r from-violet-600 to-indigo-600 hover:shadow-violet-500/25"
                  >
                    {saving ? (
                      <>
                        <Clock className="h-4 w-4 mr-2 animate-spin" />
                        Saving...
                      </>
                    ) : (
                      <>
                        <Save className="h-4 w-4 mr-2" />
                        Save Changes
                      </>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Account Info Only - Subscription moved to dedicated /subscription page */}
          <div className="space-y-6">
            {/* Link to Subscription Page */}
            <Card className="border border-violet-500/30 shadow-md bg-gradient-to-r from-violet-600/10 to-indigo-600/10 backdrop-blur-sm">
              <CardContent className="p-6">
                <div className="text-center">
                  <Crown className="h-12 w-12 mx-auto text-violet-400 mb-3" />
                  <h3 className="text-lg font-semibold text-white mb-2">
                    Manage Your Subscription
                  </h3>
                  <p className="text-sm text-slate-400 mb-4">
                    View plans, upgrade, and manage billing
                  </p>
                  <Button
                    onClick={() => window.location.href = '/subscription'}
                    className="bg-gradient-to-r from-violet-600 to-indigo-600 hover:shadow-violet-500/25"
                  >
                    Go to Subscription
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Account Stats */}
            <Card className="border border-slate-700/50 shadow-md bg-slate-800/40 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center text-white">
                  <BookOpen className="h-5 w-5 mr-2 text-emerald-400" />
                  Account Overview
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4 text-sm">
                  <div className="flex justify-between text-slate-400">
                    <span>Member Since:</span>
                    <span className="font-medium text-slate-200">
                      {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
                    </span>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>User ID:</span>
                    <span className="font-medium font-mono text-xs text-slate-200">
                      {user?.user_id?.substring(0, 8) || 'N/A'}...
                    </span>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>Account Status:</span>
                    <Badge variant="outline" className="text-emerald-400 border-emerald-500/30">
                      Active
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}