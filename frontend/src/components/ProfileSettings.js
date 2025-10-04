import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
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
      const token = localStorage.getItem('dhruv_ai_token');
      const response = await fetch(`${API}/subscription/current`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setSubscriptionData(data);
      }
    } catch (error) {
      console.error('Failed to load subscription data:', error);
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

  const getSubscriptionBadge = () => {
    if (!subscriptionData) return <Badge variant="outline">Loading...</Badge>;
    
    const plan = subscriptionData.plan || 'free';
    const isActive = subscriptionData.status === 'active';
    
    if (plan === 'free') {
      return <Badge variant="outline" className="text-gray-600">Free Plan</Badge>;
    } else if (plan === 'premium' && isActive) {
      return <Badge className="bg-gradient-to-r from-yellow-400 to-yellow-600 text-white">
        <Crown className="h-3 w-3 mr-1" />
        Premium
      </Badge>;
    } else {
      return <Badge variant="destructive">Expired</Badge>;
    }
  };

  const navigateBack = () => {
    window.history.back();
  };

  return (
    <div className="p-8 bg-gray-50 min-h-screen">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center mb-4">
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={navigateBack}
              className="mr-4"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-3 rounded-xl mr-4">
              <User className="h-8 w-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-1">
                Profile Settings
              </h1>
              <p className="text-gray-600">
                Manage your account information and preferences
              </p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Profile Information */}
          <div className="lg:col-span-2">
            <Card className="border-0 shadow-md">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Settings className="h-5 w-5 mr-2 text-blue-600" />
                  Personal Information
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {error && (
                  <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                    <div className="flex items-start">
                      <AlertCircle className="h-5 w-5 text-red-500 mr-2 mt-0.5" />
                      <p className="text-red-800 text-sm">{error}</p>
                    </div>
                  </div>
                )}

                {success && (
                  <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                    <div className="flex items-start">
                      <CheckCircle className="h-5 w-5 text-green-500 mr-2 mt-0.5" />
                      <p className="text-green-800 text-sm">Profile updated successfully!</p>
                    </div>
                  </div>
                )}

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Full Name */}
                  <div>
                    <label className="text-sm font-medium text-gray-700 mb-2 block">
                      Full Name
                    </label>
                    <Input
                      value={profileData.full_name}
                      onChange={(e) => handleInputChange('full_name', e.target.value)}
                      placeholder="Enter your full name"
                    />
                  </div>

                  {/* Email */}
                  <div>
                    <label className="text-sm font-medium text-gray-700 mb-2 block">
                      Email Address
                    </label>
                    <Input
                      type="email"
                      value={profileData.email}
                      onChange={(e) => handleInputChange('email', e.target.value)}
                      placeholder="Enter your email"
                    />
                  </div>

                  {/* Phone */}
                  <div>
                    <label className="text-sm font-medium text-gray-700 mb-2 block">
                      Phone Number
                    </label>
                    <Input
                      type="tel"
                      value={profileData.phone}
                      onChange={(e) => handleInputChange('phone', e.target.value)}
                      placeholder="Enter your phone number"
                    />
                  </div>

                  {/* Exam Type */}
                  <div>
                    <label className="text-sm font-medium text-gray-700 mb-2 block">
                      Target Exam
                    </label>
                    <select
                      value={profileData.exam_type}
                      onChange={(e) => handleInputChange('exam_type', e.target.value)}
                      className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="">Select your target exam</option>
                      <option value="JEE">JEE (Engineering)</option>
                      <option value="NEET">NEET (Medical)</option>
                      <option value="UPSC">UPSC (Civil Services)</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>

                  {/* Target Year */}
                  <div>
                    <label className="text-sm font-medium text-gray-700 mb-2 block">
                      Target Year
                    </label>
                    <Input
                      type="number"
                      value={profileData.target_year}
                      onChange={(e) => handleInputChange('target_year', parseInt(e.target.value))}
                      min={new Date().getFullYear()}
                      max={new Date().getFullYear() + 5}
                    />
                  </div>

                  {/* Current Standard */}
                  <div>
                    <label className="text-sm font-medium text-gray-700 mb-2 block">
                      Current Class/Standard
                    </label>
                    <Input
                      value={profileData.current_standard}
                      onChange={(e) => handleInputChange('current_standard', e.target.value)}
                      placeholder="e.g., Class 12, Graduate"
                    />
                  </div>
                </div>

                {/* Institution */}
                <div>
                  <label className="text-sm font-medium text-gray-700 mb-2 block">
                    Institution/School/College
                  </label>
                  <Input
                    value={profileData.institution}
                    onChange={(e) => handleInputChange('institution', e.target.value)}
                    placeholder="Enter your institution name"
                  />
                </div>

                {/* Save Button */}
                <div className="pt-4">
                  <Button 
                    onClick={handleSave}
                    disabled={saving}
                    className="w-full md:w-auto bg-blue-600 hover:bg-blue-700"
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

          {/* Subscription & Account Info */}
          <div className="space-y-6">
            {/* Subscription Card */}
            <Card className="border-0 shadow-md">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <CreditCard className="h-5 w-5 mr-2 text-purple-600" />
                  Subscription
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center py-4">
                  {getSubscriptionBadge()}
                  
                  {subscriptionData && (
                    <div className="mt-4 space-y-2 text-sm text-gray-600">
                      <p>Status: <span className="font-medium">{subscriptionData.status}</span></p>
                      {subscriptionData.expires_at && (
                        <p>Expires: <span className="font-medium">
                          {new Date(subscriptionData.expires_at).toLocaleDateString()}
                        </span></p>
                      )}
                    </div>
                  )}
                  
                  <Button 
                    variant="outline" 
                    size="sm" 
                    className="mt-4 w-full"
                    onClick={() => window.location.href = '/subscription'}
                  >
                    Manage Subscription
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Account Stats */}
            <Card className="border-0 shadow-md">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <BookOpen className="h-5 w-5 mr-2 text-green-600" />
                  Account Overview
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4 text-sm">
                  <div className="flex justify-between">
                    <span>Member Since:</span>
                    <span className="font-medium">
                      {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>User ID:</span>
                    <span className="font-medium font-mono text-xs">
                      {user?.user_id?.substring(0, 8) || 'N/A'}...
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Account Status:</span>
                    <Badge variant="outline" className="text-green-600">
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