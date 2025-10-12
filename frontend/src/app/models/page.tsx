/**
 * MODELS LIST PAGE
 * Route: /models
 * 
 * Displays all trained ML models.
 * Shows model cards with metrics and actions.
 * Protected route - requires authentication.
 */

'use client';

export const dynamic = 'force-dynamic';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuthStore } from '@/store/auth';
import { useModelsStore } from '@/store/models';
import { Brain, LogOut, ArrowLeft } from 'lucide-react';
import { formatPercentage, formatDuration, getRankBadge, getModelTypeLabel, getModelTypeColor } from '@/lib/utils';

export default function ModelsPage() {
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
            href="/dashboard"
            className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900 mb-4"
          >
            <ArrowLeft className="h-4 w-4 mr-1" />
            Back to Dashboard
          </Link>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">All Models</h1>
          <p className="text-gray-600">Complete list of trained fraud detection models</p>
        </div>

        {/* Models Grid */}
        {isLoading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-600">Loading models...</p>
          </div>
        ) : leaderboard.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-600">No models found</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {leaderboard.map((model) => (
              <Link
                key={model.model_id}
                href={`/models/${model.model_id}`}
                className="bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow"
              >
                <div className="p-6">
                  {/* Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-1">
                        <span className="text-2xl">{getRankBadge(model.rank)}</span>
                        <span className={`px-2 py-1 text-xs font-medium rounded ${getModelTypeColor(model.model_type)} text-white`}>
                          {getModelTypeLabel(model.model_type)}
                        </span>
                      </div>
                      <h3 className="font-semibold text-gray-900 text-lg">
                        {model.model_name}
                      </h3>
                    </div>
                  </div>

                  {/* Metrics */}
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">AUC-ROC</span>
                      <span className="text-sm font-semibold text-gray-900">
                        {formatPercentage(model.auc_roc)}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">F1 Score</span>
                      <span className="text-sm font-semibold text-gray-900">
                        {formatPercentage(model.f1_score)}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Accuracy</span>
                      <span className="text-sm font-semibold text-gray-900">
                        {formatPercentage(model.accuracy)}
                      </span>
                    </div>
                    <div className="flex justify-between items-center pt-3 border-t">
                      <span className="text-sm text-gray-600">Training Time</span>
                      <span className="text-sm font-semibold text-gray-900">
                        {formatDuration(model.training_time_seconds)}
                      </span>
                    </div>
                  </div>

                  {/* View Details Button */}
                  <div className="mt-4 pt-4 border-t">
                    <span className="text-blue-600 text-sm font-medium">
                      View Details →
                    </span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}

        {/* Compare Button */}
        {leaderboard.length > 1 && (
          <div className="mt-8 text-center">
            <Link
              href="/models/compare"
              className="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
            >
              Compare Models
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
