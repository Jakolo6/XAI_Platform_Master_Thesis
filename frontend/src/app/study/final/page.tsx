/**
 * STUDY FINAL COMPARISON PAGE
 * Route: /study/final
 * 
 * Shows participant a summary of all 4 explanation layers they experienced.
 * Collects final ranking: which layer did they prefer most/least?
 */

'use client';

export const dynamic = 'force-dynamic';

import { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { CheckCircle, Loader2, TrendingUp, Trophy } from 'lucide-react';
import axios from 'axios';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// ============================================================================
// TypeScript Interfaces
// ============================================================================

interface LayerSummary {
  layer_type: string;
  num_cases: number;
  avg_trust: number;
  avg_understanding: number;
  avg_usefulness: number;
  cases: Array<{
    case_index: number;
    trust: number;
    understanding: number;
    usefulness: number;
  }>;
}

interface ComparisonData {
  session_id: string;
  total_cases: number;
  layer_summary: Record<string, LayerSummary>;
  layers_shown: string[];
}

// ============================================================================
// Main Component
// ============================================================================

function FinalComparisonContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const sessionId = searchParams.get('session_id');
  
  const [comparisonData, setComparisonData] = useState<ComparisonData | null>(null);
  const [rankings, setRankings] = useState<Record<string, number>>({});
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [completed, setCompleted] = useState(false);

  useEffect(() => {
    if (!sessionId) {
      router.push('/study');
      return;
    }
    loadComparisonData();
  }, [sessionId]);

  const loadComparisonData = async () => {
    setIsLoading(true);
    try {
      const response = await axios.get(`${API_BASE}/study/session/${sessionId}/final`);
      setComparisonData(response.data);
      
      // Initialize rankings
      const initialRankings: Record<string, number> = {};
      response.data.layers_shown.forEach((layer: string) => {
        initialRankings[layer] = 0;
      });
      setRankings(initialRankings);
      
    } catch (err: any) {
      console.error('Failed to load comparison data:', err);
      alert('Failed to load comparison data');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmitRankings = async () => {
    // Validate all layers are ranked
    const rankedValues = Object.values(rankings);
    if (rankedValues.some(r => r === 0)) {
      alert('Please rank all explanation styles before submitting');
      return;
    }
    
    // Validate rankings are 1, 2, 3, 4
    const sortedRanks = rankedValues.slice().sort();
    const expectedRanks = comparisonData!.layers_shown.map((_, i) => i + 1);
    if (JSON.stringify(sortedRanks) !== JSON.stringify(expectedRanks)) {
      alert('Please assign each rank exactly once (1 = best, 4 = worst)');
      return;
    }
    
    setIsSubmitting(true);
    try {
      await axios.post(`${API_BASE}/study/session/${sessionId}/ranking`, {
        session_id: sessionId,
        rankings: rankings
      });
      
      setCompleted(true);
    } catch (err: any) {
      console.error('Failed to submit rankings:', err);
      alert('Failed to submit rankings');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-blue-50">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading comparison data...</p>
        </div>
      </div>
    );
  }

  if (completed) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-blue-50 p-4">
        <div className="max-w-2xl w-full bg-white rounded-2xl shadow-2xl p-12 text-center">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-green-100 rounded-full mb-6">
            <CheckCircle className="h-12 w-12 text-green-600" />
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Study Complete!
          </h1>
          <p className="text-lg text-gray-700 mb-8">
            Thank you for participating in our master thesis research on explainable AI. 
            Your feedback will help us understand how different explanation styles affect 
            trust and understanding in AI-assisted loan decisions.
          </p>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8">
            <p className="text-sm text-blue-900">
              <strong>Session ID:</strong> {sessionId}
            </p>
            <p className="text-xs text-blue-700 mt-2">
              Your responses have been saved. You may close this window.
            </p>
          </div>
          <button
            onClick={() => router.push('/')}
            className="px-8 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-semibold rounded-lg hover:from-blue-700 hover:to-indigo-700 shadow-lg"
          >
            Return to Home
          </button>
        </div>
      </div>
    );
  }

  if (!comparisonData) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 py-12">
      <div className="max-w-6xl mx-auto px-4">
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-yellow-100 rounded-full mb-4">
            <Trophy className="h-10 w-10 text-yellow-600" />
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Final Step: Rank the Explanation Styles
          </h1>
          <p className="text-lg text-gray-700 max-w-3xl mx-auto">
            You've seen {comparisonData.total_cases} loan decisions explained in different styles. 
            Now, please rank these explanation styles from <strong>1 (best)</strong> to <strong>{comparisonData.layers_shown.length} (worst)</strong> 
            based on your overall experience.
          </p>
        </div>

        {/* Layer Summaries */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
          {comparisonData.layers_shown.map((layerType) => {
            const summary = comparisonData.layer_summary[layerType];
            if (!summary) return null;
            
            return (
              <div key={layerType} className="bg-white rounded-xl border border-gray-200 p-6 shadow-lg">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-bold text-gray-900">
                    {layerType.replace('_', ' ').toUpperCase()}
                  </h3>
                  <div className="text-sm text-gray-600">
                    {summary.num_cases} case{summary.num_cases > 1 ? 's' : ''}
                  </div>
                </div>
                
                {/* Average Scores */}
                <div className="grid grid-cols-3 gap-3 mb-4">
                  <div className="bg-blue-50 rounded-lg p-3 text-center">
                    <div className="text-xs text-gray-600 mb-1">Trust</div>
                    <div className="text-lg font-bold text-blue-600">
                      {summary.avg_trust.toFixed(1)}
                    </div>
                  </div>
                  <div className="bg-green-50 rounded-lg p-3 text-center">
                    <div className="text-xs text-gray-600 mb-1">Understanding</div>
                    <div className="text-lg font-bold text-green-600">
                      {summary.avg_understanding.toFixed(1)}
                    </div>
                  </div>
                  <div className="bg-purple-50 rounded-lg p-3 text-center">
                    <div className="text-xs text-gray-600 mb-1">Usefulness</div>
                    <div className="text-lg font-bold text-purple-600">
                      {summary.avg_usefulness.toFixed(1)}
                    </div>
                  </div>
                </div>
                
                {/* Ranking Selector */}
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <label className="block text-sm font-semibold text-gray-900 mb-2">
                    Your Ranking:
                  </label>
                  <select
                    value={rankings[layerType] || 0}
                    onChange={(e) => setRankings({
                      ...rankings,
                      [layerType]: parseInt(e.target.value)
                    })}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg font-semibold"
                  >
                    <option value={0}>Select rank...</option>
                    {comparisonData.layers_shown.map((_, idx) => (
                      <option key={idx + 1} value={idx + 1}>
                        {idx + 1} {idx === 0 ? '(Best)' : idx === comparisonData.layers_shown.length - 1 ? '(Worst)' : ''}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            );
          })}
        </div>

        {/* Submit Button */}
        <div className="text-center">
          <button
            onClick={handleSubmitRankings}
            disabled={isSubmitting || Object.values(rankings).some(r => r === 0)}
            className="px-12 py-5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white text-lg font-bold rounded-xl hover:from-blue-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed shadow-xl transition-all flex items-center gap-3 mx-auto"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="h-6 w-6 animate-spin" />
                Submitting...
              </>
            ) : (
              <>
                <CheckCircle className="h-6 w-6" />
                Submit Final Rankings
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// Page Export with Suspense
// ============================================================================

export default function FinalComparisonPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-blue-50">
        <Loader2 className="h-12 w-12 animate-spin text-blue-600" />
      </div>
    }>
      <FinalComparisonContent />
    </Suspense>
  );
}
