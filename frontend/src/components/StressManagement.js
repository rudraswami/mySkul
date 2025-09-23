import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Progress } from './ui/progress';
import { 
  Heart, 
  Brain, 
  Moon, 
  Smile, 
  AlertTriangle,
  CheckCircle,
  Target,
  TrendingUp,
  BookOpen,
  Clock
} from 'lucide-react';

export default function StressManagement() {
  const [assessmentData, setAssessmentData] = useState({
    stress_level: 5,
    anxiety_level: 5,
    sleep_quality: 5,
    study_motivation: 5,
    physical_symptoms: [],
    emotional_state: 'neutral'
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [wellnessScore, setWellnessScore] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [motivationalContent, setMotivationalContent] = useState([]);

  const backendUrl = process.env.REACT_APP_BACKEND_URL;

  useEffect(() => {
    loadMotivationalContent();
  }, []);

  const loadMotivationalContent = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${backendUrl}/api/wellness/motivational-content`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setMotivationalContent(data.daily_content || []);
      }
    } catch (error) {
      console.error('Error loading motivational content:', error);
    }
  };

  const submitAssessment = async () => {
    setIsSubmitting(true);
    try {
      const token = localStorage.getItem('token');
      
      if (!token) {
        alert('Please log in to submit assessment');
        return;
      }
      
      const response = await fetch(`${backendUrl}/api/wellness/stress-assessment`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(assessmentData)
      });
      
      if (response.ok) {
        const data = await response.json();
        setWellnessScore(data.wellness_score);
        setRecommendations(data.recommendations || []);
        
        // Reload motivational content after assessment
        loadMotivationalContent();
        
        // Success feedback
        alert(`Assessment completed! Your wellness score: ${data.wellness_score.toFixed(1)}/10`);
      } else {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        alert(`Error: ${errorData.detail || 'Failed to submit assessment'}`);
        console.error('Assessment submission failed:', response.status, errorData);
      }
    } catch (error) {
      console.error('Error submitting assessment:', error);
      alert('Network error occurred. Please check your connection and try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const physicalSymptoms = [
    'Headaches',
    'Fatigue',
    'Insomnia',
    'Muscle tension',
    'Appetite changes',
    'Digestive issues',
    'Rapid heartbeat',
    'Difficulty concentrating'
  ];

  const emotionalStates = [
    'Very positive',
    'Positive',
    'Neutral',
    'Anxious',
    'Overwhelmed',
    'Frustrated',
    'Depressed'
  ];

  const getWellnessColor = (score) => {
    if (score >= 8) return 'text-green-600';
    if (score >= 6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getContentIcon = (type) => {
    switch (type) {
      case 'quote': return <Heart className="h-5 w-5 text-pink-500" />;
      case 'tip': return <BookOpen className="h-5 w-5 text-blue-500" />;
      case 'exercise': return <Target className="h-5 w-5 text-green-500" />;
      default: return <Brain className="h-5 w-5 text-purple-500" />;
    }
  };

  return (
    <div className="p-8 bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Wellness & Stress Management</h1>
        <p className="text-gray-600">
          Take care of your mental health with personalized wellness tools and stress management techniques
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Stress Assessment */}
        <div className="lg:col-span-2 space-y-6">
          <Card className="border-0 shadow-md">
            <CardHeader>
              <CardTitle className="flex items-center">
                <Brain className="h-5 w-5 mr-2 text-purple-600" />
                Daily Wellness Check-in
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Stress Level */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Stress Level (1 = Very Low, 10 = Very High)
                </label>
                <div className="flex items-center space-x-4">
                  <input
                    type="range"
                    min="1"
                    max="10"
                    value={assessmentData.stress_level}
                    onChange={(e) => setAssessmentData({
                      ...assessmentData, 
                      stress_level: parseInt(e.target.value)
                    })}
                    className="flex-1"
                  />
                  <span className="font-medium text-lg w-8">{assessmentData.stress_level}</span>
                </div>
              </div>

              {/* Anxiety Level */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Anxiety Level (1 = Very Low, 10 = Very High)
                </label>
                <div className="flex items-center space-x-4">
                  <input
                    type="range"
                    min="1"
                    max="10"
                    value={assessmentData.anxiety_level}
                    onChange={(e) => setAssessmentData({
                      ...assessmentData, 
                      anxiety_level: parseInt(e.target.value)
                    })}
                    className="flex-1"
                  />
                  <span className="font-medium text-lg w-8">{assessmentData.anxiety_level}</span>
                </div>
              </div>

              {/* Sleep Quality */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Sleep Quality (1 = Very Poor, 10 = Excellent)
                </label>
                <div className="flex items-center space-x-4">
                  <input
                    type="range"
                    min="1"
                    max="10"
                    value={assessmentData.sleep_quality}
                    onChange={(e) => setAssessmentData({
                      ...assessmentData, 
                      sleep_quality: parseInt(e.target.value)
                    })}
                    className="flex-1"
                  />
                  <span className="font-medium text-lg w-8">{assessmentData.sleep_quality}</span>
                </div>
              </div>

              {/* Study Motivation */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Study Motivation (1 = Very Low, 10 = Very High)
                </label>
                <div className="flex items-center space-x-4">
                  <input
                    type="range"
                    min="1"
                    max="10"
                    value={assessmentData.study_motivation}
                    onChange={(e) => setAssessmentData({
                      ...assessmentData, 
                      study_motivation: parseInt(e.target.value)
                    })}
                    className="flex-1"
                  />
                  <span className="font-medium text-lg w-8">{assessmentData.study_motivation}</span>
                </div>
              </div>

              {/* Physical Symptoms */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Physical Symptoms (Select all that apply)
                </label>
                <div className="grid grid-cols-2 gap-2">
                  {physicalSymptoms.map((symptom) => (
                    <label key={symptom} className="flex items-center">
                      <input
                        type="checkbox"
                        checked={assessmentData.physical_symptoms.includes(symptom)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setAssessmentData({
                              ...assessmentData,
                              physical_symptoms: [...assessmentData.physical_symptoms, symptom]
                            });
                          } else {
                            setAssessmentData({
                              ...assessmentData,
                              physical_symptoms: assessmentData.physical_symptoms.filter(s => s !== symptom)
                            });
                          }
                        }}
                        className="mr-2"
                      />
                      <span className="text-sm">{symptom}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Emotional State */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Overall Emotional State
                </label>
                <select
                  value={assessmentData.emotional_state}
                  onChange={(e) => setAssessmentData({
                    ...assessmentData, 
                    emotional_state: e.target.value
                  })}
                  className="w-full p-2 border border-gray-300 rounded-md"
                >
                  {emotionalStates.map((state) => (
                    <option key={state} value={state.toLowerCase()}>{state}</option>
                  ))}
                </select>
              </div>

              <Button 
                onClick={submitAssessment} 
                disabled={isSubmitting}
                className="w-full bg-purple-600 hover:bg-purple-700"
              >
                {isSubmitting ? 'Analyzing...' : 'Get Wellness Recommendations'}
              </Button>
            </CardContent>
          </Card>

          {/* Recommendations */}
          {recommendations.length > 0 && (
            <Card className="border-0 shadow-md">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Target className="h-5 w-5 mr-2 text-green-600" />
                  Personalized Recommendations
                  {wellnessScore && (
                    <span className={`ml-2 text-sm ${getWellnessColor(wellnessScore)}`}>
                      Wellness Score: {wellnessScore.toFixed(1)}/10
                    </span>
                  )}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {recommendations.map((recommendation, index) => (
                    <div key={index} className="flex items-start p-3 bg-green-50 rounded-lg">
                      <CheckCircle className="h-5 w-5 text-green-600 mr-3 mt-0.5 flex-shrink-0" />
                      <p className="text-sm text-gray-800">{recommendation}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Motivational Content & Tools */}
        <div className="space-y-6">
          {/* Daily Motivation */}
          <Card className="border-0 shadow-md">
            <CardHeader>
              <CardTitle className="flex items-center">
                <Smile className="h-5 w-5 mr-2 text-yellow-500" />
                Daily Motivation
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {motivationalContent.length > 0 ? (
                motivationalContent.map((content) => (
                  <div key={content.content_id} className="p-4 border border-gray-200 rounded-lg">
                    <div className="flex items-start mb-2">
                      {getContentIcon(content.content_type)}
                      <h4 className="font-medium text-gray-900 ml-2">{content.title}</h4>
                    </div>
                    <p className="text-sm text-gray-700">{content.content}</p>
                  </div>
                ))
              ) : (
                <div className="text-center py-8 text-gray-500">
                  Complete your wellness check-in to get personalized motivational content!
                </div>
              )}
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card className="border-0 shadow-md">
            <CardHeader>
              <CardTitle className="flex items-center">
                <Heart className="h-5 w-5 mr-2 text-red-500" />
                Quick Wellness Tools
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button className="w-full justify-start bg-blue-600 hover:bg-blue-700">
                <Moon className="h-4 w-4 mr-2" />
                Guided Meditation (5 min)
              </Button>
              
              <Button variant="outline" className="w-full justify-start">
                <Target className="h-4 w-4 mr-2" />
                Breathing Exercise
              </Button>
              
              <Button variant="outline" className="w-full justify-start">
                <Clock className="h-4 w-4 mr-2" />
                Study Break Reminder
              </Button>

              <Button variant="outline" className="w-full justify-start">
                <TrendingUp className="h-4 w-4 mr-2" />
                Progress Celebration
              </Button>
            </CardContent>
          </Card>

          {/* Wellness Tips */}
          <Card className="border-0 shadow-md">
            <CardHeader>
              <CardTitle>Daily Wellness Tips</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3 text-sm">
                <div className="flex items-start p-3 bg-yellow-50 rounded-lg">
                  <AlertTriangle className="h-4 w-4 text-yellow-600 mr-2 mt-0.5 flex-shrink-0" />
                  <p>Take a 10-minute break every hour while studying to maintain focus and reduce mental fatigue.</p>
                </div>
                
                <div className="flex items-start p-3 bg-blue-50 rounded-lg">
                  <Moon className="h-4 w-4 text-blue-600 mr-2 mt-0.5 flex-shrink-0" />
                  <p>Maintain a consistent sleep schedule of 7-8 hours for optimal cognitive performance.</p>
                </div>
                
                <div className="flex items-start p-3 bg-green-50 rounded-lg">
                  <Heart className="h-4 w-4 text-green-600 mr-2 mt-0.5 flex-shrink-0" />
                  <p>Practice gratitude by writing down 3 things you're grateful for each day.</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}