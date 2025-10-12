/**
 * HUMAN EVALUATION STUDY - INTRO PAGE
 * 
 * Welcome page for participants in the interpretability study
 * Explains the study purpose and provides instructions
 */

'use client';

export const dynamic = 'force-dynamic';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Brain, CheckCircle, Clock, Users, ArrowRight, Shield } from 'lucide-react';
import axios from 'axios';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export default function StudyIntroPage() {
  const router = useRouter();
  const [isStarting, setIsStarting] = useState(false);
  const [agreedToTerms, setAgreedToTerms] = useState(false);

  const handleStartStudy = async () => {
    if (!agreedToTerms) {
      alert('Please agree to the terms before starting the study');
      return;
    }

    setIsStarting(true);

    try {
      // Start a new study session
      const response = await axios.post(`${API_BASE}/humanstudy/session/start`, {
        num_questions: 10
      });

      const { session_id, randomization_seed } = response.data;

      // Navigate to study session with session data
      router.push(`/study/session?session_id=${session_id}&seed=${randomization_seed}`);
    } catch (error) {
      console.error('Failed to start study:', error);
      alert('Failed to start study. Please try again.');
      setIsStarting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900">
      {/* Header */}
      <div className="bg-black/30 backdrop-blur-sm border-b border-white/10">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg">
              <Brain className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">XAI Interpretability Study</h1>
              <p className="text-sm text-gray-300">Human Evaluation of Explanation Methods</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Welcome Card */}
        <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-8 mb-8">
          <h2 className="text-3xl font-bold text-white mb-4">
            Welcome to Our Research Study
          </h2>
          <p className="text-lg text-gray-200 mb-6">
            Help us understand how humans perceive AI explanations in fraud detection systems.
            Your feedback will contribute to making AI more interpretable and trustworthy.
          </p>

          {/* Study Info Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
            <div className="bg-blue-500/20 border border-blue-400/30 rounded-lg p-4">
              <Clock className="h-8 w-8 text-blue-300 mb-2" />
              <div className="text-sm font-medium text-blue-200">Duration</div>
              <div className="text-2xl font-bold text-white">~5 minutes</div>
            </div>

            <div className="bg-purple-500/20 border border-purple-400/30 rounded-lg p-4">
              <Users className="h-8 w-8 text-purple-300 mb-2" />
              <div className="text-sm font-medium text-purple-200">Questions</div>
              <div className="text-2xl font-bold text-white">10 cases</div>
            </div>

            <div className="bg-green-500/20 border border-green-400/30 rounded-lg p-4">
              <Shield className="h-8 w-8 text-green-300 mb-2" />
              <div className="text-sm font-medium text-green-200">Privacy</div>
              <div className="text-2xl font-bold text-white">Anonymous</div>
            </div>
          </div>
        </div>

        {/* Instructions */}
        <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-8 mb-8">
          <h3 className="text-2xl font-bold text-white mb-6">How It Works</h3>

          <div className="space-y-6">
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0 w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white font-bold">
                1
              </div>
              <div>
                <h4 className="text-lg font-semibold text-white mb-2">View a Decision</h4>
                <p className="text-gray-300">
                  You'll see a fraud detection decision (e.g., "Transaction flagged as fraud" or "Transaction approved").
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0 w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center text-white font-bold">
                2
              </div>
              <div>
                <h4 className="text-lg font-semibold text-white mb-2">See the Explanation</h4>
                <p className="text-gray-300">
                  An explanation will show which features influenced the decision (e.g., transaction amount, card number, location).
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0 w-8 h-8 bg-green-500 rounded-full flex items-center justify-center text-white font-bold">
                3
              </div>
              <div>
                <h4 className="text-lg font-semibold text-white mb-2">Rate Your Experience</h4>
                <p className="text-gray-300">
                  Answer three simple questions on a 1-5 scale:
                </p>
                <ul className="list-disc list-inside mt-2 space-y-1 text-gray-300 ml-4">
                  <li><strong>Trust:</strong> How confident are you in this decision?</li>
                  <li><strong>Understanding:</strong> Do you understand why this decision was made?</li>
                  <li><strong>Usefulness:</strong> Is this explanation helpful?</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* Important Notes */}
        <div className="bg-yellow-500/10 border border-yellow-400/30 rounded-2xl p-6 mb-8">
          <h3 className="text-lg font-semibold text-yellow-200 mb-3">📝 Important Notes</h3>
          <ul className="space-y-2 text-gray-300">
            <li className="flex items-start">
              <CheckCircle className="h-5 w-5 text-yellow-400 mr-2 mt-0.5 flex-shrink-0" />
              <span><strong>No right or wrong answers</strong> - We want your honest opinion</span>
            </li>
            <li className="flex items-start">
              <CheckCircle className="h-5 w-5 text-yellow-400 mr-2 mt-0.5 flex-shrink-0" />
              <span><strong>Anonymous participation</strong> - Your responses are not linked to your identity</span>
            </li>
            <li className="flex items-start">
              <CheckCircle className="h-5 w-5 text-yellow-400 mr-2 mt-0.5 flex-shrink-0" />
              <span><strong>Take your time</strong> - There's no time limit per question</span>
            </li>
            <li className="flex items-start">
              <CheckCircle className="h-5 w-5 text-yellow-400 mr-2 mt-0.5 flex-shrink-0" />
              <span><strong>Research purpose</strong> - Data will be used for academic research on AI interpretability</span>
            </li>
          </ul>
        </div>

        {/* Consent */}
        <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-6 mb-8">
          <label className="flex items-start space-x-3 cursor-pointer">
            <input
              type="checkbox"
              checked={agreedToTerms}
              onChange={(e) => setAgreedToTerms(e.target.checked)}
              className="mt-1 w-5 h-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="text-gray-200">
              I understand the study purpose and agree to participate. I confirm that my responses will be used for academic research and that my participation is voluntary and anonymous.
            </span>
          </label>
        </div>

        {/* Start Button */}
        <button
          onClick={handleStartStudy}
          disabled={!agreedToTerms || isStarting}
          className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white font-bold py-4 px-8 rounded-xl hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center space-x-3 text-lg shadow-lg hover:shadow-xl"
        >
          {isStarting ? (
            <>
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
              <span>Starting Study...</span>
            </>
          ) : (
            <>
              <span>Start Study</span>
              <ArrowRight className="h-6 w-6" />
            </>
          )}
        </button>

        {/* Footer */}
        <div className="mt-8 text-center text-sm text-gray-400">
          <p>Questions or concerns? Contact: research@xai-platform.com</p>
          <p className="mt-2">This study is part of a Master's thesis on Explainable AI</p>
        </div>
      </div>
    </div>
  );
}
