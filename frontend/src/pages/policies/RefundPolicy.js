import React from 'react';
import { Link } from 'react-router-dom';
import { RotateCcw, Mail, Phone, MapPin, Clock, CreditCard } from 'lucide-react';

export default function RefundPolicy() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-white to-blue-50 dark:from-gray-900 dark:to-gray-800">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-4xl mx-auto px-4 py-6">
          <Link to="/" className="inline-flex items-center text-blue-600 dark:text-blue-400 hover:text-blue-700 mb-4">
            ← Back to Home
          </Link>
          <div className="flex items-center gap-3">
            <RotateCcw className="w-10 h-10 text-blue-600 dark:text-blue-400" />
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Cancellation & Refund Policy</h1>
              <p className="text-gray-600 dark:text-gray-400">Last updated: January 16, 2025</p>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 prose prose-blue dark:prose-invert max-w-none">
          
          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">1. Overview</h2>
            <p className="text-gray-700 dark:text-gray-300">
              At Dhruv AI, we are committed to providing high-quality AI-powered educational services. This Cancellation & Refund Policy 
              explains our policies regarding subscription cancellations and refund eligibility for our digital services.
            </p>
            <div className="bg-yellow-50 dark:bg-yellow-900/20 p-4 rounded-lg mt-4 border border-yellow-200 dark:border-yellow-800">
              <p className="text-gray-700 dark:text-gray-300 font-semibold">
                <strong>Important:</strong> As we provide digital educational services (AI tutoring, mock tests, study materials), 
                all sales are final once services are accessed. However, we offer specific refund windows and exceptions as detailed below.
              </p>
            </div>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">2. Cancellation Policy</h2>
            
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">2.1 How to Cancel</h3>
            <p className="text-gray-700 dark:text-gray-300 mb-3">You can cancel your subscription anytime through:</p>
            <ul className="list-disc pl-6 text-gray-700 dark:text-gray-300 space-y-2">
              <li>Your account settings → Subscription → Cancel Subscription</li>
              <li>Contacting our support team at <a href="mailto:support@dhruvai.com" className="text-blue-600 dark:text-blue-400 hover:underline">support@dhruvai.com</a></li>
              <li>Calling us at +91-XXXX-XXXXXX</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3 mt-6">2.2 Effective Date of Cancellation</h3>
            <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg border border-blue-200 dark:border-blue-800">
              <div className="flex items-start gap-3">
                <Clock className="w-6 h-6 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-1" />
                <div>
                  <p className="text-gray-700 dark:text-gray-300 mb-2">
                    <strong>Immediate Effect:</strong> When you cancel, you will continue to have access to your subscription 
                    until the end of your current billing period. No new charges will be applied.
                  </p>
                  <p className="text-gray-700 dark:text-gray-300">
                    <strong>Example:</strong> If you cancel on January 15th and your subscription renews on January 30th, 
                    you can continue using all features until January 30th.
                  </p>
                </div>
              </div>
            </div>

            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3 mt-6">2.3 Auto-Renewal Cancellation</h3>
            <p className="text-gray-700 dark:text-gray-300">
              All subscriptions are set to auto-renew. To avoid being charged for the next billing cycle, 
              you must cancel at least 24 hours before your renewal date.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">3. Refund Policy</h2>
            
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">3.1 7-Day Money-Back Guarantee (New Subscribers)</h3>
            <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg border border-green-200 dark:border-green-800 mb-4">
              <p className="text-gray-700 dark:text-gray-300 mb-3">
                <strong>First-time subscribers are eligible for a full refund within 7 days of initial purchase</strong> if:
              </p>
              <ul className="list-disc pl-6 text-gray-700 dark:text-gray-300 space-y-2">
                <li>You are a new subscriber (first-time purchase of any paid plan)</li>
                <li>You request the refund within 7 days of your initial payment</li>
                <li>You have used less than 20% of your subscription features</li>
                <li>You provide a valid reason for dissatisfaction</li>
              </ul>
            </div>

            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3 mt-6">3.2 Pro-Rata Refunds (Service Issues)</h3>
            <p className="text-gray-700 dark:text-gray-300 mb-3">
              We offer pro-rata refunds in the following exceptional circumstances:
            </p>
            <ul className="list-disc pl-6 text-gray-700 dark:text-gray-300 space-y-2">
              <li><strong>Extended Service Outages:</strong> If our platform is unavailable for more than 48 consecutive hours</li>
              <li><strong>Billing Errors:</strong> If you were incorrectly charged or double-charged</li>
              <li><strong>Unauthorized Charges:</strong> If your account was compromised and unauthorized charges occurred</li>
              <li><strong>Critical Feature Failures:</strong> If a core feature you subscribed for is non-functional for more than 7 days</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3 mt-6">3.3 Non-Refundable Situations</h3>
            <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg border border-red-200 dark:border-red-800">
              <p className="text-gray-700 dark:text-gray-300 mb-3">
                <strong>Refunds are NOT available in the following cases:</strong>
              </p>
              <ul className="list-disc pl-6 text-gray-700 dark:text-gray-300 space-y-2">
                <li>After 7 days of initial purchase (for regular refund requests)</li>
                <li>For renewal subscriptions (second month onwards)</li>
                <li>If you've used more than 20% of subscription features (AI sessions, mock tests, etc.)</li>
                <li>Change of mind after actively using the service</li>
                <li>Account suspension or termination due to Terms of Service violations</li>
                <li>Failure to cancel before auto-renewal (you'll retain access until period end)</li>
                <li>Partial month refunds (except in service issue cases)</li>
              </ul>
            </div>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">4. Refund Process</h2>
            
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">4.1 How to Request a Refund</h3>
            <p className="text-gray-700 dark:text-gray-300 mb-3">To request a refund:</p>
            <ol className="list-decimal pl-6 text-gray-700 dark:text-gray-300 space-y-2">
              <li>Email us at <a href="mailto:refunds@dhruvai.com" className="text-blue-600 dark:text-blue-400 hover:underline">refunds@dhruvai.com</a></li>
              <li>Include your account email, order ID, and reason for refund</li>
              <li>Our team will review within 2-3 business days</li>
              <li>If approved, refund will be processed within 5-7 business days</li>
            </ol>

            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3 mt-6">4.2 Refund Timeline</h3>
            <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
              <div className="flex items-start gap-3">
                <CreditCard className="w-6 h-6 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-1" />
                <div className="space-y-2">
                  <p className="text-gray-700 dark:text-gray-300">
                    <strong>Processing Time:</strong> 2-3 business days for review
                  </p>
                  <p className="text-gray-700 dark:text-gray-300">
                    <strong>Refund to Bank Account:</strong> 5-7 business days after approval
                  </p>
                  <p className="text-gray-700 dark:text-gray-300">
                    <strong>Refund to UPI/Wallet:</strong> 3-5 business days after approval
                  </p>
                  <p className="text-gray-700 dark:text-gray-300">
                    <strong>Refund to Credit Card:</strong> 7-10 business days after approval
                  </p>
                </div>
              </div>
            </div>

            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3 mt-6">4.3 Refund Method</h3>
            <p className="text-gray-700 dark:text-gray-300">
              Refunds will be processed to the original payment method used for the purchase through Razorpay. 
              We cannot process refunds to a different account or payment method.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">5. Subscription Downgrades</h2>
            <p className="text-gray-700 dark:text-gray-300 mb-3">
              Instead of canceling, you can downgrade to a lower-tier plan:
            </p>
            <ul className="list-disc pl-6 text-gray-700 dark:text-gray-300 space-y-2">
              <li>Downgrade takes effect at the end of current billing period</li>
              <li>No refunds for the difference between plans</li>
              <li>You retain access to current plan features until downgrade date</li>
              <li>Can be done through account settings or by contacting support</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">6. Free Trial</h2>
            <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg border border-purple-200 dark:border-purple-800">
              <p className="text-gray-700 dark:text-gray-300 mb-3">
                <strong>7-Day Free Trial (Select Plans):</strong>
              </p>
              <ul className="list-disc pl-6 text-gray-700 dark:text-gray-300 space-y-2">
                <li>Available for first-time users on select plans</li>
                <li>Cancel anytime during trial - no charges applied</li>
                <li>After trial, subscription auto-converts to paid unless canceled</li>
                <li>No refunds for subscriptions that started as free trials</li>
              </ul>
            </div>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">7. Exceptional Circumstances</h2>
            <p className="text-gray-700 dark:text-gray-300 mb-3">
              We understand that exceptional situations may arise. We may consider refunds on a case-by-case basis for:
            </p>
            <ul className="list-disc pl-6 text-gray-700 dark:text-gray-300 space-y-2">
              <li>Medical emergencies (with documentation)</li>
              <li>Bereavement or family emergencies</li>
              <li>Technical issues preventing service access (after troubleshooting attempts)</li>
              <li>Duplicate or accidental purchases</li>
            </ul>
            <p className="text-gray-700 dark:text-gray-300 mt-3">
              Please contact our support team with relevant documentation for consideration.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">8. Payment Disputes</h2>
            <p className="text-gray-700 dark:text-gray-300">
              If you dispute a charge with your bank or payment provider (chargeback), your account may be suspended 
              until the dispute is resolved. We encourage you to contact us directly before initiating a chargeback 
              so we can work together to resolve any issues.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">9. Account Reactivation</h2>
            <p className="text-gray-700 dark:text-gray-300">
              If you cancel your subscription and later wish to reactivate:
            </p>
            <ul className="list-disc pl-6 text-gray-700 dark:text-gray-300 space-y-2">
              <li>Your data is retained for 90 days after cancellation</li>
              <li>You can resubscribe at any time and regain access</li>
              <li>Previous subscription benefits do not carry over to new subscription</li>
              <li>Any promotional pricing may no longer be available</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">10. Contact Us for Cancellation or Refund</h2>
            <div className="bg-blue-50 dark:bg-blue-900/20 p-6 rounded-lg">
              <p className="text-gray-700 dark:text-gray-300 mb-4">
                For cancellation, refund requests, or billing questions:
              </p>
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <Mail className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                  <span className="text-gray-700 dark:text-gray-300">
                    Refunds: <a href="mailto:refunds@dhruvai.com" className="text-blue-600 dark:text-blue-400 hover:underline">refunds@dhruvai.com</a>
                  </span>
                </div>
                <div className="flex items-center gap-3">
                  <Mail className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                  <span className="text-gray-700 dark:text-gray-300">
                    Support: <a href="mailto:support@dhruvai.com" className="text-blue-600 dark:text-blue-400 hover:underline">support@dhruvai.com</a>
                  </span>
                </div>
                <div className="flex items-center gap-3">
                  <Phone className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                  <span className="text-gray-700 dark:text-gray-300">Phone: +91-XXXX-XXXXXX</span>
                </div>
                <div className="flex items-center gap-3">
                  <MapPin className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                  <span className="text-gray-700 dark:text-gray-300">
                    Dhruv AI<br />
                    [Business Address]<br />
                    India
                  </span>
                </div>
              </div>
              <div className="mt-4 p-3 bg-white dark:bg-gray-700 rounded border border-blue-200 dark:border-blue-700">
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  <strong>Business Hours:</strong> Monday - Friday, 9:00 AM - 6:00 PM IST<br />
                  <strong>Response Time:</strong> Within 24 hours on business days
                </p>
              </div>
            </div>
          </section>

        </div>
      </div>
    </div>
  );
}
