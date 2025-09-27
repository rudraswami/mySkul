import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Progress } from './ui/progress';
import { Badge } from './ui/badge';
import { 
  Brain, 
  Clock, 
  Target, 
  TrendingUp, 
  BookOpen, 
  MessageCircle,
  FileText,
  Calendar
} from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function Dashboard() {
  const { user } = useAuth();
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const response = await axios.get(`${API}/dashboard/analytics`);
        setAnalytics(response.data);
      } catch (error) {
        console.error('Failed to fetch analytics:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, []);

  const formatTime = (minutes) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return hours > 0 ? `${hours}h ${mins}m` : `${mins}m`;
  };

  if (loading) {
    return (
      <div className="p-8 space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-300 rounded w-1/4 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-32 bg-gray-300 rounded-lg"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Enhanced Hero Section */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-700 opacity-90"></div>
        <div className="absolute inset-0 bg-black/10"></div>
        <div className="relative p-8 text-white">
          <div className="max-w-4xl">
            <div className="flex items-center space-x-4 mb-6">
              <div className="bg-white/20 backdrop-blur-lg p-4 rounded-2xl">
                <Brain className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-4xl font-bold mb-2">
                  Welcome back, {user?.email?.split('@')[0] || 'Student'}! 👋
                </h1>
                <p className="text-blue-100 text-xl">
                  Your personal AI mentor is ready to accelerate your learning journey
                </p>
              </div>
            </div>
            
            {/* Achievement Highlights */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
              <div className="bg-white/15 backdrop-blur-lg rounded-xl p-4 border border-white/20">
                <div className="flex items-center space-x-3">
                  <Target className="h-6 w-6 text-yellow-300" />
                  <div>
                    <div className="text-2xl font-bold">Coming Soon</div>
                    <div className="text-blue-100 text-sm">Daily Streak</div>
                  </div>
                </div>
              </div>
              
              <div className="bg-white/15 backdrop-blur-lg rounded-xl p-4 border border-white/20">
                <div className="flex items-center space-x-3">
                  <TrendingUp className="h-6 w-6 text-green-300" />
                  <div>
                    <div className="text-2xl font-bold">Ready</div>
                    <div className="text-blue-100 text-sm">AI Tutor Status</div>
                  </div>
                </div>
              </div>
              
              <div className="bg-white/15 backdrop-blur-lg rounded-xl p-4 border border-white/20">
                <div className="flex items-center space-x-3">
                  <BookOpen className="h-6 w-6 text-blue-300" />
                  <div>
                    <div className="text-2xl font-bold">Start Learning</div>
                    <div className="text-blue-100 text-sm">Begin Your Journey</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Main Content */}
      <div className="p-8 -mt-4 relative z-10 space-y-8">
        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="border-0 shadow-md">
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Clock className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Study Time</p>
                <p className="text-2xl font-bold text-gray-900">
                  {formatTime(analytics?.total_study_time || 0)}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-md">
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <Target className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Current Streak</p>
                <p className="text-2xl font-bold text-gray-900">
                  {analytics?.current_streak || 0} days
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-md">
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 rounded-lg">
                <MessageCircle className="h-6 w-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">AI Sessions</p>
                <p className="text-2xl font-bold text-gray-900">
                  {analytics?.chat_sessions_count || 0}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-md">
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-orange-100 rounded-lg">
                <TrendingUp className="h-6 w-6 text-orange-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Weekly Progress</p>
                <p className="text-2xl font-bold text-gray-900">
                  {analytics?.weekly_goals_progress || 0}%
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Study Progress */}
        <div className="lg:col-span-2">
          <Card className="border-0 shadow-md">
            <CardHeader>
              <CardTitle className="flex items-center">
                <BookOpen className="h-5 w-5 mr-2 text-blue-600" />
                Recent Study Progress
              </CardTitle>
            </CardHeader>
            <CardContent>
              {analytics?.recent_progress?.length > 0 ? (
                <div className="space-y-4">
                  {analytics.recent_progress.map((progress, index) => (
                    <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                      <div>
                        <h4 className="font-medium text-gray-900">
                          {progress.subject} - {progress.chapter}
                        </h4>
                        <p className="text-sm text-gray-600">{progress.concept}</p>
                        <p className="text-xs text-gray-500 mt-1">
                          Last accessed: {new Date(progress.last_accessed).toLocaleDateString()}
                        </p>
                      </div>
                      <div className="text-right">
                        <div className="flex items-center mb-2">
                          <Progress 
                            value={progress.mastery_level} 
                            className="w-20 h-2 mr-2" 
                          />
                          <span className="text-sm font-medium">
                            {Math.round(progress.mastery_level)}%
                          </span>
                        </div>
                        <p className="text-xs text-gray-500">
                          {formatTime(progress.time_spent)}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <BookOpen className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500">No study progress yet</p>
                  <Button className="mt-4 bg-blue-600 hover:bg-blue-700">
                    Start Learning
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions & Today's Plan */}
        <div className="space-y-6">
          {/* Quick Actions */}
          <Card className="border-0 shadow-md">
            <CardHeader>
              <CardTitle className="flex items-center">
                <Brain className="h-5 w-5 mr-2 text-purple-600" />
                Quick Actions
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button 
                className="w-full justify-start bg-blue-600 hover:bg-blue-700" 
                onClick={() => window.location.href = '/tutor'}
              >
                <MessageCircle className="h-4 w-4 mr-2" />
                Start AI Tutoring
              </Button>
              
              <Button 
                variant="outline" 
                className="w-full justify-start" 
                onClick={() => window.location.href = '/tests'}
              >
                <FileText className="h-4 w-4 mr-2" />
                Take Mock Test
              </Button>
              
              <Button 
                variant="outline" 
                className="w-full justify-start"
              >
                <Calendar className="h-4 w-4 mr-2" />
                View Study Plan
              </Button>
            </CardContent>
          </Card>

          {/* Today's Goals */}
          <Card className="border-0 shadow-md">
            <CardHeader>
              <CardTitle className="flex items-center">
                <Target className="h-5 w-5 mr-2 text-green-600" />
                Today's Goals
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Study for 2 hours</span>
                  <Progress value={60} className="w-20 h-2" />
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Complete 20 problems</span>
                  <Progress value={35} className="w-20 h-2" />
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Review weak areas</span>
                  <Progress value={0} className="w-20 h-2" />
                </div>
              </div>
              
              <div className="mt-4 p-3 bg-green-50 rounded-lg">
                <p className="text-sm text-green-800 font-medium">
                  🎯 You're making great progress! Keep it up!
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Motivation Card */}
          <Card className="border-0 shadow-md bg-gradient-to-br from-blue-50 to-indigo-50">
            <CardContent className="p-6 text-center">
              <div className="mb-4">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto">
                  <Brain className="h-8 w-8 text-blue-600" />
                </div>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">
                Daily Tip
              </h3>
              <p className="text-sm text-gray-600">
                "Success is the sum of small efforts repeated day in and day out." 
                Keep practicing consistently!
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
      </div>
    </div>
  );
}