import React from 'react';
import { Link } from 'react-router-dom';
import { Package, Monitor, Cloud, Zap, Mail, Phone } from 'lucide-react';

export default function ShippingPolicy() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-white to-blue-50 dark:from-gray-900 dark:to-gray-800">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-4xl mx-auto px-4 py-6">
          <Link to="/" className="inline-flex items-center text-blue-600 dark:text-blue-400 hover:text-blue-700 mb-4">
            ← Back to Home
          </Link>
          <div className="flex items-center gap-3">
            <Package className="w-10 h-10 text-blue-600 dark:text-blue-400" />
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Shipping & Delivery Policy</h1>
              <p className="text-gray-600 dark:text-gray-400">Digital Services - Instant Access</p>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 prose prose-blue dark:prose-invert max-w-none">
          
          {/* Important Notice */}
          <div className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 p-6 rounded-lg border-2 border-blue-200 dark:border-blue-700 mb-8">
            <div className="flex items-start gap-4">
              <Monitor className="w-12 h-12 text-blue-600 dark:text-blue-400 flex-shrink-0" />
              <div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-3 mt-0">100% Digital Platform - No Physical Shipping</h2>
                <p className="text-gray-700 dark:text-gray-300 mb-0">
                  <strong>MySckul is a fully digital educational platform.</strong> We provide AI-powered tutoring, 
                  mock tests, and study materials through our online platform. We do not ship any physical products, 
                  books, materials, or hardware.
                </p>
              </div>
            </div>
          </div>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">1. Nature of Services</h2>
            <p className="text-gray-700 dark:text-gray-300 mb-4">
              All MySckul services are delivered digitally via the internet:
            </p>

            <div className="grid md:grid-cols-2 gap-4 mb-6">
              <div className="bg-white dark:bg-gray-700 p-4 rounded-lg border border-gray-200 dark:border-gray-600">
                <div className="flex items-center gap-3 mb-2">
                  <Cloud className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                  <h3 className="font-semibold text-gray-900 dark:text-white">Cloud-Based Access</h3>
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Access from any device with internet connection
                </p>
              </div>

              <div className="bg-white dark:bg-gray-700 p-4 rounded-lg border border-gray-200 dark:border-gray-600">
                <div className="flex items-center gap-3 mb-2">
                  <Zap className="w-6 h-6 text-purple-600 dark:text-purple-400" />
                  <h3 className="font-semibold text-gray-900 dark:text-white">Instant Delivery</h3>
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Immediate access upon successful subscription
                </p>
              </div>
            </div>

            <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg border border-blue-200 dark:border-blue-800">
              <h4 className="font-semibold text-gray-900 dark:text-white mb-2">Our Digital Services Include:</h4>
              <ul className="list-disc pl-6 text-gray-700 dark:text-gray-300 space-y-1 mb-0">
                <li>AI-powered personalized tutoring (accessible 24/7)</li>
                <li>Mock tests and practice questions (online only)</li>
                <li>Auto-generated study notes and materials (digital format)</li>
                <li>Performance analytics and progress tracking (web dashboard)</li>
                <li>Doubt solving and mentor tips (AI-generated, online)</li>
              </ul>
            </div>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">2. How Digital Delivery Works</h2>
            
            <div className="space-y-4">
              <div className="flex gap-4">
                <div className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
                  1
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-1">Subscribe</h3>
                  <p className="text-gray-700 dark:text-gray-300">
                    Choose a subscription plan and complete payment via Razorpay
                  </p>
                </div>
              </div>

              <div className="flex gap-4">
                <div className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
                  2
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-1">Instant Activation</h3>
                  <p className="text-gray-700 dark:text-gray-300">
                    Your account is upgraded immediately upon successful payment
                  </p>
                </div>
              </div>

              <div className="flex gap-4">
                <div className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
                  3
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-1">Start Learning</h3>
                  <p className="text-gray-700 dark:text-gray-300">
                    Access all features immediately - no waiting, no shipping delays
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg border border-green-200 dark:border-green-800 mt-6">
              <p className="text-gray-700 dark:text-gray-300 mb-0">
                <strong>Delivery Time:</strong> Immediate (within seconds of successful payment confirmation)
              </p>
            </div>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">3. Access Requirements</h2>
            <p className="text-gray-700 dark:text-gray-300 mb-3">To access our digital services, you need:</p>
            <ul className="list-disc pl-6 text-gray-700 dark:text-gray-300 space-y-2">
              <li><strong>Internet Connection:</strong> Stable broadband or mobile data (minimum 2 Mbps recommended)</li>
              <li><strong>Compatible Device:</strong> Computer, laptop, tablet, or smartphone</li>
              <li><strong>Modern Web Browser:</strong> Chrome, Firefox, Safari, or Edge (latest versions)</li>
              <li><strong>Active Account:</strong> Registered MySckul account with valid subscription</li>
              <li><strong>Email Access:</strong> For account notifications and support</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">4. Geographic Availability</h2>
            <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg border border-purple-200 dark:border-purple-800">
              <p className="text-gray-700 dark:text-gray-300 mb-3">
                <strong>Global Access:</strong> Since our services are 100% digital, they are accessible from anywhere 
                in the world with internet connectivity. No geographic restrictions apply.
              </p>
              <ul className="list-disc pl-6 text-gray-700 dark:text-gray-300 space-y-2 mb-0">
                <li>Available 24/7 from any location</li>
                <li>No customs, import duties, or shipping fees</li>
                <li>No delivery delays or lost shipments</li>
                <li>Access from multiple devices simultaneously (based on plan)</li>
              </ul>
            </div>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">5. Service Accessibility</h2>
            <div className="space-y-4">
              <div className="bg-white dark:bg-gray-700 p-4 rounded-lg border border-gray-200 dark:border-gray-600">
                <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Web Platform</h3>
                <p className="text-gray-700 dark:text-gray-300 mb-0">
                  Access via <span className="font-mono text-blue-600 dark:text-blue-400">{window.location.origin}</span> from any web browser
                </p>
              </div>

              <div className="bg-white dark:bg-gray-700 p-4 rounded-lg border border-gray-200 dark:border-gray-600">
                <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Mobile Responsive</h3>
                <p className="text-gray-700 dark:text-gray-300 mb-0">
                  Fully optimized for mobile devices - study on the go
                </p>
              </div>

              <div className="bg-white dark:bg-gray-700 p-4 rounded-lg border border-gray-200 dark:border-gray-600">
                <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Cloud Storage</h3>
                <p className="text-gray-700 dark:text-gray-300 mb-0">
                  All your data, progress, and materials stored securely in the cloud
                </p>
              </div>
            </div>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">6. No Physical Products</h2>
            <div className="bg-yellow-50 dark:bg-yellow-900/20 p-4 rounded-lg border border-yellow-200 dark:border-yellow-800">
              <p className="text-gray-700 dark:text-gray-300 mb-3">
                <strong>Important Clarification:</strong> MySckul does NOT provide:
              </p>
              <ul className="list-disc pl-6 text-gray-700 dark:text-gray-300 space-y-2 mb-0">
                <li>Physical books, study guides, or printed materials</li>
                <li>Hardware devices (tablets, computers, etc.)</li>
                <li>Physical shipments of any kind</li>
                <li>Couriered documents or certificates</li>
                <li>Tangible goods requiring shipping</li>
              </ul>
              <p className="text-gray-700 dark:text-gray-300 mt-3 mb-0">
                All certificates and study materials are available in digital format only for download or online viewing.
              </p>
            </div>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">7. Troubleshooting Access Issues</h2>
            <p className="text-gray-700 dark:text-gray-300 mb-3">
              If you experience any issues accessing your digital services:
            </p>
            <ol className="list-decimal pl-6 text-gray-700 dark:text-gray-300 space-y-2">
              <li>Check your internet connection stability</li>
              <li>Clear browser cache and cookies</li>
              <li>Try a different browser or device</li>
              <li>Verify your subscription is active in account settings</li>
              <li>Contact our support team for immediate assistance</li>
            </ol>
            <div className="bg-blue-50 dark:bg-blue-900/20 p-3 rounded mt-3">
              <p className="text-sm text-gray-700 dark:text-gray-300 mb-0">
                <strong>Technical Support:</strong> Available 24/7 via email and phone for any access issues
              </p>
            </div>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">8. Contact Support</h2>
            <div className="bg-blue-50 dark:bg-blue-900/20 p-6 rounded-lg">
              <p className="text-gray-700 dark:text-gray-300 mb-4">
                For questions about service access or delivery:
              </p>
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <Mail className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                  <span className="text-gray-700 dark:text-gray-300">
                    Email: <a href="mailto:support@druvai.in" className="text-blue-600 dark:text-blue-400 hover:underline">support@druvai.in</a>
                  </span>
                </div>
                <div className="flex items-center gap-3">
                  <Phone className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                  <span className="text-gray-700 dark:text-gray-300">Phone: +91-8660838896</span>
                </div>
              </div>
              <div className="mt-4 p-3 bg-white dark:bg-gray-700 rounded border border-blue-200 dark:border-blue-700">
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-0">
                  <strong>Average Response Time:</strong> Within 2 hours during business hours<br />
                  <strong>Service Uptime:</strong> 99.9% guaranteed availability
                </p>
              </div>
            </div>
          </section>

        </div>
      </div>
    </div>
  );
}
