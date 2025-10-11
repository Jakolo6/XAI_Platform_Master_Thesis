/**
 * RESEARCH / XAI EVALUATION PAGE
 * 
 * Central page for comparing explainability methods across models
 * Shows global leaderboard, trade-off analysis, and quality comparisons
 * Research-focused interface for ML specialists
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/auth';
import { Brain, TrendingUp, Target, Sparkles, Filter, Download, Loader2 } from 'lucide-react';
import QualityMetricsRadar from '@/components/charts/QualityMetricsRadar';
import TradeOffScatter from '@/components/charts/TradeOffScatter';
import { researchAPI } from '@/lib/api';

// Demo data for prototype
const DEMO_DATA = {
  models: [
    {
      model_id: 'xgboost_1',
      model_name: 'XGBoost IEEE-CIS',
      model_type: 'xgboost',
      dataset: 'IEEE-CIS Fraud',
      auc_roc: 0.9024,
      quality_score: 0.82,
      method: 'SHAP' as const,
      faithfulness: 0.85,
      robustness: 0.78,
      complexity: 0.83
    },
    {
      model_id: 'xgboost_2',
      model_name: 'XGBoost IEEE-CIS',
      model_type: 'xgboost',
      dataset: 'IEEE-CIS Fraud',
      auc_roc: 0.9024,
      quality_score: 0.75,
      method: 'LIME' as const,
      faithfulness: 0.72,
      robustness: 0.70,
      complexity: 0.82
    },
    {
      model_id: 'rf_1',
      model_name: 'Random Forest IEEE-CIS',
      model_type: 'random_forest',
      dataset: 'IEEE-CIS Fraud',
      auc_roc: 0.8676,
      quality_score: 0.79,
      method: 'SHAP' as const,
      faithfulness: 0.81,
      robustness: 0.75,
      complexity: 0.80
    },
    {
      model_id: 'rf_2',
      model_name: 'Random Forest IEEE-CIS',
      model_type: 'random_forest',
      dataset: 'IEEE-CIS Fraud',
      auc_roc: 0.8676,
      quality_score: 0.71,
      method: 'LIME' as const,
      faithfulness: 0.68,
      robustness: 0.67,
      complexity: 0.78
    }
  ],
  shapMetrics: {
    faithfulness: 0.85,
    robustness: 0.78,
    complexity: 0.83,
    stability: 0.80,
    sparsity: 0.75
  },
  limeMetrics: {
    faithfulness: 0.72,
    robustness: 0.70,
    complexity: 0.82,
    stability: 0.68,
    sparsity: 0.85
  }
};

export default function ResearchPage() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuthStore();
  const [selectedDataset, setSelectedDataset] = useState<string>('all');
  const [selectedMethod, setSelectedMethod] = useState<string>('all');
  const [showParetoFrontier, setShowParetoFrontier] = useState(true);
  const [leaderboardData, setLeaderboardData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }
    fetchLeaderboardData();
  }, [isAuthenticated, router]);

  const fetchLeaderboardData = async () => {
    setIsLoading(true);
    try {
      const response = await researchAPI.getLeaderboard();
      setLeaderboardData(response.data);
    } catch (error) {
      console.error('Failed to fetch leaderboard:', error);
      // Fallback to demo data
      setLeaderboardData(DEMO_DATA);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Use real data or fallback to demo
  const modelsData = leaderboardData?.models || DEMO_DATA.models;
  
  // Filter data based on selections
  const filteredData = modelsData.filter((model: any) => {
    if (selectedDataset !== 'all' && model.dataset_id !== selectedDataset) return false;
    if (selectedMethod !== 'all' && model.method !== selectedMethod) return false;
    return true;
  });
  
  // Show loading state
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading research data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-gradient-to-br from-purple-500 to-blue-600 rounded-lg">
                  <Brain className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                    XAI Research Lab
                  </h1>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    Compare explainability methods and evaluate interpretability quality
                  </p>
                </div>
              </div>
            </div>
            <button className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
              <Download className="h-4 w-4 mr-2" />
              Export Results
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Filters */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4 mb-6">
          <div className="flex items-center space-x-4">
            <Filter className="h-5 w-5 text-gray-400" />
            <div className="flex-1 grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Dataset
                </label>
                <select
                  value={selectedDataset}
                  onChange={(e) => setSelectedDataset(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm dark:bg-gray-700 dark:text-white"
                >
                  <option value="all">All Datasets</option>
                  <option value="IEEE-CIS Fraud">IEEE-CIS Fraud</option>
                  <option value="Give Me Some Credit">Give Me Some Credit</option>
                  <option value="German Credit">German Credit</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Explanation Method
                </label>
                <select
                  value={selectedMethod}
                  onChange={(e) => setSelectedMethod(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm dark:bg-gray-700 dark:text-white"
                >
                  <option value="all">All Methods</option>
                  <option value="SHAP">SHAP Only</option>
                  <option value="LIME">LIME Only</option>
                </select>
              </div>
              <div className="flex items-end">
                <label className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={showParetoFrontier}
                    onChange={(e) => setShowParetoFrontier(e.target.checked)}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-700 dark:text-gray-300">
                    Show Pareto Frontier
                  </span>
                </label>
              </div>
            </div>
          </div>
        </div>

        {/* Key Metrics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg p-6 text-white shadow-lg">
            <div className="flex items-center justify-between mb-2">
              <TrendingUp className="h-8 w-8 opacity-80" />
              <span className="text-xs font-medium bg-white/20 px-2 py-1 rounded">AVG</span>
            </div>
            <div className="text-3xl font-bold mb-1">88.5%</div>
            <div className="text-sm opacity-90">Model Performance</div>
            <div className="text-xs opacity-75 mt-1">Across all models</div>
          </div>

          <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg p-6 text-white shadow-lg">
            <div className="flex items-center justify-between mb-2">
              <Sparkles className="h-8 w-8 opacity-80" />
              <span className="text-xs font-medium bg-white/20 px-2 py-1 rounded">SHAP</span>
            </div>
            <div className="text-3xl font-bold mb-1">80.2%</div>
            <div className="text-sm opacity-90">Avg Quality Score</div>
            <div className="text-xs opacity-75 mt-1">SHAP explanations</div>
          </div>

          <div className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-lg p-6 text-white shadow-lg">
            <div className="flex items-center justify-between mb-2">
              <Target className="h-8 w-8 opacity-80" />
              <span className="text-xs font-medium bg-white/20 px-2 py-1 rounded">LIME</span>
            </div>
            <div className="text-3xl font-bold mb-1">73.0%</div>
            <div className="text-sm opacity-90">Avg Quality Score</div>
            <div className="text-xs opacity-75 mt-1">LIME explanations</div>
          </div>

          <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-lg p-6 text-white shadow-lg">
            <div className="flex items-center justify-between mb-2">
              <Brain className="h-8 w-8 opacity-80" />
              <span className="text-xs font-medium bg-white/20 px-2 py-1 rounded">BEST</span>
            </div>
            <div className="text-3xl font-bold mb-1">90.2%</div>
            <div className="text-sm opacity-90">Top Model AUC</div>
            <div className="text-xs opacity-75 mt-1">XGBoost + SHAP</div>
          </div>
        </div>

        {/* Trade-off Scatter Plot */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 mb-8">
          <TradeOffScatter 
            data={filteredData}
            showParetoFrontier={showParetoFrontier}
          />
        </div>

        {/* Radar Comparison */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 mb-8">
          <QualityMetricsRadar 
            shapMetrics={DEMO_DATA.shapMetrics}
            limeMetrics={DEMO_DATA.limeMetrics}
          />
        </div>

        {/* Global Leaderboard */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">
              Global XAI Leaderboard
            </h2>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              Ranked by composite quality score (faithfulness + robustness + complexity)
            </p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Rank
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Model
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Dataset
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Method
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    AUC-ROC
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Faithfulness
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Robustness
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Complexity
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Quality Score
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {filteredData
                  .sort((a, b) => b.quality_score - a.quality_score)
                  .map((model, index) => (
                    <tr key={model.model_id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex items-center justify-center w-8 h-8 rounded-full text-sm font-bold ${
                          index === 0 ? 'bg-yellow-100 text-yellow-800' :
                          index === 1 ? 'bg-gray-100 text-gray-800' :
                          index === 2 ? 'bg-orange-100 text-orange-800' :
                          'bg-gray-50 text-gray-600'
                        }`}>
                          {index + 1}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900 dark:text-white">
                          {model.model_type}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                        {model.dataset}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          model.method === 'SHAP' 
                            ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300'
                            : 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300'
                        }`}>
                          {model.method}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                        {(model.auc_roc * 100).toFixed(2)}%
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                        {(model.faithfulness * 100).toFixed(1)}%
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                        {(model.robustness * 100).toFixed(1)}%
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                        {(model.complexity * 100).toFixed(1)}%
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="text-sm font-bold text-gray-900 dark:text-white mr-2">
                            {(model.quality_score * 100).toFixed(1)}%
                          </div>
                          <div className="w-16 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                            <div 
                              className="bg-gradient-to-r from-blue-500 to-purple-600 h-2 rounded-full"
                              style={{ width: `${model.quality_score * 100}%` }}
                            />
                          </div>
                        </div>
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Research Insights */}
        <div className="mt-8 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
            📊 Research Insights
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-700 dark:text-gray-300">
            <div>
              <strong>SHAP Advantages:</strong>
              <ul className="list-disc list-inside mt-1 space-y-1 text-xs">
                <li>Higher faithfulness scores (85% vs 72%)</li>
                <li>Better robustness across perturbations</li>
                <li>Theoretically grounded (Shapley values)</li>
              </ul>
            </div>
            <div>
              <strong>LIME Advantages:</strong>
              <ul className="list-disc list-inside mt-1 space-y-1 text-xs">
                <li>Higher sparsity (85% vs 75%)</li>
                <li>Model-agnostic approach</li>
                <li>Faster generation time</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
