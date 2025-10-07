import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { 
  BookOpen, 
  Trophy, 
  Clock, 
  Target, 
  RefreshCw,
  FileText,
  TrendingUp,
  Award,
  Calendar,
  CheckCircle,
  AlertCircle,
  Star,
  Filter,
  Search
} from 'lucide-react';

export default function TestLibrary({ onRetakeTest, onReviewTest }) {
  const [tests, setTests] = useState([]);
  const [filteredTests, setFilteredTests] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeFilter, setActiveFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSubject, setSelectedSubject] = useState('all');

  const backendUrl = process.env.REACT_APP_BACKEND_URL;

  useEffect(() => {
    fetchTestLibrary();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [tests, activeFilter, selectedSubject, searchQuery]);

  const fetchTestLibrary = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await fetch(`${backendUrl}/api/mock-tests/library`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setTests(data.tests || []);
        setStats(data.stats || {});
      }
    } catch (error) {
      console.error('Error fetching test library:', error);
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...tests];

    // Filter by category
    if (activeFilter !== 'all') {
      filtered = filtered.filter(test => test.category === activeFilter);
    }

    // Filter by subject
    if (selectedSubject !== 'all') {
      filtered = filtered.filter(test => 
        test.subjects && test.subjects.includes(selectedSubject)
      );
    }

    // Search filter
    if (searchQuery) {
      filtered = filtered.filter(test =>
        test.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        test.subjects?.some(sub => sub.toLowerCase().includes(searchQuery.toLowerCase()))
      );
    }

    setFilteredTests(filtered);
  };

  const getScoreColor = (accuracy) => {
    if (accuracy >= 85) return 'text-green-600 bg-green-50 border-green-200';
    if (accuracy >= 70) return 'text-blue-600 bg-blue-50 border-blue-200';
    if (accuracy >= 50) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    return 'text-red-600 bg-red-50 border-red-200';
  };

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'high_score':
        return <Trophy className="w-4 h-4 text-yellow-500" />;
      case 'retakable':
        return <RefreshCw className="w-4 h-4 text-blue-500" />;
      default:
        return <FileText className="w-4 h-4 text-gray-500" />;
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  const formatTime = (seconds) => {
    if (!seconds) return 'N/A';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  // Get unique subjects from all tests
  const allSubjects = [...new Set(tests.flatMap(test => test.subjects || []))];

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 p-4 md:p-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Loading your test library...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <BookOpen className="w-8 h-8 text-blue-600" />
            <h1 className="text-3xl font-bold text-gray-800">My Test Library</h1>
          </div>
          <p className="text-gray-600">Review, retake, and track your mock test journey</p>
        </div>

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <Card className="bg-white border-blue-200 hover:shadow-lg transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Total Tests</p>
                    <p className="text-3xl font-bold text-blue-600">{stats.total_tests || 0}</p>
                  </div>
                  <FileText className="w-10 h-10 text-blue-500 opacity-20" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-white border-green-200 hover:shadow-lg transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Avg. Accuracy</p>
                    <p className="text-3xl font-bold text-green-600">{stats.average_accuracy?.toFixed(1) || 0}%</p>
                  </div>
                  <Target className="w-10 h-10 text-green-500 opacity-20" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-white border-yellow-200 hover:shadow-lg transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 mb-1">High Scores</p>
                    <p className="text-3xl font-bold text-yellow-600">{stats.categories?.high_score || 0}</p>
                  </div>
                  <Trophy className="w-10 h-10 text-yellow-500 opacity-20" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-white border-purple-200 hover:shadow-lg transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 mb-1">To Retake</p>
                    <p className="text-3xl font-bold text-purple-600">{stats.categories?.retakable || 0}</p>
                  </div>
                  <RefreshCw className="w-10 h-10 text-purple-500 opacity-20" />
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Filters and Search */}
        <Card className="bg-white mb-6">
          <CardContent className="p-4">
            <div className="flex flex-col md:flex-row gap-4">
              {/* Search Bar */}
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <input
                    type="text"
                    placeholder="Search tests by name or subject..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              {/* Category Filters */}
              <div className="flex gap-2 flex-wrap">
                <Button
                  variant={activeFilter === 'all' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setActiveFilter('all')}
                  className="flex items-center gap-2"
                >
                  <Filter className="w-4 h-4" />
                  All
                </Button>
                <Button
                  variant={activeFilter === 'recent' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setActiveFilter('recent')}
                >
                  Recent
                </Button>
                <Button
                  variant={activeFilter === 'high_score' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setActiveFilter('high_score')}
                  className="flex items-center gap-2"
                >
                  <Trophy className="w-4 h-4" />
                  High Scores
                </Button>
                <Button
                  variant={activeFilter === 'retakable' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setActiveFilter('retakable')}
                  className="flex items-center gap-2"
                >
                  <RefreshCw className="w-4 h-4" />
                  Retakable
                </Button>
              </div>

              {/* Subject Filter */}
              {allSubjects.length > 0 && (
                <select
                  value={selectedSubject}
                  onChange={(e) => setSelectedSubject(e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="all">All Subjects</option>
                  {allSubjects.map(subject => (
                    <option key={subject} value={subject}>{subject}</option>
                  ))}
                </select>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Test Cards Grid */}
        {filteredTests.length === 0 ? (
          <Card className="bg-white">
            <CardContent className="p-12 text-center">
              <BookOpen className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-600 mb-2">No tests found</h3>
              <p className="text-gray-500 mb-6">
                {searchQuery || activeFilter !== 'all' || selectedSubject !== 'all'
                  ? 'Try adjusting your filters or search query'
                  : 'Start taking mock tests to build your library!'}
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredTests.map((test) => (
              <Card
                key={test.library_id || test.test_id}
                className="bg-white hover:shadow-xl transition-all duration-300 border border-gray-200 hover:border-blue-300"
              >
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      {getCategoryIcon(test.category)}
                      <Badge variant="outline" className="text-xs">
                        {test.exam_type || 'General'}
                      </Badge>
                    </div>
                    <div className={`px-3 py-1 rounded-full border ${getScoreColor(test.accuracy || 0)}`}>
                      <span className="text-sm font-bold">{test.accuracy?.toFixed(0) || 0}%</span>
                    </div>
                  </div>
                  <CardTitle className="text-lg font-semibold text-gray-800 line-clamp-2">
                    {test.title || 'Mock Test'}
                  </CardTitle>
                </CardHeader>

                <CardContent>
                  {/* Subjects */}
                  <div className="flex flex-wrap gap-2 mb-4">
                    {test.subjects?.map((subject, idx) => (
                      <Badge key={idx} variant="secondary" className="text-xs">
                        {subject}
                      </Badge>
                    ))}
                  </div>

                  {/* Stats */}
                  <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
                    <div className="flex items-center gap-2 text-gray-600">
                      <CheckCircle className="w-4 h-4 text-green-500" />
                      <span>{test.correct_answers}/{test.total_questions}</span>
                    </div>
                    <div className="flex items-center gap-2 text-gray-600">
                      <Clock className="w-4 h-4 text-blue-500" />
                      <span>{formatTime(test.time_taken)}</span>
                    </div>
                    <div className="flex items-center gap-2 text-gray-600">
                      <Award className="w-4 h-4 text-purple-500" />
                      <span>{test.score}/{test.max_score}</span>
                    </div>
                    <div className="flex items-center gap-2 text-gray-600">
                      <Calendar className="w-4 h-4 text-orange-500" />
                      <span className="text-xs">{formatDate(test.attempt_date)}</span>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      className="flex-1"
                      onClick={() => onReviewTest && onReviewTest(test.test_id)}
                    >
                      <FileText className="w-4 h-4 mr-2" />
                      Review
                    </Button>
                    <Button
                      size="sm"
                      className="flex-1 bg-blue-600 hover:bg-blue-700"
                      onClick={() => onRetakeTest && onRetakeTest(test.test_id)}
                    >
                      <RefreshCw className="w-4 h-4 mr-2" />
                      Retake
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
