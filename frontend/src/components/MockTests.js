import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { 
  FileText, 
  Clock, 
  Target, 
  Award, 
  TrendingUp, 
  CheckCircle,
  Circle
} from 'lucide-react';

export default function MockTests() {
  const [selectedCategory, setSelectedCategory] = useState('all');

  // Sample mock test data
  const mockTests = [
    {
      id: 1,
      title: 'JEE Main Mathematics - Full Length Test',
      duration: '3 hours',
      questions: 75,
      difficulty: 'High',
      completed: false,
      bestScore: null,
      subjects: ['Mathematics'],
      description: 'Comprehensive test covering all mathematics topics for JEE Main'
    },
    {
      id: 2,
      title: 'Physics Mechanics - Chapter Test',
      duration: '1.5 hours',
      questions: 30,
      difficulty: 'Medium',
      completed: true,
      bestScore: 85,
      subjects: ['Physics'],
      description: 'Focus test on mechanics including motion, forces, and energy'
    },
    {
      id: 3,
      title: 'Organic Chemistry - Quick Assessment',
      duration: '45 minutes',
      questions: 20,
      difficulty: 'Easy',
      completed: true,
      bestScore: 92,
      subjects: ['Chemistry'],
      description: 'Assessment covering basic organic chemistry concepts'
    }
  ];

  const recentResults = [
    {
      testName: 'Physics Mechanics - Chapter Test',
      score: 85,
      date: '2 days ago',
      rank: 156,
      totalStudents: 1250
    },
    {
      testName: 'Algebra Fundamentals',
      score: 78,
      date: '1 week ago',
      rank: 89,
      totalStudents: 890
    },
    {
      testName: 'Organic Chemistry Basics',
      score: 92,
      date: '2 weeks ago',
      rank: 45,
      totalStudents: 2100
    }
  ];

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'Easy': return 'bg-green-100 text-green-800';
      case 'Medium': return 'bg-yellow-100 text-yellow-800';
      case 'High': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getScoreColor = (score) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 75) return 'text-blue-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="p-8 bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Mock Tests</h1>
        <p className="text-gray-600">
          Practice with our comprehensive test series designed to simulate real exam conditions
        </p>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card className="border-0 shadow-md">
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <FileText className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Tests Taken</p>
                <p className="text-2xl font-bold text-gray-900">12</p>
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
                <p className="text-sm font-medium text-gray-600">Average Score</p>
                <p className="text-2xl font-bold text-gray-900">82%</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-md">
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Award className="h-6 w-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Best Rank</p>
                <p className="text-2xl font-bold text-gray-900">#45</p>
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
                <p className="text-sm font-medium text-gray-600">Improvement</p>
                <p className="text-2xl font-bold text-green-600">+15%</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Available Tests */}
        <div className="lg:col-span-2">
          <Card className="border-0 shadow-md">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="flex items-center">
                <FileText className="h-5 w-5 mr-2 text-blue-600" />
                Available Tests
              </CardTitle>
              <div className="flex space-x-2">
                <Button
                  variant={selectedCategory === 'all' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setSelectedCategory('all')}
                >
                  All
                </Button>
                <Button
                  variant={selectedCategory === 'full' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setSelectedCategory('full')}
                >
                  Full Length
                </Button>
                <Button
                  variant={selectedCategory === 'chapter' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setSelectedCategory('chapter')}
                >
                  Chapter-wise
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {mockTests.map((test) => (
                  <div key={test.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center mb-2">
                          {test.completed ? (
                            <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                          ) : (
                            <Circle className="h-5 w-5 text-gray-300 mr-2" />
                          )}
                          <h3 className="font-semibold text-gray-900">{test.title}</h3>
                          <Badge 
                            className={`ml-2 ${getDifficultyColor(test.difficulty)}`}
                          >
                            {test.difficulty}
                          </Badge>
                        </div>
                        
                        <p className="text-sm text-gray-600 mb-3">{test.description}</p>
                        
                        <div className="flex items-center space-x-4 text-sm text-gray-500">
                          <div className="flex items-center">
                            <Clock className="h-4 w-4 mr-1" />
                            {test.duration}
                          </div>
                          <div className="flex items-center">
                            <FileText className="h-4 w-4 mr-1" />
                            {test.questions} questions
                          </div>
                          {test.completed && test.bestScore && (
                            <div className="flex items-center">
                              <Award className="h-4 w-4 mr-1" />
                              <span className={getScoreColor(test.bestScore)}>
                                Best: {test.bestScore}%
                              </span>
                            </div>
                          )}
                        </div>
                      </div>
                      
                      <div className="ml-4">
                        <Button 
                          className="bg-blue-600 hover:bg-blue-700"
                          size="sm"
                        >
                          {test.completed ? 'Retake' : 'Start Test'}
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-6 text-center">
                <Button variant="outline" className="w-full">
                  View All Tests
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Recent Results & Performance */}
        <div className="space-y-6">
          {/* Recent Results */}
          <Card className="border-0 shadow-md">
            <CardHeader>
              <CardTitle className="flex items-center">
                <TrendingUp className="h-5 w-5 mr-2 text-green-600" />
                Recent Results
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recentResults.map((result, index) => (
                  <div key={index} className="p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <p className="font-medium text-sm text-gray-900 truncate">
                        {result.testName}
                      </p>
                      <span className={`text-sm font-bold ${getScoreColor(result.score)}`}>
                        {result.score}%
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-xs text-gray-500">
                      <span>Rank: #{result.rank}/{result.totalStudents}</span>
                      <span>{result.date}</span>
                    </div>
                    <Progress 
                      value={result.score} 
                      className="mt-2 h-2" 
                    />
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Performance Insights */}
          <Card className="border-0 shadow-md">
            <CardHeader>
              <CardTitle className="flex items-center">
                <Target className="h-5 w-5 mr-2 text-purple-600" />
                Performance Insights
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-600">Strong Area: Mathematics</span>
                    <span className="font-medium text-green-600">90%</span>
                  </div>
                  <Progress value={90} className="h-2" />
                </div>
                
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-600">Needs Work: Physics</span>
                    <span className="font-medium text-yellow-600">68%</span>
                  </div>
                  <Progress value={68} className="h-2" />
                </div>
                
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-600">Time Management</span>
                    <span className="font-medium text-blue-600">75%</span>
                  </div>
                  <Progress value={75} className="h-2" />
                </div>
              </div>

              <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                <p className="text-sm text-blue-800">
                  💡 <strong>Tip:</strong> Focus more on Physics concepts. Take chapter-wise tests to improve specific areas.
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card className="border-0 shadow-md">
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button className="w-full justify-start bg-green-600 hover:bg-green-700">
                <Award className="h-4 w-4 mr-2" />
                View Detailed Analysis
              </Button>
              
              <Button variant="outline" className="w-full justify-start">
                <FileText className="h-4 w-4 mr-2" />
                Practice Questions
              </Button>
              
              <Button variant="outline" className="w-full justify-start">
                <Clock className="h-4 w-4 mr-2" />
                Schedule Test
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}