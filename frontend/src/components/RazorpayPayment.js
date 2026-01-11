import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Button } from './ui/button.jsx';
import { LoadingSpinner } from './ui/loading.jsx';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card.jsx';
import { CheckCircle, AlertCircle, CreditCard, Smartphone, Building } from 'lucide-react';

const RazorpayPayment = ({ 
  planName, 
  billingCycle, 
  amount, 
  onSuccess, 
  onError, 
  onCancel,
  userDetails 
}) => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [paymentStatus, setPaymentStatus] = useState(null);
  const [razorpayLoaded, setRazorpayLoaded] = useState(false);

  const backendUrl = process.env.REACT_APP_BACKEND_URL;

  // Load Razorpay script dynamically
  useEffect(() => {
    const loadRazorpayScript = () => {
      return new Promise((resolve) => {
        // Check if Razorpay is already loaded
        if (window.Razorpay) {
          setRazorpayLoaded(true);
          resolve(true);
          return;
        }

        const script = document.createElement('script');
        script.src = 'https://checkout.razorpay.com/v1/checkout.js';
        script.async = true;
        script.onload = () => {
          setRazorpayLoaded(true);
          resolve(true);
        };
        script.onerror = () => {
          console.error('Failed to load Razorpay SDK');
          resolve(false);
        };
        document.body.appendChild(script);
      });
    };

    loadRazorpayScript();
  }, []);

  const handlePayment = async () => {
    if (!razorpayLoaded || !window.Razorpay) {
      onError?.('Razorpay SDK not loaded. Please refresh and try again.');
      return;
    }

    setIsProcessing(true);
    setPaymentStatus(null);

    try {
      // Get JWT token
      const token = localStorage.getItem('dhruv_ai_token');
      if (!token) {
        throw new Error('Authentication required');
      }

      // CRITICAL FIX: Don't send amount - backend calculates from plan config
      // Frontend only sends plan_name and billing_cycle
      const orderResponse = await axios.post(
        `${backendUrl}/api/subscription/razorpay/create-order`,
        {
          plan_name: planName.toUpperCase(),  // "FREE", "STUDENT", "PRO" - must match backend
          billing_cycle: billingCycle,        // "monthly", "yearly"
          user_id: userDetails?.user_id || 'unknown'  // For logging only
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      const orderData = orderResponse.data;
      
      console.log('Razorpay order created:', {
        order_id: orderData.order_id,
        amount_inr: orderData.amount_inr,
        amount_paise: orderData.amount
      });

      // Razorpay checkout options
      const options = {
        key: orderData.key_id || process.env.REACT_APP_RAZORPAY_KEY_ID,
        amount: orderData.amount,  // Backend returns amount in PAISE
        currency: orderData.currency,
        name: 'MySckul - EdTech Platform',
        description: `${planName} Plan - ${billingCycle} subscription`,
        order_id: orderData.order_id,
        image: '/logo192.png',
        handler: async (response) => {
          try {
            setPaymentStatus('verifying');
            
            // Verify payment on backend
            const verifyResponse = await axios.post(
              `${backendUrl}/api/subscription/razorpay/verify-payment`,
              {
                razorpay_order_id: response.razorpay_order_id,
                razorpay_payment_id: response.razorpay_payment_id,
                razorpay_signature: response.razorpay_signature,
                user_id: userDetails?.user_id
              },
              {
                headers: {
                  'Authorization': `Bearer ${token}`,
                  'Content-Type': 'application/json'
                }
              }
            );

            setPaymentStatus('success');
            onSuccess?.(verifyResponse.data);
          } catch (error) {
            console.error('Payment verification failed:', error);
            setPaymentStatus('failed');
            onError?.(error.response?.data?.detail || 'Payment verification failed');
          }
        },
        prefill: {
          name: userDetails?.name || '',
          email: userDetails?.email || '',
          contact: userDetails?.phone || ''
        },
        theme: {
          color: '#3B82F6'
        },
        modal: {
          ondismiss: () => {
            setIsProcessing(false);
            setPaymentStatus('cancelled');
            onCancel?.();
          }
        },
        method: {
          upi: true,
          card: true,
          netbanking: true,
          wallet: true,
          emi: orderData.amount_inr > 1000 ? true : false  // Use INR amount for EMI check
        },
        notes: {
          plan_name: planName,
          billing_cycle: billingCycle,
          user_id: userDetails?.user_id
        }
      };

      const razorpayInstance = new window.Razorpay(options);
      razorpayInstance.open();

    } catch (error) {
      console.error('Order creation failed:', error);
      setIsProcessing(false);
      setPaymentStatus('failed');
      
      // Enhanced error message
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to create payment order';
      onError?.(errorMessage);
      
      // Log full error for debugging
      console.error('Full error:', {
        status: error.response?.status,
        data: error.response?.data,
        message: error.message
      });
    }
  };

  const getStatusIcon = () => {
    switch (paymentStatus) {
      case 'success':
        return <CheckCircle className="h-8 w-8 text-green-500" />;
      case 'failed':
      case 'cancelled':
        return <AlertCircle className="h-8 w-8 text-red-500" />;
      default:
        return <CreditCard className="h-8 w-8 text-blue-500" />;
    }
  };

  const getStatusMessage = () => {
    switch (paymentStatus) {
      case 'verifying':
        return 'Verifying payment...';
      case 'success':
        return 'Payment successful! Your subscription has been activated.';
      case 'failed':
        return 'Payment verification failed. Please try again.';
      case 'cancelled':
        return 'Payment was cancelled.';
      default:
        return 'Ready to process payment';
    }
  };

  if (paymentStatus && paymentStatus !== 'verifying') {
    return (
      <Card className="w-full max-w-md mx-auto">
        <CardContent className="p-6 text-center">
          <div className="mb-4 flex justify-center">
            {getStatusIcon()}
          </div>
          <h3 className="text-lg font-semibold mb-2">
            {paymentStatus === 'success' ? 'Payment Successful!' : 'Payment Status'}
          </h3>
          <p className="text-gray-600 mb-4">{getStatusMessage()}</p>
          {paymentStatus === 'success' && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
              <p className="text-green-800 font-medium">
                Welcome to {planName} Plan!
              </p>
              <p className="text-green-600 text-sm">
                Your subscription is now active and all features are unlocked.
              </p>
            </div>
          )}
          {(paymentStatus === 'failed' || paymentStatus === 'cancelled') && (
            <Button 
              onClick={() => {
                setPaymentStatus(null);
                setIsProcessing(false);
              }}
              className="w-full"
            >
              Try Again
            </Button>
          )}
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <CreditCard className="h-6 w-6 text-blue-600" />
          <span>Complete Payment</span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Payment Summary */}
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex justify-between items-center mb-2">
            <span className="font-medium">{planName} Plan</span>
            <span className="font-bold">₹{amount}</span>
          </div>
          <div className="flex justify-between items-center text-sm text-gray-600 mb-2">
            <span>Billing Cycle</span>
            <span className="capitalize">{billingCycle}</span>
          </div>
          <div className="flex justify-between items-center text-sm text-gray-600 mb-2">
            <span>Base Amount</span>
            <span>₹{Math.round(amount / 1.18)}</span>
          </div>
          <div className="flex justify-between items-center text-sm text-gray-600 mb-2">
            <span>GST (18%)</span>
            <span>₹{Math.round(amount - (amount / 1.18))}</span>
          </div>
          <hr className="my-2" />
          <div className="flex justify-between items-center font-bold">
            <span>Total Amount</span>
            <span>₹{amount}</span>
          </div>
        </div>

        {/* Payment Methods Info */}
        <div className="space-y-3">
          <h4 className="font-medium text-gray-900">Accepted Payment Methods:</h4>
          <div className="grid grid-cols-3 gap-3">
            <div className="flex flex-col items-center p-3 bg-blue-50 rounded-lg">
              <Smartphone className="h-6 w-6 text-blue-600 mb-1" />
              <span className="text-xs text-blue-700">UPI</span>
            </div>
            <div className="flex flex-col items-center p-3 bg-green-50 rounded-lg">
              <CreditCard className="h-6 w-6 text-green-600 mb-1" />
              <span className="text-xs text-green-700">Cards</span>
            </div>
            <div className="flex flex-col items-center p-3 bg-purple-50 rounded-lg">
              <Building className="h-6 w-6 text-purple-600 mb-1" />
              <span className="text-xs text-purple-700">Net Banking</span>
            </div>
          </div>
        </div>

        {/* Pay Now Button */}
        <Button
          onClick={handlePayment}
          disabled={isProcessing || paymentStatus === 'verifying'}
          className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold"
        >
          {(isProcessing || paymentStatus === 'verifying') ? (
            <div className="flex items-center space-x-2">
              <LoadingSpinner size="sm" />
              <span>{paymentStatus === 'verifying' ? 'Verifying...' : 'Processing...'}</span>
            </div>
          ) : (
            `Pay ₹${amount} Now`
          )}
        </Button>

        {/* Security Note */}
        <div className="text-center">
          <p className="text-xs text-gray-500">
            🔒 Secured by Razorpay • Your payment information is encrypted and secure
          </p>
        </div>
      </CardContent>
    </Card>
  );
};

export default RazorpayPayment;