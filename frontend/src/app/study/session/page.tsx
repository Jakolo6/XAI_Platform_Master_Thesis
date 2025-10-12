/**
 * HUMAN STUDY SESSION PAGE
 * Route: /study/session
 * 
 * Interactive study session where participants rate explanations
 * Shows model predictions with SHAP explanations and collects trust/understanding ratings
 */

'use client';

export const dynamic = 'force-dynamic';

import { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { CheckCircle, ArrowRight, ArrowLeft, Loader2, Star } from 'lucide-react';
import axios from 'axios';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

interface Question {
  question_id: number;
  model_prediction: string;
  true_label: string;
  confidence: number;
  explanation_method: string;
  feature_importance: { [key: string]: number };
}

function StudySessionContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const sessionId = searchParams.get('session_id');
  
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [responses, setResponses] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [completed, setCompleted] = useState(false);
  
  // Rating states
  const [trustRating, setTrustRating] = useState(0);
  const [understandingRating, setUnderstandingRating] = useState(0);
  const [usefulnessRating, setUsefulnessRating] = useState(0);

  useEffect(() => {
    if (!sessionId) {
      router.push('/study');
      return;
    }
    loadQuestions();
  }, [sessionId]);

  const loadQuestions = async () => {
    setIsLoading(true);
    try {
      // Fetch real questions from backend
      const response = await axios.get(`${API_BASE}/humanstudy/questions`);
      setQuestions(response.data.questions || response.data);
    } catch (error: any) {
      console.error('Failed to load questions:', error);
      const errorMsg = error.response?.data?.detail || error.message || 'Failed to load study questions';
      alert(`Backend Error: ${errorMsg}\n\nCould not load study questions. Please ensure:\n1. Backend is running\n2. Models are trained\n3. Explanations are generated\n\nEndpoint: GET /api/v1/humanstudy/questions`);
      setQuestions([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmitResponse = async () => {
    if (trustRating === 0 || understandingRating === 0 || usefulnessRating === 0) {
      alert('Please provide all ratings before continuing');
      return;
    }

    const response = {
      question_id: questions[currentQuestion].question_id,
      trust_rating: trustRating,
      understanding_rating: understandingRating,
      usefulness_rating: usefulnessRating,
      time_spent: 30, // Could track actual time
    };

    setResponses([...responses, response]);
    
    // Reset ratings
    setTrustRating(0);
    setUnderstandingRating(0);
    setUsefulnessRating(0);

    // Move to next question or complete
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    } else {
      await submitAllResponses();
    }
  };

  const submitAllResponses = async () => {
    setIsSubmitting(true);
    try {
      await axios.post(`${API_BASE}/humanstudy/responses`, {
        session_id: sessionId,
        responses: [...responses, {
          question_id: questions[currentQuestion].question_id,
          trust_rating: trustRating,
          understanding_rating: understandingRating,
          usefulness_rating: usefulnessRating,
          time_spent: 30,
        }]
      });
      setCompleted(true);
    } catch (error) {
      console.error('Failed to submit responses:', error);
      alert('Failed to submit responses. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const RatingStars = ({ rating, setRating, label }: { rating: number; setRating: (r: number) => void; label: string }) => (
    <div className="mb-6">
      <label className="block text-sm font-medium text-gray-700 mb-2">{label}</label>
      <div className="flex gap-2">
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            onClick={() => setRating(star)}
            className="focus:outline-none transition-transform hover:scale-110"
          >
            <Star
              className={`h-8 w-8 ${
                star <= rating
                  ? 'fill-yellow-400 text-yellow-400'
                  : 'text-gray-300'
              }`}
            />
          </button>
        ))}
        <span className="ml-2 text-sm text-gray-600 self-center">
          {rating > 0 ? `${rating}/5` : 'Not rated'}
        </span>
      </div>
    </div>
  );

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading study questions...</p>
        </div>
      </div>
    );
  }

  if (completed) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-6">
            <CheckCircle className="h-10 w-10 text-green-600" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Study Complete!
          </h2>
          <p className="text-gray-600 mb-8">
            Thank you for participating in our XAI evaluation study. Your responses help us understand how people interpret AI explanations.
          </p>
          <button
            onClick={() => router.push('/dashboard')}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Return to Dashboard
          </button>
        </div>
      </div>
    );
  }

  const question = questions[currentQuestion];
  const progress = ((currentQuestion + 1) / questions.length) * 100;

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>Question {currentQuestion + 1} of {questions.length}</span>
            <span>{Math.round(progress)}% Complete</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Question Card */}
        <div className="bg-white rounded-lg shadow-lg p-8 mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">
            Evaluate This Explanation
          </h2>

          {/* Model Prediction */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
            <h3 className="font-semibold text-gray-900 mb-4">Model Prediction</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="text-sm text-gray-600">Prediction</div>
                <div className="text-lg font-bold text-gray-900">{question.model_prediction}</div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Confidence</div>
                <div className="text-lg font-bold text-gray-900">
                  {(question.confidence * 100).toFixed(1)}%
                </div>
              </div>
            </div>
          </div>

          {/* Explanation */}
          <div className="mb-6">
            <h3 className="font-semibold text-gray-900 mb-4">
              Explanation ({question.explanation_method})
            </h3>
            <div className="space-y-2">
              {Object.entries(question.feature_importance)
                .sort(([, a], [, b]) => Math.abs(b) - Math.abs(a))
                .map(([feature, importance]) => (
                  <div key={feature} className="flex items-center gap-3">
                    <div className="w-40 text-sm text-gray-700">{feature}</div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <div className="flex-1 bg-gray-200 rounded-full h-6 relative">
                          <div
                            className={`h-6 rounded-full ${
                              importance > 0 ? 'bg-blue-500' : 'bg-red-500'
                            }`}
                            style={{
                              width: `${Math.abs(importance) * 100}%`,
                              marginLeft: importance < 0 ? `${100 - Math.abs(importance) * 100}%` : '0'
                            }}
                          />
                        </div>
                        <div className="w-16 text-sm text-gray-600 text-right">
                          {importance > 0 ? '+' : ''}{importance.toFixed(2)}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
            </div>
          </div>

          {/* Rating Questions */}
          <div className="border-t pt-6">
            <h3 className="font-semibold text-gray-900 mb-6">Rate This Explanation</h3>
            
            <RatingStars
              rating={trustRating}
              setRating={setTrustRating}
              label="How much do you trust this explanation?"
            />
            
            <RatingStars
              rating={understandingRating}
              setRating={setUnderstandingRating}
              label="How well do you understand why the model made this prediction?"
            />
            
            <RatingStars
              rating={usefulnessRating}
              setRating={setUsefulnessRating}
              label="How useful is this explanation for decision-making?"
            />
          </div>

          {/* Navigation */}
          <div className="flex justify-between mt-8 pt-6 border-t">
            <button
              onClick={() => setCurrentQuestion(Math.max(0, currentQuestion - 1))}
              disabled={currentQuestion === 0}
              className="flex items-center px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ArrowLeft className="h-5 w-5 mr-2" />
              Previous
            </button>
            
            <button
              onClick={handleSubmitResponse}
              disabled={isSubmitting || trustRating === 0 || understandingRating === 0 || usefulnessRating === 0}
              className="flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                  Submitting...
                </>
              ) : currentQuestion < questions.length - 1 ? (
                <>
                  Next Question
                  <ArrowRight className="h-5 w-5 ml-2" />
                </>
              ) : (
                <>
                  Complete Study
                  <CheckCircle className="h-5 w-5 ml-2" />
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function StudySessionPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center">Loading...</div>}>
      <StudySessionContent />
    </Suspense>
  );
}
