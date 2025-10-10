/**
 * DASHBOARD PAGE
 * Route: /dashboard
 * 
 * Main dashboard after login.
 * Shows overview of models, metrics, and quick actions.
 * Protected route - requires authentication.
 */

'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuthStore } from '@/store/auth';
import { useModelsStore } from '@/store/models';
import { 
  Brain, 
  BarChart3, 
  TrendingUp, 
  Award, 
  Clock,
  ArrowRight,
  LogOut
} from 'lucide-react';
import { formatPercentage, formatDuration, getRankBadge, getModelTypeLabel } from '@/lib/utils';

export default function DashboardPage() {
  const router = useRouter();
  const { isAuthenticated, logout, user } = useAuthStore();
  const { leaderboard, fetchLeaderboard, isLoading } = useModelsStore();

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }
    fetchLeaderboard();
  }, [isAuthenticated, router, fetchLeaderboard]);

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  if (!isAuthenticated) {
    return null;
  }

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
                  className="text-blue-600 px-3 py-2 rounded-md text-sm font-medium"
                >
                  Dashboard
                </Link>
                <Link
                  href="/models"
                  className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
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
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Dashboard</h1>
          <p className="text-gray-600">Overview of your fraud detection models</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex items-center justify-between mb-2">
              <div className="bg-blue-100 p-3 rounded-lg">
                <BarChart3 className="h-6 w-6 text-blue-600" />
              </div>
            </div>
            <div className="text-2xl font-bold text-gray-900">{leaderboard.length}</div>
            <div className="text-sm text-gray-600">Trained Models</div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex items-center justify-between mb-2">
              <div className="bg-green-100 p-3 rounded-lg">
                <TrendingUp className="h-6 w-6 text-green-600" />
              </div>
            </div>
            <div className="text-2xl font-bold text-gray-900">
              {leaderboard[0] ? formatPercentage(leaderboard[0].auc_roc, 1) : '-'}
            </div>
            <div className="text-sm text-gray-600">Best AUC-ROC</div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex items-center justify-between mb-2">
              <div className="bg-purple-100 p-3 rounded-lg">
                <Award className="h-6 w-6 text-purple-600" />
              </div>
            </div>
            <div className="text-2xl font-bold text-gray-900">
              {leaderboard[0] ? getModelTypeLabel(leaderboard[0].model_type) : '-'}
            </div>
            <div className="text-sm text-gray-600">Top Model</div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex items-center justify-between mb-2">
              <div className="bg-orange-100 p-3 rounded-lg">
                <Clock className="h-6 w-6 text-orange-600" />
              </div>
            </div>
            <div className="text-2xl font-bold text-gray-900">270k</div>
            <div className="text-sm text-gray-600">Training Samples</div>
          </div>
        </div>

        {/* Leaderboard */}
        <div className="bg-white rounded-lg shadow-sm border mb-8">
          <div className="px-6 py-4 border-b">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-bold text-gray-900">Model Leaderboard</h2>
              <Link
                href="/models"
                className="text-blue-600 hover:text-blue-700 text-sm font-medium inline-flex items-center"
              >
                View All
                <ArrowRight className="ml-1 h-4 w-4" />
              </Link>
            </div>
          </div>

          {isLoading ? (
            <div className="p-8 text-center text-gray-500">Loading models...</div>
          ) : leaderboard.length === 0 ? (
            <div className="p-8 text-center text-gray-500">No models found</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Rank
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Model
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      AUC-ROC
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      F1 Score
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Accuracy
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Training Time
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {leaderboard.map((model) => (
                    <tr key={model.model_id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        {getRankBadge(model.rank)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{model.model_name}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded">
                          {getModelTypeLabel(model.model_type)}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatPercentage(model.auc_roc)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatPercentage(model.f1_score)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatPercentage(model.accuracy)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatDuration(model.training_time_seconds)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <Link
                          href={`/models/${model.model_id}`}
                          className="text-blue-600 hover:text-blue-700 font-medium"
                        >
                          View Details
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Link
            href="/models"
            className="bg-white rounded-lg shadow-sm border p-6 hover:shadow-md transition-shadow"
          >
            <div className="flex items-center space-x-4">
              <div className="bg-blue-100 p-3 rounded-lg">
                <BarChart3 className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">View All Models</h3>
                <p className="text-sm text-gray-600">Explore detailed metrics</p>
              </div>
            </div>
          </Link>

          <Link
            href="/models/compare"
            className="bg-white rounded-lg shadow-sm border p-6 hover:shadow-md transition-shadow"
          >
            <div className="flex items-center space-x-4">
              <div className="bg-green-100 p-3 rounded-lg">
                <TrendingUp className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Compare Models</h3>
                <p className="text-sm text-gray-600">Side-by-side comparison</p>
              </div>
            </div>
          </Link>

          <div className="bg-white rounded-lg shadow-sm border p-6 opacity-50 cursor-not-allowed">
            <div className="flex items-center space-x-4">
              <div className="bg-purple-100 p-3 rounded-lg">
                <Brain className="h-6 w-6 text-purple-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Generate Explanations</h3>
                <p className="text-sm text-gray-600">Coming soon</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
