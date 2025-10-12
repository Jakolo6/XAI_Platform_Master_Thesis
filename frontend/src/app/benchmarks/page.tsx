'use client';

export const dynamic = 'force-dynamic';

import { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, Award, Clock } from 'lucide-react';
import { benchmarksAPI } from '@/lib/api';

interface BenchmarkData {
  dataset_id: string;
  dataset_name: string;
  models: Record<string, {
    auc_roc: number;
    f1_score: number;
    training_time_seconds: number;
    model_size_mb: number;
  }>;
}

export default function BenchmarksPage() {
  const [benchmarks, setBenchmarks] = useState<BenchmarkData[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedMetric, setSelectedMetric] = useState<'auc_roc' | 'f1_score'>('auc_roc');

  useEffect(() => {
    fetchBenchmarks();
  }, []);

  const fetchBenchmarks = async () => {
    try {
      setLoading(true);
      
      // Real API call to backend
      const response = await benchmarksAPI.getAll();
      setBenchmarks(response.data);
    } catch (error: any) {
      console.error('Failed to fetch benchmarks:', error);
      // Set empty array on error so UI shows empty state
      setBenchmarks([]);
    } finally {
      setLoading(false);
    }
  };

  const getMetricValue = (model: any, metric: string) => {
    return model[metric] || 0;
  };

  const getBestModel = (dataset: BenchmarkData) => {
    let best = { model: '', score: 0 };
    Object.entries(dataset.models).forEach(([modelType, metrics]) => {
      const score = getMetricValue(metrics, selectedMetric);
      if (score > best.score) {
        best = { model: modelType, score };
      }
    });
    return best;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading benchmarks...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 flex items-center">
            <BarChart3 className="h-8 w-8 mr-3 text-blue-600" />
            Cross-Dataset Benchmarks
          </h1>
          <p className="text-gray-600 mt-2">
            Compare model performance across different datasets
          </p>
        </div>

        {/* Metric Selector */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-8">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-700">Compare by:</span>
            <div className="flex gap-2">
              <button
                onClick={() => setSelectedMetric('auc_roc')}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  selectedMetric === 'auc_roc'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                AUC-ROC
              </button>
              <button
                onClick={() => setSelectedMetric('f1_score')}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  selectedMetric === 'f1_score'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                F1 Score
              </button>
            </div>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-600 text-sm">Datasets Compared</span>
              <BarChart3 className="h-5 w-5 text-blue-600" />
            </div>
            <div className="text-3xl font-bold text-gray-900">{benchmarks.length}</div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-600 text-sm">Total Models</span>
              <TrendingUp className="h-5 w-5 text-green-600" />
            </div>
            <div className="text-3xl font-bold text-gray-900">
              {benchmarks.reduce((sum, b) => sum + Object.keys(b.models).length, 0)}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-600 text-sm">Best Overall</span>
              <Award className="h-5 w-5 text-yellow-600" />
            </div>
            <div className="text-xl font-bold text-gray-900">
              {benchmarks.length > 0 ? getBestModel(benchmarks[0]).model : 'N/A'}
            </div>
          </div>
        </div>

        {/* Benchmark Tables */}
        {benchmarks.map((benchmark) => {
          const best = getBestModel(benchmark);
          
          return (
            <div key={benchmark.dataset_id} className="bg-white rounded-lg shadow-sm border border-gray-200 mb-8">
              {/* Dataset Header */}
              <div className="border-b border-gray-200 p-6">
                <h2 className="text-xl font-bold text-gray-900">{benchmark.dataset_name}</h2>
                <p className="text-sm text-gray-600 mt-1">Dataset ID: {benchmark.dataset_id}</p>
              </div>

              {/* Models Table */}
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Model
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        AUC-ROC
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        F1 Score
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Training Time
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Model Size
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {Object.entries(benchmark.models)
                      .sort((a, b) => getMetricValue(b[1], selectedMetric) - getMetricValue(a[1], selectedMetric))
                      .map(([modelType, metrics]) => {
                        const isBest = modelType === best.model;
                        
                        return (
                          <tr 
                            key={modelType}
                            className={isBest ? 'bg-yellow-50' : 'hover:bg-gray-50'}
                          >
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="flex items-center">
                                <span className="text-sm font-medium text-gray-900">
                                  {modelType}
                                </span>
                                {isBest && (
                                  <Award className="h-4 w-4 text-yellow-600 ml-2" />
                                )}
                              </div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className={`text-sm ${
                                selectedMetric === 'auc_roc' ? 'font-bold text-blue-600' : 'text-gray-900'
                              }`}>
                                {metrics.auc_roc?.toFixed(4) || 'N/A'}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className={`text-sm ${
                                selectedMetric === 'f1_score' ? 'font-bold text-blue-600' : 'text-gray-900'
                              }`}>
                                {metrics.f1_score?.toFixed(4) || 'N/A'}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="flex items-center text-sm text-gray-900">
                                <Clock className="h-4 w-4 mr-1 text-gray-400" />
                                {metrics.training_time_seconds?.toFixed(2)}s
                              </div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {metrics.model_size_mb?.toFixed(2)} MB
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                                Completed
                              </span>
                            </td>
                          </tr>
                        );
                      })}
                  </tbody>
                </table>
              </div>

              {/* Best Model Summary */}
              <div className="border-t border-gray-200 bg-gray-50 p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <Award className="h-5 w-5 text-yellow-600 mr-2" />
                    <span className="text-sm font-medium text-gray-700">
                      Best Model: <span className="text-gray-900">{best.model}</span>
                    </span>
                  </div>
                  <span className="text-sm text-gray-600">
                    {selectedMetric === 'auc_roc' ? 'AUC-ROC' : 'F1 Score'}: 
                    <span className="font-bold text-blue-600 ml-1">
                      {best.score.toFixed(4)}
                    </span>
                  </span>
                </div>
              </div>
            </div>
          );
        })}

        {/* Empty State */}
        {benchmarks.length === 0 && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
            <BarChart3 className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No Benchmarks Available</h3>
            <p className="text-gray-600 mb-6">
              Train models on different datasets to see performance comparisons here.
            </p>
            <button
              onClick={() => window.location.href = '/models/train'}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Train a Model
            </button>
          </div>
        )}

        {/* Info Box */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mt-8">
          <h3 className="font-semibold text-blue-900 mb-2">About Benchmarks</h3>
          <p className="text-sm text-blue-800">
            This page shows performance comparisons of different models across various datasets.
            The highlighted model in each dataset represents the best performer for the selected metric.
            Use this to identify which algorithms work best for different types of data.
          </p>
        </div>
      </div>
    </div>
  );
}
