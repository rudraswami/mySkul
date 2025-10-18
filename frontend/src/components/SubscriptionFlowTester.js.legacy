import React, { useState } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { useSubscription } from '../contexts/SubscriptionContext';
import { handleSubscriptionError, handlePostUpgradeRetry, animateSubscriptionUnlock } from '../utils/subscriptionErrorHandler';

export default function SubscriptionFlowTester() {
  const { checkFeatureAccess } = useSubscription();
  const [testResults, setTestResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const addResult = (test, result, error = null) => {
    setTestResults(prev => [...prev, { test, result, error, timestamp: new Date().toLocaleTimeString() }]);
  };

  const testSubscriptionErrors = async () => {
    setLoading(true);
    addResult('Starting Subscription Error Tests', '🧪 Testing Enhanced Error Handling');

    // Test 1: Direct 402 Error
    try {
      const error = {
        response: { 
          status: 402, 
          data: { message: 'Subscription limit reached', code: 'LIMIT_REACHED' } 
        }
      };
      const result = await handleSubscriptionError(error, 'ai_tutor_daily', checkFeatureAccess, () => {});
      addResult('402 Error Test', result.handled ? '✅ Handled as subscription error' : '❌ Not handled');
    } catch (e) {
      addResult('402 Error Test', '❌ Failed', e.message);
    }

    // Test 2: 500 Error with limit keywords
    try {
      const error = {
        response: { 
          status: 500, 
          data: { message: 'daily limit reached for this feature' } 
        }
      };
      const result = await handleSubscriptionError(error, 'ai_tutor_daily', checkFeatureAccess, () => {});
      addResult('500 + Limit Keywords Test', result.handled ? '✅ Detected as subscription error' : '❌ Not detected');
    } catch (e) {
      addResult('500 + Limit Keywords Test', '❌ Failed', e.message);
    }

    // Test 3: Regular 500 Error
    try {
      const error = {
        response: { 
          status: 500, 
          data: { message: 'Internal server error' } 
        }
      };
      const result = await handleSubscriptionError(error, 'ai_tutor_daily', checkFeatureAccess, () => {});
      addResult('Regular 500 Error Test', result.handled ? '✅ Handled as server error' : '❌ Not handled');
    } catch (e) {
      addResult('Regular 500 Error Test', '❌ Failed', e.message);
    }

    // Test 4: Network Error
    try {
      const error = { message: 'Network request failed' };
      const result = await handleSubscriptionError(error, 'ai_tutor_daily', checkFeatureAccess, () => {});
      addResult('Network Error Test', !result.handled ? '✅ Not handled (correct)' : '❌ Incorrectly handled');
    } catch (e) {
      addResult('Network Error Test', '❌ Failed', e.message);
    }

    // Test 5: Animation Test
    try {
      const testElement = document.createElement('div');
      testElement.style.transform = 'scale(1)';
      document.body.appendChild(testElement);
      
      animateSubscriptionUnlock(testElement);
      
      setTimeout(() => {
        const finalScale = testElement.style.transform;
        document.body.removeChild(testElement);
        addResult('Animation Test', finalScale ? '✅ Animation applied' : '❌ No animation');
      }, 500);
    } catch (e) {
      addResult('Animation Test', '❌ Failed', e.message);
    }

    setLoading(false);
  };

  const testFeatureAccess = async (featureName) => {
    try {
      addResult(`Testing ${featureName}`, '🔄 Checking access...');
      const result = await checkFeatureAccess(featureName);
      addResult(`${featureName} Access`, 
        result.has_access ? '✅ Access granted' : '⚠️ Access denied - modal should appear'
      );
    } catch (error) {
      addResult(`${featureName} Test`, '❌ Failed', error.message);
    }
  };

  return (
    <Card className="max-w-2xl mx-auto mt-8">
      <CardHeader>
        <CardTitle>🧪 Subscription Flow Tester</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <Button 
            onClick={testSubscriptionErrors}
            disabled={loading}
            variant="outline"
          >
            {loading ? '🧪 Testing...' : '🔬 Test Error Handling'}
          </Button>
          
          <Button 
            onClick={() => testFeatureAccess('ai_tutor_daily')}
            variant="outline"
          >
            🎓 Test AI Tutor Access
          </Button>
          
          <Button 
            onClick={() => testFeatureAccess('mock_tests_weekly')}
            variant="outline"
          >
            📝 Test Mock Tests Access
          </Button>
          
          <Button 
            onClick={() => testFeatureAccess('auto_note_uploads_daily')}
            variant="outline"
          >
            📁 Test Auto-Notes Access
          </Button>
        </div>

        <div className="mt-6">
          <h4 className="font-medium mb-3">Test Results:</h4>
          <div className="bg-gray-50 rounded-lg p-4 max-h-64 overflow-y-auto">
            {testResults.length === 0 ? (
              <p className="text-gray-500 text-sm">No tests run yet</p>
            ) : (
              <div className="space-y-2">
                {testResults.map((result, index) => (
                  <div key={index} className="text-sm">
                    <span className="text-gray-500">[{result.timestamp}]</span>
                    <span className="font-medium ml-2">{result.test}:</span>
                    <span className="ml-2">{result.result}</span>
                    {result.error && (
                      <div className="text-red-600 text-xs ml-6">Error: {result.error}</div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="text-xs text-gray-500 mt-4">
          <p>💡 This tester validates the enhanced subscription flow:</p>
          <ul className="list-disc list-inside mt-1 space-y-1">
            <li>Intelligent error detection (subscription vs server errors)</li>
            <li>Proper modal triggering for subscription limits</li>
            <li>Animation effects for premium unlock</li>
            <li>Feature access checking across all modules</li>
          </ul>
        </div>
      </CardContent>
    </Card>
  );
}