import React from 'react';
import { Link } from 'react-router-dom';
import { FileText, Mail, Phone, MapPin } from 'lucide-react';

export default function TermsAndConditions() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-white to-blue-50 dark:from-gray-900 dark:to-gray-800">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-4xl mx-auto px-4 py-6">
          <Link to="/" className="inline-flex items-center text-blue-600 dark:text-blue-400 hover:text-blue-700 mb-4">
            ← Back to Home
          </Link>
          <div className="flex items-center gap-3">
            <FileText className="w-10 h-10 text-blue-600 dark:text-blue-400" />
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Terms and Conditions</h1>
              <p className="text-gray-600 dark:text-gray-400">Last updated: January 16, 2025</p>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 prose prose-blue dark:prose-invert max-w-none">
          
          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">1. Acceptance of Terms</h2>
            <p className="text-gray-700 dark:text-gray-300">
              Welcome to Dhruv AI. By accessing or using our AI-powered educational platform 
              ("Platform"), you agree to be bound by these Terms and Conditions ("Terms"). If you do not agree to these Terms, 
              please do not use our services.
            </p>
            <p className="text-gray-700 dark:text-gray-300">
              These Terms constitute a legally binding agreement between you and Dhruv AI ("we," "us," or "our").
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">2. Services Provided</h2>
            <p className="text-gray-700 dark:text-gray-300 mb-3">Dhruv AI offers the following digital educational services:</p>
            <ul className="list-disc pl-6 text-gray-700 dark:text-gray-300 space-y-2">
              <li><strong>AI Tutor:</strong> Personalized AI-powered tutoring for various subjects and exam preparations (JEE, NEET, UPSC, etc.)</li>
              <li><strong>Mock Tests:</strong> Practice tests with AI-generated questions and performance analytics</li>
              <li><strong>Auto-Note Mentor:</strong> AI-assisted note-taking and study material generation</li>
              <li><strong>Study Analytics:</strong> Performance tracking and personalized recommendations</li>
              <li><strong>Subscription Plans:</strong> Free, Starter, Scholar, and Genius tiers with varying features</li>
            </ul>
            <p className="text-gray-700 dark:text-gray-300 mt-3">
              <strong>Important:</strong> All our services are digital and delivered online. We do not provide physical products or materials.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">3. User Registration and Account</h2>
            
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">3.1 Eligibility</h3>
            <p className="text-gray-700 dark:text-gray-300">
              You must be at least 13 years old to use Dhruv AI. If you are under 18, you must have parental consent to use our services.
            </p>

            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3 mt-6">3.2 Account Security</h3>
            <ul className="list-disc pl-6 text-gray-700 dark:text-gray-300 space-y-2">
              <li>You are responsible for maintaining the confidentiality of your account credentials</li>
              <li>We use Google OAuth for secure authentication</li>
              <li>You must notify us immediately of any unauthorized access</li>
              <li>You are responsible for all activities under your account</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3 mt-6">3.3 Account Termination</h3>
            <p className="text-gray-700 dark:text-gray-300">
              We reserve the right to suspend or terminate your account for violations of these Terms, fraudulent activity, 
              or abuse of our services.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">4. Subscription and Payments</h2>
            
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">4.1 Subscription Plans</h3>
            <ul className="list-disc pl-6 text-gray-700 dark:text-gray-300 space-y-2">
              <li><strong>Free:</strong> Limited AI sessions, basic mock tests</li>
              <li><strong>Starter:</strong> Increased limits, standard features</li>
              <li><strong>Scholar:</strong> Enhanced features, priority support</li>
              <li><strong>Genius:</strong> Unlimited access, premium features</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3 mt-6">4.2 Payment Terms</h3>
            <ul className="list-disc pl-6 text-gray-700 dark:text-gray-300 space-y-2">
              <li>All payments are processed securely through Razorpay</li>
              <li>Subscription fees are billed monthly or annually based on your chosen plan</li>
              <li>Prices are in Indian Rupees (INR) unless otherwise stated</li>
              <li>All fees are non-refundable except as required by law or stated in our Refund Policy</li>
              <li>We reserve the right to change pricing with 30 days' notice</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3 mt-6">4.3 Auto-Renewal</h3>
            <p className="text-gray-700 dark:text-gray-300">
              Subscriptions automatically renew unless you cancel before the renewal date. You can cancel anytime from your account settings.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">5. Intellectual Property Rights</h2>
            
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">5.1 Our Content</h3>
            <p className="text-gray-700 dark:text-gray-300">
              All content, features, and functionality on Dhruv AI (including AI algorithms, study materials, test questions, 
              software, text, graphics, logos, and trademarks) are owned by Dhruv AI and protected by intellectual property laws.
            </p>

            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3 mt-6">5.2 Your Content</h3>
            <p className="text-gray-700 dark:text-gray-300">
              You retain ownership of content you create (notes, test responses, chat history). By using our services, 
              you grant us a license to use this content to provide and improve our services.
            </p>

            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3 mt-6">5.3 Restrictions</h3>
            <ul className="list-disc pl-6 text-gray-700 dark:text-gray-300 space-y-2">
              <li>You may not copy, modify, or distribute our content without permission</li>
              <li>You may not reverse engineer or attempt to extract our AI algorithms</li>
              <li>You may not use our services to create competing products</li>
              <li>Commercial use requires explicit written permission</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">6. Acceptable Use Policy</h2>
            <p className="text-gray-700 dark:text-gray-300 mb-3">You agree NOT to:</p>
            <ul className="list-disc pl-6 text-gray-700 dark:text-gray-300 space-y-2">
              <li>Use the Platform for any illegal or unauthorized purpose</li>
              <li>Violate any laws in your jurisdiction</li>
              <li>Share your account with others or create multiple accounts</li>
              <li>Attempt to hack, disrupt, or overload our systems</li>
              <li>Upload malicious code, viruses, or harmful content</li>
              <li>Harass, abuse, or harm other users</li>
              <li>Scrape, data mine, or systematically extract our content</li>
              <li>Use automated tools (bots) without permission</li>
              <li>Impersonate others or provide false information</li>
              <li>Circumvent subscription limits or payment systems</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">7. AI-Generated Content Disclaimer</h2>
            <p className="text-gray-700 dark:text-gray-300">
              Our AI Tutor uses advanced language models to generate educational content. While we strive for accuracy:
            </p>
            <ul className="list-disc pl-6 text-gray-700 dark:text-gray-300 space-y-2">
              <li>AI responses may occasionally contain errors or inaccuracies</li>
              <li>Always verify critical information with authoritative sources</li>
              <li>AI is a study aid, not a replacement for qualified teachers</li>
              <li>We do not guarantee exam success or specific outcomes</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">8. Privacy and Data Protection</h2>
            <p className="text-gray-700 dark:text-gray-300">
              Your privacy is important to us. Our collection and use of personal information is governed by our 
              <Link to="/policies/privacy" className="text-blue-600 dark:text-blue-400 hover:underline"> Privacy Policy</Link>, 
              which is incorporated into these Terms by reference.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">9. Disclaimers and Limitations of Liability</h2>
            
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">9.1 Service "As Is"</h3>
            <p className="text-gray-700 dark:text-gray-300">
              Dhruv AI is provided "AS IS" and "AS AVAILABLE" without warranties of any kind, express or implied. 
              We do not guarantee uninterrupted, error-free, or secure service.
            </p>

            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3 mt-6">9.2 Limitation of Liability</h3>
            <p className="text-gray-700 dark:text-gray-300">
              To the maximum extent permitted by law, Dhruv AI shall not be liable for any indirect, incidental, 
              special, consequential, or punitive damages, including loss of profits, data, or opportunities, 
              arising from your use of our services.
            </p>
            <p className="text-gray-700 dark:text-gray-300 mt-3">
              Our total liability shall not exceed the amount you paid to us in the 12 months preceding the claim.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">10. Indemnification</h2>
            <p className="text-gray-700 dark:text-gray-300">
              You agree to indemnify and hold Dhruv AI harmless from any claims, damages, losses, or expenses 
              (including legal fees) arising from your use of our services, violation of these Terms, or 
              infringement of any third-party rights.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">11. Modification of Terms</h2>
            <p className="text-gray-700 dark:text-gray-300">
              We reserve the right to modify these Terms at any time. We will notify you of material changes via email 
              or prominent notice on the Platform. Continued use after changes constitutes acceptance of the modified Terms.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">12. Termination</h2>
            <p className="text-gray-700 dark:text-gray-300">
              Either party may terminate this agreement at any time. Upon termination, your right to use the Platform 
              ceases immediately. Provisions that by their nature should survive (including intellectual property, 
              disclaimers, and limitations of liability) will continue after termination.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">13. Governing Law and Dispute Resolution</h2>
            <p className="text-gray-700 dark:text-gray-300">
              These Terms are governed by the laws of India. Any disputes shall be resolved through arbitration in 
              accordance with the Arbitration and Conciliation Act, 1996, with proceedings conducted in English.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">14. Severability</h2>
            <p className="text-gray-700 dark:text-gray-300">
              If any provision of these Terms is found to be invalid or unenforceable, the remaining provisions 
              will continue in full force and effect.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">15. Contact Information</h2>
            <div className="bg-blue-50 dark:bg-blue-900/20 p-6 rounded-lg">
              <p className="text-gray-700 dark:text-gray-300 mb-4">
                For questions about these Terms and Conditions:
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
                    Druv AI<br />
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
