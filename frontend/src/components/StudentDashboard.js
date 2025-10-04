import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { 
  Brain, 
  BookOpen, 
  Target, 
  Trophy, 
  Clock, 
  TrendingUp,
  Calendar,
  Users,
  Star,
  ChevronRight,
  Play,
  BookMarked,
  FileText,
  MessageCircle,
  BarChart3,
  Zap,
  CheckCircle,
  AlertCircle,
  Plus,
  ArrowUp,
  ArrowDown,
  Timer,
  Heart,
  Flame
} from 'lucide-react';

// Import backend URL
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export default function StudentDashboard() {
  const { user } = useAuth();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [todayGoals, setTodayGoals] = useState([
    { id: 1, text: 'Study for 120 minutes total', progress: 75, target: 120 },
    { id: 2, text: 'Ask AI Tutor for help with doubts', progress: 30, target: 100 }
  ]);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const token = localStorage.getItem('dhruv_ai_token');
      const response = await fetch(`${BACKEND_URL}/api/dashboard/analytics`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setDashboardData(data);
      }
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      // Set some demo data if API fails
      setDashboardData({
        study_time_today: "0h 30m",
        total_sessions: 6,
        current_streak: 7,
        weekly_progress: 75,
        recent_subjects: [
          { name: "Mathematics", progress: 75, topic: "Quadratic Equations" },
          { name: "Physics", progress: 60, topic: "Newton's Laws" },
          { name: "Chemistry", progress: 45, topic: "Chemical Bonding" }
        ]
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="p-8 bg-gray-50 min-h-screen">
        <div className="max-w-7xl mx-auto">
          <div className="animate-pulse space-y-8">
            <div className="bg-gray-200 rounded-lg h-48 w-full"></div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {[1, 2, 3, 4].map(i => (
                <div key={i} className="bg-gray-200 rounded-lg h-32"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 bg-gray-50 min-h-screen">
      <div className="max-w-7xl mx-auto">
        
        {/* Welcome Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 text-white mb-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="bg-white bg-opacity-20 p-3 rounded-xl mr-4">
                <Brain className="h-8 w-8" />
              </div>
              <div>
                <h1 className="text-3xl font-bold mb-2">
                  Welcome back, {user?.full_name?.split(' ')[0] || 'Student'}! 👋
                </h1>
                <p className="text-blue-100 text-lg">
                  ⭐ You studied more than 70% of learners this week!
                </p>
              </div>
            </div>
            <div className="flex space-x-2">
              <Badge className="bg-green-500 text-white border-0">Trust</Badge>
              <Badge className="bg-purple-500 text-white border-0">Personalized</Badge>
              <Badge className="bg-yellow-500 text-white border-0">Empowerment</Badge>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Main Content Area */}
          <div className="lg:col-span-2 space-y-8">
            
            {/* Today's Focus */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle className="flex items-center">
                  <Target className="h-5 w-5 mr-2 text-blue-600" />
                  Today's Focus
                </CardTitle>
                <span className="text-sm text-gray-500">0%</span>
              </CardHeader>
              <CardContent className="space-y-4">
                {todayGoals.map((goal) => (
                  <div key={goal.id} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <CheckCircle className="h-4 w-4 mr-2 text-gray-400" />
                        <span className="text-sm">{goal.text}</span>
                      </div>
                      <div className="flex items-center text-xs text-gray-500">
                        <Clock className="h-3 w-3 mr-1" />
                        <span>120 mins</span>
                        <span className="ml-2 font-medium">General</span>
                        <span className="ml-2">0%</span>
                      </div>
                    </div>
                    <Progress value={0} className="h-2" />
                  </div>
                ))}
                
                {/* Second goal */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <CheckCircle className="h-4 w-4 mr-2 text-gray-400" />
                      <span className="text-sm">Ask AI Tutor for help with doubts</span>
                    </div>
                    <div className="flex items-center text-xs text-gray-500">
                      <Clock className="h-3 w-3 mr-1" />
                      <span>10 mins</span>
                      <span className="ml-2 font-medium">AI Tutor</span>
                      <span className="ml-2">0%</span>
                    </div>
                  </div>
                  <Progress value={0} className="h-2" />
                </div>
              </CardContent>
            </Card>

            {/* Performance Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <Card>
                <CardContent className="p-6 text-center">
                  <div className="text-2xl font-bold text-blue-600">0h 30m</div>
                  <p className="text-sm text-gray-600">of 2h goal</p>
                  <div className="mt-2">
                    <Clock className="h-4 w-4 inline text-blue-500" />
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="p-6 text-center">
                  <div className="text-2xl font-bold text-yellow-600">7 🔥</div>
                  <p className="text-sm text-gray-600">days consistent</p>
                  <div className="mt-2">
                    <Trophy className="h-4 w-4 inline text-yellow-500" />
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="p-6 text-center">
                  <div className="text-2xl font-bold text-green-600">75%</div>
                  <p className="text-sm text-gray-600">vs target</p>
                  <div className="mt-2">
                    <TrendingUp className="h-4 w-4 inline text-green-500" />
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="p-6 text-center">
                  <div className="text-2xl font-bold text-purple-600">14</div>
                  <p className="text-sm text-gray-600">this week</p>
                  <div className="mt-2">
                    <Brain className="h-4 w-4 inline text-purple-500" />
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Study Progress */}
            <Card className="border border-blue-200 bg-blue-50">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <div className="p-3 bg-blue-100 rounded-lg">
                    <BarChart3 className="h-6 w-6 text-blue-600" />
                  </div>
                  <div className="ml-4">
                    <h3 className="text-lg font-semibold text-gray-900">Subject & Chapter Progress</h3>
                    <p className="text-sm text-gray-600">Track your learning across different topics</p>
                  </div>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-3 bg-white rounded-lg border border-blue-100">
                    <div className="flex items-center">
                      <div className="w-3 h-3 bg-red-500 rounded-full mr-3"></div>
                      <div>
                        <div className="font-semibold text-gray-900">Mathematics</div>
                        <Badge variant="secondary" className="bg-blue-100 text-blue-700">
                          1/15 chapters
                        </Badge>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-gray-900">0%</div>
                      <div className="text-sm text-gray-500">mastery</div>
                    </div>
                  </div>
                  
                  <div className="text-center py-8">
                    <MessageCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600 mb-4">Ready to boost your learning?</p>
                    <div className="flex flex-col sm:flex-row gap-4 justify-center">
                      <Button 
                        size="sm"
                        className="bg-blue-600 hover:bg-blue-700"
                        onClick={() => window.location.href = '/tutor'}
                      >
                        <FileText className="h-4 w-4 mr-2" />
                        Revise Notes
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => window.location.href = '/tutor'}
                      >
                        <MessageCircle className="h-4 w-4 mr-2" />
                        Ask Tutor
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Today's Learning Path */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Calendar className="h-5 w-5 mr-2 text-purple-600" />
                  Today's Learning Path
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center p-3 bg-blue-50 rounded-lg">
                    <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white text-sm font-bold mr-3">
                      1
                    </div>
                    <div className="flex-1">
                      <div className="font-semibold">Quick Warm-up</div>
                      <div className="text-sm text-gray-600">Review yesterday's concepts</div>
                    </div>
                    <Badge variant="secondary" className="bg-blue-100 text-blue-700">
                      5 mins
                    </Badge>
                  </div>
                  
                  <div className="flex items-center p-3 bg-gray-50 rounded-lg opacity-60">
                    <div className="w-8 h-8 bg-gray-400 rounded-full flex items-center justify-center text-white text-sm font-bold mr-3">
                      2
                    </div>
                    <div className="flex-1">
                      <div className="font-semibold">New Chapter Introduction</div>
                      <div className="text-sm text-gray-600">Mathematics • Quadratic Equations</div>
                    </div>
                    <Badge variant="secondary" className="bg-blue-100 text-blue-700">
                      15 mins
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Right Sidebar */}
          <div className="space-y-6">
            
            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Zap className="h-5 w-5 mr-2 text-blue-600" />
                  Quick Actions
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button 
                  variant="default" 
                  className="w-full justify-start h-12 bg-blue-600 hover:bg-blue-700"
                  onClick={() => window.location.href = '/tutor'}
                >
                  <MessageCircle className="h-5 w-5 mr-3" />
                  <div className="text-left">
                    <div className="font-semibold">Solve Doubts</div>
                    <div className="text-xs text-blue-100">Get instant AI help</div>
                  </div>
                </Button>
                
                <Button 
                  variant="outline" 
                  className="w-full justify-start h-12 hover:bg-gray-50"
                  onClick={() => window.location.href = '/tests'}
                >
                  <Trophy className="h-5 w-5 mr-3" />
                  <div className="text-left">
                    <div className="font-semibold">Practice Tests</div>
                    <div className="text-xs text-gray-600">Test your knowledge</div>
                  </div>
                </Button>
                
                <Button 
                  className="w-full justify-start h-12 bg-blue-600 hover:bg-blue-700"
                  onClick={() => window.location.href = '/auto-notes'}
                >
                  <BookMarked className="h-5 w-5 mr-3" />
                  <div className="text-left">
                    <div className="font-semibold">Generate Notes</div>
                    <div className="text-xs text-blue-100">AI-powered notes</div>
                  </div>
                </Button>
              </CardContent>
            </Card>

            {/* Wellness Widget */}
            <Card className="border border-purple-200 bg-purple-50">
              <CardHeader>
                <CardTitle className="flex items-center text-purple-800">
                  <Heart className="h-5 w-5 mr-2" />
                  Wellness Check
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center py-4">
                  <div className="text-2xl mb-2">😊</div>
                  <p className="text-purple-700 font-medium mb-2">Feeling Good!</p>
                  <p className="text-sm text-purple-600 mb-4">
                    Great job maintaining balance
                  </p>
                  <Button 
                    size="sm" 
                    variant="outline" 
                    className="border-purple-300 text-purple-700 hover:bg-purple-100"
                    onClick={() => window.location.href = '/wellness'}
                  >
                    Take Wellness Check
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Recent Activity */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Clock className="h-5 w-5 mr-2 text-green-600" />
                  Recent Activity
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 text-sm">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
                      <span>Completed Math practice</span>
                    </div>
                    <span className="text-gray-500">2h ago</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <div className="w-2 h-2 bg-blue-500 rounded-full mr-3"></div>
                      <span>Asked AI Tutor query</span>
                    </div>
                    <span className="text-gray-500">4h ago</span>
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