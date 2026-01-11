import React from 'react';
import { Link } from 'react-router-dom';
import { Shield, Mail, Phone, MapPin } from 'lucide-react';

export default function PrivacyPolicy() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-white to-blue-50 dark:from-gray-900 dark:to-gray-800">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-4xl mx-auto px-4 py-6">
          <Link to="/" className="inline-flex items-center text-blue-600 dark:text-blue-400 hover:text-blue-700 mb-4">
            ← Back to Home
          </Link>
          <div className="flex items-center gap-3">
            <Shield className="w-10 h-10 text-blue-600 dark:text-blue-400" />
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Privacy Policy</h1>
              <p className="text-gray-600 dark:text-gray-400">Last updated: January 16, 2025</p>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 prose prose-blue dark:prose-invert max-w-none">
          
          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">1. Introduction</h2>
            <p className="text-gray-700 dark:text-gray-300">
              Welcome to MySckul AI ("we," "our," or "us"). We are committed to protecting your personal information and your right to privacy. 
              This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our AI-powered 
              educational platform and services.
            </p>
            <p className="text-gray-700 dark:text-gray-300">
              By using MySckul, you agree to the collection and use of information 
              in accordance with this policy.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">2. Information We Collect</h2>
            
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">2.1 Personal Information</h3>
            <p className="text-gray-700 dark:text-gray-300 mb-3">We collect the following personal information:</p>
            <ul className="list-disc pl-6 text-gray-700 dark:text-gray-300 space-y-2">
              <li><strong>Account Information:</strong> Name, email address, phone number, exam type, study goals</li>
              <li><strong>Profile Data:</strong> Educational background, preferred study mode, timezone, country</li>
              <li><strong>Google OAuth Data:</strong> When you sign up using Google, we receive your name, email, and profile picture</li>
              <li><strong>Payment Information:</strong> Processed securely through Razorpay (we do not store credit card details)</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3 mt-6">2.2 Usage Information</h3>
            <ul className="list-disc pl-6 text-gray-700 dark:text-gray-300 space-y-2">
              <li>AI Tutor chat history and interactions</li>
              <li>Mock test results and performance analytics</li>
              <li>Study session duration and frequency</li>
              <li>Feature usage patterns and preferences</li>
              <li>Device information (browser type, operating system, IP address)</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3 mt-6">2.3 Automatically Collected Information</h3>
            <ul className="list-disc pl-6 text-gray-700 dark:text-gray-300 space-y-2">
              <li>Cookies and similar tracking technologies</li>
              <li>Log data (access times, pages viewed, errors)</li>
              <li>Session information and authentication tokens</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">3. How We Use Your Information</h2>
            <p className="text-gray-700 dark:text-gray-300 mb-3">We use your information for:</p>
            <ul className="list-disc pl-6 text-gray-700 dark:text-gray-300 space-y-2">
              <li><strong>Service Delivery:</strong> Providing personalized AI tutoring, mock tests, and study materials</li>
              <li><strong>Account Management:</strong> Creating and maintaining your account, authentication, subscription management</li>
              <li><strong>Personalization:</strong> Customizing content based on your exam type, study goals, and performance</li>
              <li><strong>Analytics:</strong> Improving our AI algorithms and platform features</li>
              <li><strong>Communication:</strong> Sending important updates, notifications, and promotional materials (with your consent)</li>
              <li><strong>Payment Processing:</strong> Managing subscriptions and payments through Razorpay</li>
              <li><strong>Security:</strong> Detecting and preventing fraud, abuse, and security threats</li>
              <li><strong>Legal Compliance:</strong> Complying with legal obligations and enforcing our terms</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">4. How We Share Your Information</h2>
            <p className="text-gray-700 dark:text-gray-300 mb-3">We may share your information with:</p>
            <ul className="list-disc pl-6 text-gray-700 dark:text-gray-300 space-y-2">
              <li><strong>Service Providers:</strong> Razorpay (payment processing), Google Cloud (infrastructure), OpenAI (AI services)</li>
              <li><strong>Legal Requirements:</strong> When required by law, court order, or government request</li>
              <li><strong>Business Transfers:</strong> In case of merger, acquisition, or sale of assets</li>
              <li><strong>With Your Consent:</strong> When you explicitly authorize us to share specific information</li>
            </ul>
            <p className="text-gray-700 dark:text-gray-300 mt-3">
              <strong>We do NOT sell your personal information to third parties.</strong>
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">5. Data Security</h2>
            <p className="text-gray-700 dark:text-gray-300 mb-3">We implement industry-standard security measures:</p>
            <ul className="list-disc pl-6 text-gray-700 dark:text-gray-300 space-y-2">
              <li>HTTPS/SSL encryption for all data transmission</li>
              <li>Secure OAuth 2.0 authentication with Google</li>
              <li>Encrypted storage of sensitive data</li>
              <li>Regular security audits and updates</li>
              <li>Access controls and authentication for all systems</li>
              <li>Secure payment processing through PCI-DSS compliant Razorpay</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">6. Your Privacy Rights</h2>
            <p className="text-gray-700 dark:text-gray-300 mb-3">You have the right to:</p>
            <ul className="list-disc pl-6 text-gray-700 dark:text-gray-300 space-y-2">
              <li><strong>Access:</strong> Request a copy of your personal data</li>
              <li><strong>Correction:</strong> Update or correct inaccurate information</li>
              <li><strong>Deletion:</strong> Request deletion of your account and data (subject to legal retention requirements)</li>
              <li><strong>Portability:</strong> Export your data in a machine-readable format</li>
              <li><strong>Opt-out:</strong> Unsubscribe from marketing communications</li>
              <li><strong>Restriction:</strong> Request limitation of data processing</li>
            </ul>
            <p className="text-gray-700 dark:text-gray-300 mt-3">
              To exercise these rights, contact us at <a href="mailto:support@druvai.in" className="text-blue-600 dark:text-blue-400 hover:underline">support@druvai.in</a>
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">7. Data Retention</h2>
            <p className="text-gray-700 dark:text-gray-300">
              We retain your information for as long as your account is active or as needed to provide services. 
              After account deletion, we may retain certain information for legal compliance, dispute resolution, 
              and legitimate business purposes for up to 7 years.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">8. Cookies and Tracking</h2>
            <p className="text-gray-700 dark:text-gray-300 mb-3">We use cookies and similar technologies for:</p>
            <ul className="list-disc pl-6 text-gray-700 dark:text-gray-300 space-y-2">
              <li><strong>Essential Cookies:</strong> Required for login, session management, and security</li>
              <li><strong>Functional Cookies:</strong> Remember your preferences and settings</li>
              <li><strong>Analytics Cookies:</strong> Understand how you use our platform</li>
              <li><strong>Performance Cookies:</strong> Optimize platform performance</li>
            </ul>
            <p className="text-gray-700 dark:text-gray-300 mt-3">
              You can control cookies through your browser settings, but disabling certain cookies may affect functionality.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">9. Children's Privacy</h2>
            <p className="text-gray-700 dark:text-gray-300">
              MySckul is designed for students aged 13 and above. We do not knowingly collect information from children under 13. 
              If you believe we have inadvertently collected such information, please contact us immediately for deletion.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">10. International Data Transfers</h2>
            <p className="text-gray-700 dark:text-gray-300">
              Your information may be transferred to and processed in countries other than your country of residence. 
              We ensure appropriate safeguards are in place for such transfers in compliance with applicable data protection laws.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">11. Updates to This Policy</h2>
            <p className="text-gray-700 dark:text-gray-300">
              We may update this Privacy Policy periodically. We will notify you of significant changes via email or 
              prominent notice on our platform. Continued use after changes constitutes acceptance of the updated policy.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">12. Contact Us</h2>
            <div className="bg-blue-50 dark:bg-blue-900/20 p-6 rounded-lg">
              <p className="text-gray-700 dark:text-gray-300 mb-4">
                If you have questions about this Privacy Policy or our data practices:
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
                <div className="flex items-center gap-3">
                  <MapPin className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                  <span className="text-gray-700 dark:text-gray-300">
                    MySckul AI<br />
                    Near Laksmi Hospital<br />
                    Kaggadasapur, Bangalore - 560093<br />
                    Karnataka, India
                  </span>
                </div>
              </div>
            </div>
          </section>

        </div>
      </div>
    </div>
  );
}
