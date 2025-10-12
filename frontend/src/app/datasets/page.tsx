'use client';

export const dynamic = 'force-dynamic';

import { useState, useEffect } from 'react';
import {
  Database,
  Download,
  CheckCircle,
  Loader2,
  BarChart3,
  AlertCircle,
  TrendingUp,
  PieChart as PieChartIcon
} from 'lucide-react';
import axios from 'axios';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line
} from 'recharts';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

interface DatasetStatus {
  downloaded: boolean;
  processed: boolean;
  n_samples?: number;
  n_features?: number;
  train_size?: number;
  val_size?: number;
  test_size?: number;
}

interface EDAStats {
  distributions: Record<string, any>;
  correlations: Record<string, any>;
  missing_values: Record<string, number>;
  target_distribution: {
    class_0: number;
    class_1: number;
  };
}

export default function HomeCreditDatasetPage() {
  const [status, setStatus] = useState<DatasetStatus>({
    downloaded: false,
    processed: false
  });
  const [edaStats, setEdaStats] = useState<EDAStats | null>(null);
  const [isDownloading, setIsDownloading] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    checkDatasetStatus();
  }, []);

  const checkDatasetStatus = async () => {
    try {
      // First check status endpoint
      const statusResponse = await axios.get(`${API_BASE}/datasets/home-credit/status`);
      
      if (statusResponse.data.ready) {
        // Data is in Supabase, load it
        const edaResponse = await axios.get(`${API_BASE}/datasets/home-credit/eda/home-credit-default-risk`);
        
        if (edaResponse.data) {
          setStatus({
            downloaded: true,
            processed: true,
            n_samples: edaResponse.data.n_samples,
            n_features: edaResponse.data.n_features,
            train_size: edaResponse.data.train_size,
            val_size: edaResponse.data.val_size,
            test_size: edaResponse.data.test_size
          });
          
          setEdaStats({
            distributions: edaResponse.data.eda_stats?.distributions || {},
            correlations: edaResponse.data.eda_stats?.correlations || {},
            missing_values: edaResponse.data.eda_stats?.missing_values || {},
            target_distribution: edaResponse.data.target_distribution || { class_0: 0, class_1: 0 }
          });
          
          console.log('✅ Dataset loaded from Supabase!');
        }
      } else if (statusResponse.data.needs_preprocessing) {
        // Files in R2 but not processed
        setStatus({
          downloaded: true,
          processed: false
        });
        console.log('⚠️ Files in R2, but not processed yet. Click "Preprocess Dataset"');
      } else {
        // Need to download
        setStatus({
          downloaded: false,
          processed: false
        });
        console.log('📥 Need to download dataset first');
      }
    } catch (error) {
      console.log('❌ Error checking status:', error);
    }
  };

  const handleDownload = async () => {
    setIsDownloading(true);
    setError(null);
    
    try {
      await axios.post(`${API_BASE}/datasets/home-credit/download`);
      setStatus(prev => ({ ...prev, downloaded: true }));
      alert('Dataset downloaded successfully! Now preprocessing...');
      await handlePreprocess();
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to download dataset');
    } finally {
      setIsDownloading(false);
    }
  };

  const handlePreprocess = async () => {
    setIsProcessing(true);
    setError(null);
    
    try {
      await axios.post(`${API_BASE}/datasets/home-credit/preprocess`);
      
      // Wait a moment for Supabase to save
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Refresh data from Supabase
      await checkDatasetStatus();
      
      alert('Dataset preprocessed and saved to Supabase! You can refresh anytime to see the data.');
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to preprocess dataset');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50">
      {/* Header */}
      <div className="bg-white border-b shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center space-x-4">
            <div className="p-3 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl">
              <Database className="h-8 w-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Home Credit Default Risk Dataset
              </h1>
              <p className="text-gray-600 mt-1">
                Kaggle Competition Dataset for Credit Risk Assessment
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="flex items-center space-x-2">
              <AlertCircle className="h-5 w-5 text-red-600" />
              <p className="text-red-800">{error}</p>
            </div>
          </div>
        )}

        {/* Data Preparation Checklist */}
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            Data Preparation Steps
          </h2>
          
          <div className="space-y-3">
            <div className="flex items-center space-x-3">
              {status.downloaded ? (
                <CheckCircle className="h-5 w-5 text-green-600" />
              ) : (
                <div className="h-5 w-5 rounded-full border-2 border-gray-300" />
              )}
              <span className={status.downloaded ? 'text-green-900 font-medium' : 'text-gray-600'}>
                Dataset Downloaded from Kaggle
              </span>
            </div>
            
            <div className="flex items-center space-x-3">
              {status.processed ? (
                <CheckCircle className="h-5 w-5 text-green-600" />
              ) : (
                <div className="h-5 w-5 rounded-full border-2 border-gray-300" />
              )}
              <span className={status.processed ? 'text-green-900 font-medium' : 'text-gray-600'}>
                Cleaning done (NaN handling, encoding)
              </span>
            </div>
            
            <div className="flex items-center space-x-3">
              {status.processed ? (
                <CheckCircle className="h-5 w-5 text-green-600" />
              ) : (
                <div className="h-5 w-5 rounded-full border-2 border-gray-300" />
              )}
              <span className={status.processed ? 'text-green-900 font-medium' : 'text-gray-600'}>
                Feature engineering (scaling, one-hot encoding)
              </span>
            </div>
            
            <div className="flex items-center space-x-3">
              {status.processed ? (
                <CheckCircle className="h-5 w-5 text-green-600" />
              ) : (
                <div className="h-5 w-5 rounded-full border-2 border-gray-300" />
              )}
              <span className={status.processed ? 'text-green-900 font-medium' : 'text-gray-600'}>
                Train/Validation/Test split (70/15/15)
              </span>
            </div>
            
            <div className="flex items-center space-x-3">
              {status.processed ? (
                <CheckCircle className="h-5 w-5 text-green-600" />
              ) : (
                <div className="h-5 w-5 rounded-full border-2 border-gray-300" />
              )}
              <span className={status.processed ? 'text-green-900 font-medium' : 'text-gray-600'}>
                Stored dataset version in Supabase
              </span>
            </div>
          </div>

          {!status.downloaded && (
            <button
              onClick={handleDownload}
              disabled={isDownloading}
              className="mt-6 flex items-center space-x-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
            >
              {isDownloading ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin" />
                  <span>Downloading...</span>
                </>
              ) : (
                <>
                  <Download className="h-5 w-5" />
                  <span>Download Dataset</span>
                </>
              )}
            </button>
          )}

          {status.downloaded && !status.processed && (
            <button
              onClick={handlePreprocess}
              disabled={isProcessing}
              className="mt-6 flex items-center space-x-2 px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50"
            >
              {isProcessing ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin" />
                  <span>Processing...</span>
                </>
              ) : (
                <>
                  <BarChart3 className="h-5 w-5" />
                  <span>Preprocess Dataset</span>
                </>
              )}
            </button>
          )}
        </div>

        {/* Dataset Statistics */}
        {status.processed && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <div className="text-sm text-gray-600 mb-1">Total Samples</div>
              <div className="text-3xl font-bold text-gray-900">
                {status.n_samples?.toLocaleString()}
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <div className="text-sm text-gray-600 mb-1">Features</div>
              <div className="text-3xl font-bold text-gray-900">
                {status.n_features}
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <div className="text-sm text-gray-600 mb-1">Train / Val / Test</div>
              <div className="text-lg font-bold text-gray-900">
                {status.train_size?.toLocaleString()} / {status.val_size?.toLocaleString()} / {status.test_size?.toLocaleString()}
              </div>
            </div>
          </div>
        )}

        {/* EDA Visualizations */}
        {edaStats && (
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center space-x-2">
              <TrendingUp className="h-6 w-6 text-indigo-600" />
              <span>Exploratory Data Analysis</span>
            </h2>
            
            {/* Target Distribution with Charts */}
            <div className="mb-8">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">
                Target Distribution (Default Risk)
              </h3>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Stats Cards */}
                <div className="space-y-4">
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <div className="text-sm text-green-700 mb-1">No Default (Class 0)</div>
                    <div className="text-2xl font-bold text-green-900">
                      {edaStats.target_distribution?.class_0?.toLocaleString()}
                    </div>
                    <div className="text-xs text-green-600 mt-1">
                      {((edaStats.target_distribution?.class_0 / (edaStats.target_distribution?.class_0 + edaStats.target_distribution?.class_1)) * 100).toFixed(1)}%
                    </div>
                  </div>
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <div className="text-sm text-red-700 mb-1">Default (Class 1)</div>
                    <div className="text-2xl font-bold text-red-900">
                      {edaStats.target_distribution?.class_1?.toLocaleString()}
                    </div>
                    <div className="text-xs text-red-600 mt-1">
                      {((edaStats.target_distribution?.class_1 / (edaStats.target_distribution?.class_0 + edaStats.target_distribution?.class_1)) * 100).toFixed(1)}%
                    </div>
                  </div>
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <div className="text-sm text-blue-700 mb-1">Class Imbalance Ratio</div>
                    <div className="text-2xl font-bold text-blue-900">
                      {(edaStats.target_distribution?.class_0 / edaStats.target_distribution?.class_1).toFixed(2)}:1
                    </div>
                    <div className="text-xs text-blue-600 mt-1">
                      Imbalanced dataset - consider SMOTE or class weights
                    </div>
                  </div>
                </div>
                
                {/* Pie Chart */}
                <div className="bg-gray-50 rounded-lg p-4">
                  <ResponsiveContainer width="100%" height={250}>
                    <PieChart>
                      <Pie
                        data={[
                          { name: 'No Default', value: edaStats.target_distribution?.class_0 || 0, color: '#10b981' },
                          { name: 'Default', value: edaStats.target_distribution?.class_1 || 0, color: '#ef4444' }
                        ]}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        <Cell fill="#10b981" />
                        <Cell fill="#ef4444" />
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>

            {/* Feature Distributions */}
            <div className="mb-8">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">
                Key Feature Statistics
              </h3>
              
              {/* Feature Distribution Chart */}
              <div className="bg-gray-50 rounded-lg p-4 mb-6">
                <h4 className="text-sm font-medium text-gray-700 mb-3">Feature Mean Values (Top 10)</h4>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart
                    data={Object.entries(edaStats.distributions || {}).slice(0, 10).map(([feature, stats]: [string, any]) => ({
                      feature: feature.length > 20 ? feature.substring(0, 20) + '...' : feature,
                      mean: stats.mean,
                      std: stats.std
                    }))}
                    margin={{ top: 5, right: 30, left: 20, bottom: 60 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="feature" angle={-45} textAnchor="end" height={100} />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="mean" fill="#6366f1" name="Mean" />
                    <Bar dataKey="std" fill="#8b5cf6" name="Std Dev" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              
              {/* Feature Statistics Table */}
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Feature
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Mean
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Std Dev
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Min / Max
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Range
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {Object.entries(edaStats.distributions || {}).slice(0, 10).map(([feature, stats]: [string, any]) => (
                      <tr key={feature} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {feature}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                          {stats.mean?.toFixed(2)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                          {stats.std?.toFixed(2)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                          {stats.min?.toFixed(2)} / {stats.max?.toFixed(2)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                          {(stats.max - stats.min).toFixed(2)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Missing Values Summary */}
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-4">
                Missing Values Summary
              </h3>
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm text-gray-700">
                  All missing values have been handled during preprocessing:
                </p>
                <ul className="mt-2 space-y-1 text-sm text-gray-600">
                  <li>• Numerical features: Filled with median values</li>
                  <li>• Categorical features: Filled with mode values</li>
                  <li>• All features encoded and scaled for model training</li>
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
