/**
 * STUDY SESSION PAGE - Master Thesis User Study
 * Route: /study/session
 * 
 * Presents 6 loan application cases from UCI German Credit dataset.
 * Each case shows: loan data, model decision, and ONE of 4 explanation layers.
 * Collects ratings: trust, understanding, usefulness, mental effort.
 * 
 * Dataset: UCI German Credit (Statlog) - 1000 rows, 20 features
 * Model: german_credit_xgb
 */

'use client';

export const dynamic = 'force-dynamic';

import { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { 
  CheckCircle, 
  ArrowRight, 
  Loader2, 
  Star, 
  User, 
  DollarSign, 
  Calendar,
  Briefcase,
  Home,
  TrendingUp,
  TrendingDown,
  AlertCircle,
  XCircle
} from 'lucide-react';
import axios from 'axios';
import { ExplanationRouter } from '@/components/study/ExplanationLayers';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
const TOTAL_CASES = 6;

// ============================================================================
// TypeScript Interfaces
// ============================================================================

interface LoanData {
  applicant_info: Record<string, any>;
  loan_details: Record<string, any>;
  financial_status: Record<string, any>;
  other_info: Record<string, any>;
}

interface Decision {
  approved: boolean;
  risk_score: number;
  confidence: number;
  label: string;
}

interface Explanation {
  layer_type: string;
  prediction_proba: number;
  base_value: number;
  top_features: Array<{
    feature: string;
    value: any;
    contribution: number;
    importance: number;
  }>;
  rendered_content: any;
}

interface CaseData {
  case_index: number;
  session_id: string;
  instance_id: string;
  loan_data: LoanData;
  decision: Decision;
  explanation: Explanation;
  explanation_layer: string;
}

// ============================================================================
// Main Component
// ============================================================================

function StudySessionContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const sessionId = searchParams.get('session_id');
  
  // State management
  const [currentCaseIndex, setCurrentCaseIndex] = useState(0);
  const [caseData, setCaseData] = useState<CaseData | null>(null);
  const [layerAssignments, setLayerAssignments] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [caseStartTime, setCaseStartTime] = useState<number>(Date.now());
  
  // Rating states
  const [trustRating, setTrustRating] = useState(0);
  const [understandingRating, setUnderstandingRating] = useState(0);
  const [usefulnessRating, setUsefulnessRating] = useState(0);
  const [mentalEffortRating, setMentalEffortRating] = useState(0);
  const [comments, setComments] = useState('');

  // Initialize session
  useEffect(() => {
    if (!sessionId) {
      router.push('/study');
      return;
    }
    
    // Get layer assignments from URL or fetch from backend
    const assignmentsParam = searchParams.get('assignments');
    if (assignmentsParam) {
      setLayerAssignments(assignmentsParam.split(','));
    }
    
    loadCase(0);
  }, [sessionId]);

  // Load a specific case
  const loadCase = async (caseIndex: number) => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Get layer assignment for this case
      const layerAssignment = layerAssignments[caseIndex] || 'layer_1';
      
      const response = await axios.post(`${API_BASE}/study/case`, {
        session_id: sessionId,
        case_index: caseIndex,
        layer_assignment: layerAssignment
      });
      
      setCaseData(response.data);
      setCaseStartTime(Date.now());
      
      // Reset ratings
      setTrustRating(0);
      setUnderstandingRating(0);
      setUsefulnessRating(0);
      setMentalEffortRating(0);
      setComments('');
      
    } catch (err: any) {
      console.error('Failed to load case:', err);
      setError(err.response?.data?.detail || 'Failed to load case');
    } finally {
      setIsLoading(false);
    }
  };

  // Submit ratings for current case
  const handleSubmitRatings = async () => {
    if (!caseData) return;
    
    // Validate all ratings are provided
    if (trustRating === 0 || understandingRating === 0 || 
        usefulnessRating === 0 || mentalEffortRating === 0) {
      alert('Please provide all ratings before continuing');
      return;
    }
    
    setIsSubmitting(true);
    setError(null);
    
    try {
      const timeSpent = (Date.now() - caseStartTime) / 1000; // seconds
      
      await axios.post(`${API_BASE}/study/response`, {
        session_id: sessionId,
        case_index: currentCaseIndex,
        instance_id: caseData.instance_id,
        explanation_layer: caseData.explanation_layer,
        trust: trustRating,
        understanding: understandingRating,
        usefulness: usefulnessRating,
        mental_effort: mentalEffortRating,
        time_spent: timeSpent,
        comments: comments || null,
        decision_label: caseData.decision.label,
        risk_score: caseData.decision.risk_score
      });
      
      // Move to next case or final screen
      if (currentCaseIndex < TOTAL_CASES - 1) {
        const nextIndex = currentCaseIndex + 1;
        setCurrentCaseIndex(nextIndex);
        await loadCase(nextIndex);
      } else {
        // All cases completed, go to final comparison
        router.push(`/study/final?session_id=${sessionId}`);
      }
      
    } catch (err: any) {
      console.error('Failed to submit ratings:', err);
      setError(err.response?.data?.detail || 'Failed to submit ratings');
    } finally {
      setIsSubmitting(false);
    }
  };

  // ============================================================================
  // Render Helper Components
  // ============================================================================

  const RatingStars = ({ 
    rating, 
    setRating, 
    label, 
    description 
  }: { 
    rating: number; 
    setRating: (r: number) => void; 
    label: string;
    description?: string;
  }) => (
    <div className="mb-6">
      <label className="block text-sm font-semibold text-gray-900 mb-1">{label}</label>
      {description && (
        <p className="text-xs text-gray-600 mb-2">{description}</p>
      )}
      <div className="flex gap-2 items-center">
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            onClick={() => setRating(star)}
            className="focus:outline-none transition-transform hover:scale-110"
            type="button"
          >
            <Star
              className={`h-8 w-8 ${
                star <= rating
                  ? 'fill-yellow-400 text-yellow-400'
                  : 'text-gray-300 hover:text-gray-400'
              }`}
            />
          </button>
        ))}
        <span className="ml-3 text-sm font-medium text-gray-700">
          {rating > 0 ? `${rating}/5` : 'Not rated'}
        </span>
      </div>
    </div>
  );

  const LoanDataDisplay = ({ loanData }: { loanData: LoanData }) => {
    const renderSection = (title: string, data: Record<string, any>, icon: React.ReactNode) => {
      if (Object.keys(data).length === 0) return null;
      
      return (
        <div className="mb-4">
          <div className="flex items-center gap-2 mb-3">
            {icon}
            <h4 className="font-semibold text-gray-900">{title}</h4>
          </div>
          <div className="grid grid-cols-2 gap-3">
            {Object.entries(data).map(([key, value]) => (
              <div key={key} className="bg-gray-50 rounded-lg p-3">
                <div className="text-xs text-gray-600 mb-1">{key}</div>
                <div className="text-sm font-medium text-gray-900">
                  {typeof value === 'number' ? value.toFixed(2) : String(value)}
                </div>
              </div>
            ))}
          </div>
        </div>
      );
    };

    return (
      <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4">Loan Application Details</h3>
        {renderSection('Applicant Information', loanData.applicant_info, <User className="w-5 h-5 text-blue-600" />)}
        {renderSection('Loan Details', loanData.loan_details, <DollarSign className="w-5 h-5 text-green-600" />)}
        {renderSection('Financial Status', loanData.financial_status, <Briefcase className="w-5 h-5 text-purple-600" />)}
        {renderSection('Other Information', loanData.other_info, <Home className="w-5 h-5 text-orange-600" />)}
      </div>
    );
  };

  const DecisionDisplay = ({ decision }: { decision: Decision }) => (
    <div className={`rounded-xl border-2 p-6 mb-6 ${
      decision.approved 
        ? 'bg-green-50 border-green-300' 
        : 'bg-red-50 border-red-300'
    }`}>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          {decision.approved ? (
            <CheckCircle className="w-8 h-8 text-green-600" />
          ) : (
            <XCircle className="w-8 h-8 text-red-600" />
          )}
          <div>
            <h3 className="text-xl font-bold text-gray-900">
              {decision.approved ? 'Loan Approved' : 'Loan Denied'}
            </h3>
            <p className="text-sm text-gray-700">{decision.label}</p>
          </div>
        </div>
        <div className="text-right">
          <div className="text-3xl font-bold text-gray-900">
            {(decision.confidence * 100).toFixed(0)}%
          </div>
          <div className="text-sm text-gray-600">Confidence</div>
        </div>
      </div>
      
      {/* Risk Score Bar */}
      <div className="mt-4">
        <div className="flex justify-between text-xs text-gray-600 mb-1">
          <span>Low Risk</span>
          <span>High Risk</span>
        </div>
        <div className="relative h-4 bg-gradient-to-r from-green-500 via-yellow-500 to-red-500 rounded-full">
          <div
            className="absolute top-0 h-full w-1 bg-gray-900"
            style={{ left: `${decision.risk_score * 100}%` }}
          />
        </div>
      </div>
    </div>
  );

  const ExplanationDisplay = ({ explanation }: { explanation: Explanation }) => {
    return (
      <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4">
          Why This Decision?
        </h3>
        
        {/* Use the ExplanationRouter to render the appropriate layer */}
        <ExplanationRouter
          layer_type={explanation.layer_type}
          features={explanation.top_features}
          prediction_proba={explanation.prediction_proba}
          base_value={explanation.base_value}
          rendered_content={explanation.rendered_content}
        />
      </div>
    );
  };

  // ============================================================================
  // Render States
  // ============================================================================

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-blue-50">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading case {currentCaseIndex + 1} of {TOTAL_CASES}...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-blue-50 p-4">
        <div className="max-w-md w-full bg-white rounded-xl shadow-lg p-8">
          <div className="flex items-center gap-3 mb-4">
            <AlertCircle className="w-8 h-8 text-red-600" />
            <h2 className="text-xl font-bold text-gray-900">Error</h2>
          </div>
          <p className="text-gray-700 mb-6">{error}</p>
          <button
            onClick={() => loadCase(currentCaseIndex)}
            className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!caseData) {
    return null;
  }

  const progress = ((currentCaseIndex + 1) / TOTAL_CASES) * 100;

  // ============================================================================
  // Main Render
  // ============================================================================

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 py-8">
      <div className="max-w-5xl mx-auto px-4">
        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex justify-between text-sm text-gray-700 mb-2">
            <span className="font-semibold">Case {currentCaseIndex + 1} of {TOTAL_CASES}</span>
            <span>{Math.round(progress)}% Complete</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
            <div
              className="bg-gradient-to-r from-blue-500 to-indigo-600 h-3 rounded-full transition-all duration-500"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Case Content */}
        <div className="space-y-6">
          {/* Loan Data */}
          <LoanDataDisplay loanData={caseData.loan_data} />
          
          {/* Model Decision */}
          <DecisionDisplay decision={caseData.decision} />
          
          {/* Explanation */}
          <ExplanationDisplay explanation={caseData.explanation} />
          
          {/* Rating Form */}
          <div className="bg-white rounded-xl border border-gray-200 p-8">
            <h3 className="text-xl font-bold text-gray-900 mb-6">
              Please Rate This Explanation
            </h3>
            
            <RatingStars
              rating={trustRating}
              setRating={setTrustRating}
              label="1. Trust"
              description="How much do you trust this explanation?"
            />
            
            <RatingStars
              rating={understandingRating}
              setRating={setUnderstandingRating}
              label="2. Understanding"
              description="How well do you understand why the model made this decision?"
            />
            
            <RatingStars
              rating={usefulnessRating}
              setRating={setUsefulnessRating}
              label="3. Usefulness"
              description="How useful is this explanation for making a decision?"
            />
            
            <RatingStars
              rating={mentalEffortRating}
              setRating={setMentalEffortRating}
              label="4. Mental Effort"
              description="How much mental effort did it take to understand this explanation? (1 = very easy, 5 = very difficult)"
            />
            
            {/* Optional Comments */}
            <div className="mt-6">
              <label className="block text-sm font-semibold text-gray-900 mb-2">
                Additional Comments (Optional)
              </label>
              <textarea
                value={comments}
                onChange={(e) => setComments(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                rows={3}
                placeholder="Any thoughts about this explanation?"
              />
            </div>
            
            {/* Submit Button */}
            <div className="mt-8 flex justify-end">
              <button
                onClick={handleSubmitRatings}
                disabled={
                  isSubmitting || 
                  trustRating === 0 || 
                  understandingRating === 0 || 
                  usefulnessRating === 0 || 
                  mentalEffortRating === 0
                }
                className="px-8 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-semibold rounded-lg hover:from-blue-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shadow-lg transition-all"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="h-5 w-5 animate-spin" />
                    Submitting...
                  </>
                ) : currentCaseIndex < TOTAL_CASES - 1 ? (
                  <>
                    Next Case
                    <ArrowRight className="h-5 w-5" />
                  </>
                ) : (
                  <>
                    Complete & Continue
                    <CheckCircle className="h-5 w-5" />
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// Page Export with Suspense
// ============================================================================

export default function StudySessionPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-blue-50">
        <Loader2 className="h-12 w-12 animate-spin text-blue-600" />
      </div>
    }>
      <StudySessionContent />
    </Suspense>
  );
}
