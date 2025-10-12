/**
 * GLOBAL MODELS COMPARISON PAGE
 * Route: /models/compare
 * 
 * Compare multiple models against each other.
 * Shows model selection and comparison interface.
 * Protected route - requires authentication.
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { createClient } from '@/lib/supabase/client';
import { useModelsStore } from '@/store/models';
import { Brain, LogOut, ArrowLeft } from 'lucide-react';
import { formatPercentage, formatDuration, getRankBadge, getModelTypeLabel } from '@/lib/utils';
import type { User } from '@supabase/supabase-js';

export default function CompareModelsPage() {
  const router = useRouter();
  const supabase = createClient();
  const [user, setUser] = useState<User | null>(null);
  const { leaderboard, fetchLeaderboard, isLoading } = useModelsStore();

  useEffect(() => {
    supabase.auth.getUser().then(({ data: { user } }) => {
      setUser(user);
      if (user) {
        fetchLeaderboard();
      }
    });
  }, [fetchLeaderboard]);

  const handleLogout = async () => {
    await supabase.auth.signOut();
    router.push('/');
  };

  if (!user) {
    return null;
  }

  // Get top 4 models for comparison
  const topModels = leaderboard.slice(0, 4);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white border-b sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex items-center space-x-8">
              <Link href="/dashboard" className="flex items-center space-x-2">
                <Brain className="h-8 w-8 text-blue-600" />
                <span className="text-xl font-bold">XAI Finance</span>
              </Link>
              <div className="hidden md:flex space-x-4">
                <Link
                  href="/dashboard"
                  className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
                >
                  Dashboard
                </Link>
                <Link
                  href="/models"
                  className="text-blue-600 px-3 py-2 rounded-md text-sm font-medium"
                >
                  Models
                </Link>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">{user?.email}</span>
              <button
                onClick={handleLogout}
                className="text-gray-600 hover:text-gray-900 p-2 rounded-md"
                title="Logout"
              >
                <LogOut className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <Link
            href="/models"
            className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900 mb-4"
          >
            <ArrowLeft className="h-4 w-4 mr-1" />
            Back to Models
          </Link>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Model Comparison</h1>
          <p className="text-gray-600">Side-by-side comparison of top performing models</p>
        </div>

        {isLoading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-600">Loading models...</p>
          </div>
        ) : topModels.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-600">No models to compare</p>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Performance Chart */}
            <div className="bg-white rounded-lg shadow-sm border">
              <div className="px-6 py-4 border-b">
                <h2 className="text-xl font-bold text-gray-900">Performance Comparison</h2>
              </div>
              <div className="p-6">
                <ComparisonChart models={topModels} />
              </div>
            </div>

            {/* Comparison Table */}
            <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
              <table className="min-w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Metric
                    </th>
                    {topModels.map((model) => (
                      <th key={model.model_id} className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                        <div className="flex flex-col items-center">
                          <span className="text-lg mb-1">{getRankBadge(model.rank)}</span>
                          <span>{getModelTypeLabel(model.model_type)}</span>
                        </div>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  <tr>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      AUC-ROC
                    </td>
                    {topModels.map((model) => (
                      <td key={model.model_id} className="px-6 py-4 whitespace-nowrap text-center">
                        <span className={`text-sm font-semibold ${model.rank === 1 ? 'text-green-600' : 'text-gray-900'}`}>
                          {formatPercentage(model.auc_roc)}
                        </span>
                      </td>
                    ))}
                  </tr>
                  <tr className="bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      AUC-PR
                    </td>
                    {topModels.map((model) => (
                      <td key={model.model_id} className="px-6 py-4 whitespace-nowrap text-center">
                        <span className={`text-sm font-semibold ${model.rank === 1 ? 'text-green-600' : 'text-gray-900'}`}>
                          {formatPercentage(model.auc_pr)}
                        </span>
                      </td>
                    ))}
                  </tr>
                  <tr>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      F1 Score
                    </td>
                    {topModels.map((model) => (
                      <td key={model.model_id} className="px-6 py-4 whitespace-nowrap text-center">
                        <span className={`text-sm font-semibold ${model.rank === 1 ? 'text-green-600' : 'text-gray-900'}`}>
                          {formatPercentage(model.f1_score)}
                        </span>
                      </td>
                    ))}
                  </tr>
                  <tr className="bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      Accuracy
                    </td>
                    {topModels.map((model) => (
                      <td key={model.model_id} className="px-6 py-4 whitespace-nowrap text-center">
                        <span className={`text-sm font-semibold ${model.rank === 1 ? 'text-green-600' : 'text-gray-900'}`}>
                          {formatPercentage(model.accuracy)}
                        </span>
                      </td>
                    ))}
                  </tr>
                  <tr>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      Training Time
                    </td>
                    {topModels.map((model) => (
                      <td key={model.model_id} className="px-6 py-4 whitespace-nowrap text-center">
                        <span className="text-sm font-semibold text-gray-900">
                          {formatDuration(model.training_time_seconds)}
                        </span>
                      </td>
                    ))}
                  </tr>
                </tbody>
              </table>
            </div>

            {/* Key Insights */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
              <h3 className="text-lg font-bold text-blue-900 mb-4">Key Insights</h3>
              <ul className="space-y-2 text-sm text-blue-800">
                <li>• <strong>Best Overall:</strong> {topModels[0] ? getModelTypeLabel(topModels[0].model_type) : '-'} with {topModels[0] ? formatPercentage(topModels[0].auc_roc) : '-'} AUC-ROC</li>
                <li>• <strong>Fastest:</strong> {topModels.reduce((fastest, model) => 
                  model.training_time_seconds < fastest.training_time_seconds ? model : fastest
                ).model_type ? getModelTypeLabel(topModels.reduce((fastest, model) => 
                  model.training_time_seconds < fastest.training_time_seconds ? model : fastest
                ).model_type) : '-'} in {topModels.length > 0 ? formatDuration(Math.min(...topModels.map(m => m.training_time_seconds))) : '-'}</li>
                <li>• <strong>Top 3 models</strong> achieve 93-94% AUC-ROC (excellent performance)</li>
                <li>• <strong>Gradient boosting methods</strong> (XGBoost, CatBoost, LightGBM) outperform others</li>
              </ul>
            </div>

            {/* View Individual Models */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {topModels.map((model) => (
                <Link
                  key={model.model_id}
                  href={`/models/${model.model_id}`}
                  className="bg-white rounded-lg shadow-sm border p-4 hover:shadow-md transition-shadow text-center"
                >
                  <div className="text-2xl mb-2">{getRankBadge(model.rank)}</div>
                  <div className="font-semibold text-gray-900 mb-1">
                    {getModelTypeLabel(model.model_type)}
                  </div>
                  <div className="text-sm text-blue-600">View Details →</div>
                </Link>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
