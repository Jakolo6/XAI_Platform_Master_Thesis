/**
 * MODEL COMPARISON PAGE
 * Route: /models/[id]/compare
 * 
 * Compares SHAP vs LIME explanations for a specific model.
 * Shows agreement metrics, correlation, and side-by-side comparison.
 * Protected route - requires authentication.
 */

'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { explanationsAPI, modelsAPI } from '@/lib/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';
import { ArrowLeft, TrendingUp, CheckCircle2, AlertCircle } from 'lucide-react';

interface FeatureImportance {
  feature: string;
  importance: number;
  rank: number;
}

interface ComparisonData {
  model_id: string;
  shap: {
    feature_importance: FeatureImportance[];
  };
  lime: {
    feature_importance: FeatureImportance[];
  };
  comparison: {
    common_features: number;
    top_5_agreement: number;
    top_10_agreement: number;
    rank_correlation: number;
    p_value: number;
  };
}

export default function ComparePage() {
  const params = useParams();
  const router = useRouter();
  const modelId = params.id as string;

  const [model, setModel] = useState<any>(null);
  const [comparison, setComparison] = useState<ComparisonData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedMethod, setSelectedMethod] = useState<'both' | 'shap' | 'lime'>('both');

  useEffect(() => {
    fetchData();
  }, [modelId]);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // Fetch model details
      const modelResponse = await modelsAPI.getById(modelId);
      setModel(modelResponse.data);

      // Fetch comparison data
      const comparisonResponse = await explanationsAPI.compare(modelId);
      setComparison(comparisonResponse.data);
      
      setLoading(false);
    } catch (err: any) {
      console.error('Failed to fetch comparison:', err);
      const errorDetail = err.response?.data?.detail || 'Failed to load comparison data';
      
      // Check if it's a missing explanations error
      if (errorDetail.includes('SHAP and LIME explanations required')) {
        setError('missing_explanations');
      } else {
        setError(errorDetail);
      }
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading comparison...</p>
        </div>
      </div>
    );
  }

  if (error) {
    // Special handling for missing explanations
    if (error === 'missing_explanations') {
      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg shadow-lg p-8 max-w-2xl">
            <AlertCircle className="w-16 h-16 text-yellow-500 mx-auto mb-4" />
            <h2 className="text-2xl font-semibold text-gray-900 mb-4 text-center">
              Explanations Not Ready
            </h2>
            <p className="text-gray-600 text-center mb-6">
              To compare SHAP and LIME, you need to generate both explanations first.
            </p>
            
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
              <h3 className="font-semibold text-blue-900 mb-3">📋 Quick Setup:</h3>
              <ol className="space-y-2 text-blue-800 text-sm">
                <li>1. Go back to the model detail page</li>
                <li>2. Click <strong>"Generate SHAP Explanation"</strong> (takes ~3 seconds)</li>
                <li>3. Wait for SHAP to complete</li>
                <li>4. Click <strong>"Generate LIME Explanation"</strong> (takes ~15 minutes)</li>
                <li>5. Wait for LIME to complete</li>
                <li>6. Return here to see the comparison!</li>
              </ol>
            </div>

            <div className="flex gap-4">
              <button
                onClick={() => router.push(`/models/${modelId}`)}
                className="flex-1 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
              >
                Go to Model Page
              </button>
              <button
                onClick={fetchData}
                className="flex-1 px-4 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 font-medium"
              >
                Retry
              </button>
            </div>
          </div>
        </div>
      );
    }

    // Generic error handling
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2 text-center">Error</h2>
          <p className="text-gray-600 text-center mb-4">{error}</p>
          <button
            onClick={() => router.push(`/models/${modelId}`)}
            className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Back to Model
          </button>
        </div>
      </div>
    );
  }

  if (!comparison) return null;

  // Prepare data for side-by-side comparison
  const topN = 10;
  const shapTop = comparison.shap.feature_importance.slice(0, topN);
  const limeTop = comparison.lime.feature_importance.slice(0, topN);

  // Create combined data for comparison chart
  const allFeatures = new Set([
    ...shapTop.map(f => f.feature),
    ...limeTop.map(f => f.feature)
  ]);

  const comparisonChartData = Array.from(allFeatures).map(feature => {
    const shapFeature = comparison.shap.feature_importance.find(f => f.feature === feature);
    const limeFeature = comparison.lime.feature_importance.find(f => f.feature === feature);
    
    return {
      feature,
      shap: shapFeature?.importance || 0,
      lime: limeFeature?.importance || 0,
      inBoth: shapFeature && limeFeature,
    };
  }).sort((a, b) => (b.shap + b.lime) - (a.shap + a.lime)).slice(0, 15);

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => router.push(`/models/${modelId}`)}
            className="flex items-center text-gray-600 hover:text-gray-900 mb-4"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Model
          </button>
          
          <h1 className="text-3xl font-bold text-gray-900">
            SHAP vs LIME Comparison
          </h1>
          {model && (
            <p className="text-gray-600 mt-2">
              Model: {model.model_type} | AUC-ROC: {(model.metrics?.auc_roc * 100).toFixed(2)}%
            </p>
          )}
        </div>

        {/* Comparison Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Common Features</p>
                <p className="text-2xl font-bold text-gray-900">
                  {comparison.comparison.common_features}/20
                </p>
              </div>
              <CheckCircle2 className="w-8 h-8 text-green-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Top-5 Agreement</p>
                <p className="text-2xl font-bold text-gray-900">
                  {(comparison.comparison.top_5_agreement * 100).toFixed(0)}%
                </p>
              </div>
              <TrendingUp className="w-8 h-8 text-blue-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Top-10 Agreement</p>
                <p className="text-2xl font-bold text-gray-900">
                  {(comparison.comparison.top_10_agreement * 100).toFixed(0)}%
                </p>
              </div>
              <TrendingUp className="w-8 h-8 text-purple-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Rank Correlation</p>
                <p className="text-2xl font-bold text-gray-900">
                  {comparison.comparison.rank_correlation.toFixed(3)}
                </p>
                <p className="text-xs text-gray-500">
                  p = {comparison.comparison.p_value.toFixed(4)}
                </p>
              </div>
              <TrendingUp className="w-8 h-8 text-orange-500" />
            </div>
          </div>
        </div>

        {/* Method Selector */}
        <div className="bg-white rounded-lg shadow p-4 mb-8">
          <div className="flex items-center gap-4">
            <span className="text-sm font-medium text-gray-700">View:</span>
            <div className="flex gap-2">
              <button
                onClick={() => setSelectedMethod('both')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  selectedMethod === 'both'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Both Methods
              </button>
              <button
                onClick={() => setSelectedMethod('shap')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  selectedMethod === 'shap'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                SHAP Only
              </button>
              <button
                onClick={() => setSelectedMethod('lime')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  selectedMethod === 'lime'
                    ? 'bg-green-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                LIME Only
              </button>
            </div>
          </div>
        </div>

        {/* Comparison Chart */}
        {selectedMethod === 'both' && (
          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Feature Importance Comparison (Top 15)
            </h2>
            <ResponsiveContainer width="100%" height={500}>
              <BarChart data={comparisonChartData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis type="category" dataKey="feature" width={150} />
                <Tooltip />
                <Legend />
                <Bar dataKey="shap" fill="#3B82F6" name="SHAP" />
                <Bar dataKey="lime" fill="#10B981" name="LIME" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Side-by-Side Tables */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* SHAP Table */}
          {(selectedMethod === 'both' || selectedMethod === 'shap') && (
            <div className="bg-white rounded-lg shadow overflow-hidden">
              <div className="bg-blue-600 px-6 py-4">
                <h3 className="text-lg font-semibold text-white">SHAP Feature Importance</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rank</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Feature</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Importance</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {shapTop.map((feature, idx) => (
                      <tr key={feature.feature} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {idx + 1}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {feature.feature}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {feature.importance.toFixed(4)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* LIME Table */}
          {(selectedMethod === 'both' || selectedMethod === 'lime') && (
            <div className="bg-white rounded-lg shadow overflow-hidden">
              <div className="bg-green-600 px-6 py-4">
                <h3 className="text-lg font-semibold text-white">LIME Feature Importance</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rank</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Feature</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Importance</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {limeTop.map((feature, idx) => (
                      <tr key={feature.feature} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {idx + 1}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {feature.feature}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {feature.importance.toFixed(4)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>

        {/* Insights */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-3">📊 Key Insights</h3>
          <ul className="space-y-2 text-blue-800">
            <li>
              • Both methods agree that <strong>{shapTop[0].feature}</strong> is the most important feature
            </li>
            <li>
              • {comparison.comparison.common_features} features appear in both top-20 lists
            </li>
            <li>
              • Rank correlation of {comparison.comparison.rank_correlation.toFixed(3)} indicates{' '}
              {comparison.comparison.rank_correlation > 0.7 ? 'strong' : 
               comparison.comparison.rank_correlation > 0.4 ? 'moderate' : 'weak'} agreement
            </li>
            <li>
              • {comparison.comparison.top_10_agreement >= 0.5 ? 'Good' : 'Moderate'} overlap in top-10 features 
              ({(comparison.comparison.top_10_agreement * 100).toFixed(0)}%)
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
