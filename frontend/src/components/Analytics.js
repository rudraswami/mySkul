import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { 
  BarChart3, 
  TrendingUp, 
  Clock, 
  Target, 
  BookOpen,
  Award,
  Calendar,
  Brain
} from 'lucide-react';

export default function Analytics() {
  const [selectedPeriod, setSelectedPeriod] = useState('week');

  // Sample analytics data
  const studyData = {
    totalTime: 42, // hours
    weeklyGoal: 50,
    streak: 7,
    averageSession: 2.5,
    subjects: [
      { name: 'Mathematics', time: 18, progress: 85, color: 'blue' },
      { name: 'Physics', time: 15, progress: 72, color: 'green' },
      { name: 'Chemistry', time: 9, progress: 65, color: 'purple' }
    ]
  };

  const performanceData = [
    { subject: 'Mathematics', scores: [78, 82, 85, 88, 90, 92, 89], trend: '+14%' },
    { subject: 'Physics', scores: [65, 68, 70, 72, 75, 78, 80], trend: '+23%' },
    { subject: 'Chemistry', scores: [70, 72, 69, 74, 76, 78, 81], trend: '+16%' }
  ];

  const weakAreas = [
    { topic: 'Trigonometry', subject: 'Mathematics', accuracy: 68, priority: 'High' },
    { topic: 'Thermodynamics', subject: 'Physics', accuracy: 72, priority: 'Medium' },
    { topic: 'Organic Reactions', subject: 'Chemistry', accuracy: 65, priority: 'High' }
  ];

  const getSubjectColor = (color) => {
    const colors = {
      blue: 'bg-blue-100 text-blue-800',
      green: 'bg-green-100 text-green-800',
      purple: 'bg-purple-100 text-purple-800'
    };
    return colors[color] || 'bg-gray-100 text-gray-800';
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'High': return 'bg-red-100 text-red-800';
      case 'Medium': return 'bg-yellow-100 text-yellow-800';
      case 'Low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="p-8 bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Learning Analytics</h1>
          <p className="text-gray-600">
            Track your progress and identify areas for improvement
          </p>
        </div>
        
        <div className="flex space-x-2">
          {['week', 'month', 'quarter'].map((period) => (
            <Button
              key={period}
              variant={selectedPeriod === period ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSelectedPeriod(period)}
              className="capitalize"
            >
              {period}
            </Button>
          ))}
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card className="border-0 shadow-md">
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Clock className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Study Time</p>
                <p className="text-2xl font-bold text-gray-900">{studyData.totalTime}h</p>
                <p className="text-xs text-gray-500">This week</p>
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
                <p className="text-sm font-medium text-gray-600">Weekly Goal</p>
                <p className="text-2xl font-bold text-gray-900">
                  {Math.round((studyData.totalTime / studyData.weeklyGoal) * 100)}%
                </p>
                <Progress 
                  value={(studyData.totalTime / studyData.weeklyGoal) * 100} 
                  className="mt-1 h-2" 
                />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-md">
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-orange-100 rounded-lg">
                <Award className="h-6 w-6 text-orange-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Current Streak</p>
                <p className="text-2xl font-bold text-gray-900">{studyData.streak} days</p>
                <p className="text-xs text-green-600">Keep it up!</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-md">
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Brain className="h-6 w-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Avg Session</p>
                <p className="text-2xl font-bold text-gray-900">{studyData.averageSession}h</p>
                <p className="text-xs text-gray-500">Per session</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="overview" className="space-y-8">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="subjects">Subjects</TabsTrigger>
          <TabsTrigger value="improvement">Areas to Improve</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Study Distribution */}
            <Card className="border-0 shadow-md">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <BarChart3 className="h-5 w-5 mr-2 text-blue-600" />
                  Study Time Distribution
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {studyData.subjects.map((subject, index) => (
                    <div key={index}>
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center">
                          <Badge className={getSubjectColor(subject.color)}>
                            {subject.name}
                          </Badge>
                        </div>
                        <span className="text-sm font-medium text-gray-700">
                          {subject.time}h ({Math.round((subject.time / studyData.totalTime) * 100)}%)
                        </span>
                      </div>
                      <Progress 
                        value={(subject.time / studyData.totalTime) * 100} 
                        className="h-3" 
                      />
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Weekly Activity */}
            <Card className="border-0 shadow-md">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Calendar className="h-5 w-5 mr-2 text-green-600" />
                  Weekly Activity
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-7 gap-2">
                  {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((day, index) => {
                    const hours = [3, 4, 2, 5, 6, 4, 3][index];
                    const intensity = Math.min(hours / 6, 1);
                    
                    return (
                      <div key={day} className="text-center">
                        <div className="text-xs text-gray-500 mb-1">{day}</div>
                        <div 
                          className="w-full h-16 rounded-lg flex items-end justify-center"
                          style={{
                            backgroundColor: `rgba(59, 130, 246, ${intensity})`,
                            border: '1px solid #e5e7eb'
                          }}
                        >
                          <span className="text-xs text-white font-medium mb-1">
                            {hours}h
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Performance Tab */}
        <TabsContent value="performance" className="space-y-6">
          <Card className="border-0 shadow-md">
            <CardHeader>
              <CardTitle className="flex items-center">
                <TrendingUp className="h-5 w-5 mr-2 text-green-600" />
                Performance Trends
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {performanceData.map((subject, index) => (
                  <div key={index} className="p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="font-semibold text-gray-900">{subject.subject}</h4>
                      <Badge variant="outline" className="text-green-600 border-green-200">
                        {subject.trend}
                      </Badge>
                    </div>
                    
                    <div className="flex items-end space-x-2 h-20">
                      {subject.scores.map((score, i) => (
                        <div 
                          key={i}
                          className="flex-1 bg-blue-200 rounded-t-sm"
                          style={{ height: `${(score / 100) * 100}%` }}
                          title={`Week ${i + 1}: ${score}%`}
                        />
                      ))}
                    </div>
                    
                    <div className="flex justify-between text-xs text-gray-500 mt-2">
                      <span>7 weeks ago</span>
                      <span>Current: {subject.scores[subject.scores.length - 1]}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Subjects Tab */}
        <TabsContent value="subjects" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {studyData.subjects.map((subject, index) => (
              <Card key={index} className="border-0 shadow-md">
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <span className="flex items-center">
                      <BookOpen className="h-5 w-5 mr-2 text-gray-600" />
                      {subject.name}
                    </span>
                    <Badge className={getSubjectColor(subject.color)}>
                      {subject.progress}%
                    </Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between text-sm mb-2">
                        <span className="text-gray-600">Overall Progress</span>
                        <span className="font-medium">{subject.progress}%</span>
                      </div>
                      <Progress value={subject.progress} className="h-2" />
                    </div>
                    
                    <div>
                      <div className="flex justify-between text-sm mb-2">
                        <span className="text-gray-600">Time Spent</span>
                        <span className="font-medium">{subject.time}h</span>
                      </div>
                      <Progress 
                        value={(subject.time / studyData.totalTime) * 100} 
                        className="h-2" 
                      />
                    </div>

                    <div className="pt-3 border-t border-gray-200">
                      <Button variant="outline" size="sm" className="w-full">
                        View Detailed Report
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Improvement Areas Tab */}
        <TabsContent value="improvement" className="space-y-6">
          <Card className="border-0 shadow-md">
            <CardHeader>
              <CardTitle className="flex items-center">
                <Target className="h-5 w-5 mr-2 text-red-600" />
                Areas Needing Attention
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {weakAreas.map((area, index) => (
                  <div key={index} className="p-4 border border-gray-200 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-3">
                        <h4 className="font-semibold text-gray-900">{area.topic}</h4>
                        <Badge variant="outline">
                          {area.subject}
                        </Badge>
                        <Badge className={getPriorityColor(area.priority)}>
                          {area.priority} Priority
                        </Badge>
                      </div>
                      <span className="text-sm font-medium text-gray-700">
                        {area.accuracy}% Accuracy
                      </span>
                    </div>
                    
                    <Progress value={area.accuracy} className="mb-3 h-2" />
                    
                    <div className="flex justify-between items-center">
                      <p className="text-sm text-gray-600">
                        Recommended: Focus on practice problems and concept review
                      </p>
                      <Button size="sm" variant="outline">
                        Study Plan
                      </Button>
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                <div className="flex items-center mb-2">
                  <Brain className="h-5 w-5 text-blue-600 mr-2" />
                  <span className="font-medium text-blue-900">AI Recommendation</span>
                </div>
                <p className="text-sm text-blue-800">
                  Based on your performance, we recommend spending 30% more time on Trigonometry 
                  and Thermodynamics. Use our AI tutor for personalized practice problems in these areas.
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}