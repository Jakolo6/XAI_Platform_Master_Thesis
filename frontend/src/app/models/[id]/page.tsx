/**
 * MODEL DETAIL PAGE
 * Route: /models/[id]
 * 
 * Detailed view of a single model.
 * Shows metrics, confusion matrix, and explanation generation.
 * Supports SHAP and LIME explanation methods.
 * Protected route - requires authentication.
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import Link from 'next/link';
import { useAuthStore } from '@/store/auth';
import { useModelsStore } from '@/store/models';
import { Brain, LogOut, ArrowLeft, Download, TrendingUp, Target, Zap, Sparkles, FileDown, Settings, BarChart3, PieChart } from 'lucide-react';
import { formatPercentage, formatMetric, formatDuration, getModelTypeLabel } from '@/lib/utils';
import MetricsChart from '@/components/charts/MetricsChart';
import ConfusionMatrixChart from '@/components/charts/ConfusionMatrixChart';
import ROCCurveChart from '@/components/charts/ROCCurveChart';
import PRCurveChart from '@/components/charts/PRCurveChart';
import ExplanationViewer from '@/components/explanations/ExplanationViewer';
import QualityMetrics from '@/components/explanations/QualityMetrics';
import { explanationsAPI } from '@/lib/api';
import { exportSHAPToCSV, exportLIMEToCSV } from '@/utils/export';

// Enable debug logging in development
const DEBUG = process.env.NODE_ENV === 'development';
const log = (...args: any[]) => DEBUG && console.log(...args);

export default function ModelDetailPage() {
  const router = useRouter();
  const params = useParams();
  const modelId = params.id as string;
  
  const { isAuthenticated, logout, user } = useAuthStore();
  const { selectedModel, selectedMetrics, fetchModelById, fetchModelMetrics, isLoading } = useModelsStore();
  
  const [shapExplanation, setShapExplanation] = useState<any>(null);
  const [limeExplanation, setLimeExplanation] = useState<any>(null);
  const [selectedMethod, setSelectedMethod] = useState<'shap' | 'lime'>('shap');
  const [isGeneratingExplanation, setIsGeneratingExplanation] = useState(false);
  const [isGeneratingLime, setIsGeneratingLime] = useState(false);
  const [limeProgress, setLimeProgress] = useState<string>('');
  const [limeTaskId, setLimeTaskId] = useState<string | null>(null);
  const [explanationError, setExplanationError] = useState<string | null>(null);
  const [qualityMetrics, setQualityMetrics] = useState<any>(null);
  const [isLoadingQuality, setIsLoadingQuality] = useState(false);
  const [showQualityMetrics, setShowQualityMetrics] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }
    if (modelId) {
      fetchModelById(modelId);
      fetchModelMetrics(modelId);
    }
  }, [isAuthenticated, modelId, router, fetchModelById, fetchModelMetrics]);

  /**
   * Handle user logout
   * Clears authentication state and redirects to home page
   */
  const handleLogout = () => {
    logout();
    router.push('/');
  };

  /**
   * Generate SHAP explanation for the current model
   * Polls for completion every 2 seconds for up to 2 minutes
   * Updates state with explanation results or error messages
   */
  const handleGenerateExplanation = async () => {
    setIsGeneratingExplanation(true);
    setExplanationError(null);
    
    try {
      log('Generating explanation for model:', modelId);
      const response = await explanationsAPI.generate(modelId, 'shap', {});
      log('Explanation started:', response.data);
      
      // Poll for completion
      const explanationId = response.data.id;
      let pollCount = 0;
      const maxPolls = 60; // 2 minutes at 2 second intervals
      
      const pollInterval = setInterval(async () => {
        try {
          pollCount++;
          log(`Polling attempt ${pollCount}/${maxPolls}...`);
          
          const result = await explanationsAPI.getById(explanationId);
          log('Poll result:', result.data.status);
          
          if (result.data.status === 'completed') {
            clearInterval(pollInterval);
            log('SHAP Explanation completed! Result:', result.data.result);
            const parsedResult = JSON.parse(result.data.result);
            log('Parsed result:', parsedResult);
            setShapExplanation(parsedResult);
            setSelectedMethod('shap');
            setIsGeneratingExplanation(false);
          } else if (result.data.status === 'failed') {
            clearInterval(pollInterval);
            setExplanationError('Explanation generation failed');
            setIsGeneratingExplanation(false);
          } else if (pollCount >= maxPolls) {
            clearInterval(pollInterval);
            setExplanationError('Explanation generation timed out');
            setIsGeneratingExplanation(false);
          }
        } catch (error: any) {
          log('Polling error:', error);
          clearInterval(pollInterval);
          setExplanationError(error.response?.data?.detail || 'Failed to fetch explanation');
          setIsGeneratingExplanation(false);
        }
      }, 2000);
      
    } catch (error: any) {
      log('Generation error:', error);
      setExplanationError(error.response?.data?.detail || 'Failed to generate explanation');
      setIsGeneratingExplanation(false);
    }
  };

  /**
   * Load quality metrics for current explanation
   */
  const loadQualityMetrics = async () => {
    const currentExplanation = selectedMethod === 'shap' ? shapExplanation : limeExplanation;
    if (!currentExplanation) return;

    setIsLoadingQuality(true);
    try {
      // Generate demo quality metrics based on method
      // In a real implementation, this would call the backend API
      const demoMetrics = {
        faithfulness: {
          monotonicity: selectedMethod === 'shap' ? 0.85 : 0.78,
          selectivity: selectedMethod === 'shap' ? 4.2 : 3.8,
        },
        robustness: {
          stability: selectedMethod === 'shap' ? 0.92 : 0.81,
          stability_std: selectedMethod === 'shap' ? 0.05 : 0.08,
        },
        complexity: {
          sparsity: selectedMethod === 'shap' ? 0.27 : 0.32,
          gini_coefficient: selectedMethod === 'shap' ? 0.73 : 0.68,
          effective_features: selectedMethod === 'shap' ? 15 : 18,
        },
        overall_quality: selectedMethod === 'shap' ? 0.85 : 0.78,
      };
      
      setQualityMetrics(demoMetrics);
    } catch (error) {
      log('Failed to load quality metrics:', error);
    } finally {
      setIsLoadingQuality(false);
    }
  };

  // Auto-load quality metrics when showing them
  useEffect(() => {
    if (showQualityMetrics && !qualityMetrics) {
      loadQualityMetrics();
    }
  }, [showQualityMetrics]);

  /**
   * Generate LIME explanation for the current model
   * LIME is optimized to run in 3-5 minutes with 200 samples
   * Provides real-time progress updates with visual feedback
   * Polls for completion every 2 seconds for up to 5 minutes
   */
  const handleGenerateLime = async () => {
    setIsGeneratingLime(true);
    setExplanationError(null);
    setLimeProgress('Starting LIME generation...');
    
    try {
      log('Generating LIME explanation for model:', modelId);
      const response = await explanationsAPI.generate(modelId, 'lime', {});
      log('LIME explanation started:', response.data);
      
      const explanationId = response.data.id;
      setLimeTaskId(explanationId);
      setLimeProgress('LIME generation in progress... (0/5 min)');
      
      // Poll for completion
      let pollCount = 0;
      const maxPolls = 150; // 5 minutes at 2 second intervals (safety buffer)
      const startTime = Date.now();
      
      const pollInterval = setInterval(async () => {
        try {
          pollCount++;
          const elapsed = Math.floor((Date.now() - startTime) / 1000 / 60); // minutes
          const remaining = Math.max(0, 5 - elapsed);
          
          setLimeProgress(`LIME generation in progress... (${elapsed}/5 min, ~${remaining} min remaining)`);
          
          const result = await explanationsAPI.getById(explanationId);
          log('LIME poll result:', result.data.status);
          
          if (result.data.status === 'completed') {
            clearInterval(pollInterval);
            setLimeProgress('LIME generation complete! ✅');
            
            // Parse and save LIME result
            const parsedResult = JSON.parse(result.data.result);
            setLimeExplanation(parsedResult);
            setSelectedMethod('lime');
            setIsGeneratingLime(false);
            
            // Show success
            setTimeout(() => {
              setLimeProgress('');
              setLimeTaskId(null);
            }, 3000);
            
            log('LIME completed!', parsedResult);
          } else if (result.data.status === 'failed') {
            clearInterval(pollInterval);
            setLimeProgress('');
            setIsGeneratingLime(false);
            setLimeTaskId(null);
            setExplanationError('LIME generation failed. Please try again.');
          } else if (pollCount >= maxPolls) {
            clearInterval(pollInterval);
            setLimeProgress('');
            setIsGeneratingLime(false);
            setLimeTaskId(null);
            setExplanationError('LIME generation timed out. Please check back later.');
          }
        } catch (pollError) {
          log('Polling error:', pollError);
        }
      }, 2000);
      
    } catch (error: any) {
      log('LIME generation error:', error);
      setExplanationError(error.response?.data?.detail || 'Failed to generate LIME explanation');
      setIsGeneratingLime(false);
      setLimeProgress('');
      setLimeTaskId(null);
    }
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
            href="/models"
            className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900 mb-4"
          >
            <ArrowLeft className="h-4 w-4 mr-1" />
            Back to Models
          </Link>
          
          {isLoading || !selectedModel ? (
            <div className="animate-pulse">
              <div className="h-8 bg-gray-200 rounded w-1/3 mb-2"></div>
              <div className="h-4 bg-gray-200 rounded w-1/4"></div>
            </div>
          ) : (
            <>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">{selectedModel.name}</h1>
              <div className="flex items-center space-x-4">
                <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                  {getModelTypeLabel(selectedModel.model_type)}
                </span>
                <span className="text-sm text-gray-600">Version {selectedModel.version}</span>
                <span className="text-sm text-gray-600">
                  Status: <span className="font-medium text-green-600">{selectedModel.status}</span>
                </span>
              </div>
            </>
          )}
        </div>

        {isLoading || !selectedMetrics ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-600">Loading model details...</p>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="bg-white rounded-lg shadow-sm border p-6">
                <div className="flex items-center justify-between mb-2">
                  <div className="bg-blue-100 p-2 rounded-lg">
                    <TrendingUp className="h-5 w-5 text-blue-600" />
                  </div>
                </div>
                <div className="text-2xl font-bold text-gray-900">
                  {formatPercentage(selectedMetrics.auc_roc)}
                </div>
                <div className="text-sm text-gray-600">AUC-ROC</div>
              </div>

              <div className="bg-white rounded-lg shadow-sm border p-6">
                <div className="flex items-center justify-between mb-2">
                  <div className="bg-green-100 p-2 rounded-lg">
                    <Target className="h-5 w-5 text-green-600" />
                  </div>
                </div>
                <div className="text-2xl font-bold text-gray-900">
                  {formatPercentage(selectedMetrics.f1_score)}
                </div>
                <div className="text-sm text-gray-600">F1 Score</div>
              </div>

              <div className="bg-white rounded-lg shadow-sm border p-6">
                <div className="flex items-center justify-between mb-2">
                  <div className="bg-purple-100 p-2 rounded-lg">
                    <Zap className="h-5 w-5 text-purple-600" />
                  </div>
                </div>
                <div className="text-2xl font-bold text-gray-900">
                  {formatPercentage(selectedMetrics.accuracy)}
                </div>
                <div className="text-sm text-gray-600">Accuracy</div>
              </div>

              <div className="bg-white rounded-lg shadow-sm border p-6">
                <div className="flex items-center justify-between mb-2">
                  <div className="bg-orange-100 p-2 rounded-lg">
                    <Target className="h-5 w-5 text-orange-600" />
                  </div>
                </div>
                <div className="text-2xl font-bold text-gray-900">
                  {formatPercentage(selectedMetrics.precision)}
                </div>
                <div className="text-sm text-gray-600">Precision</div>
              </div>
            </div>

            {/* Model Configuration & Hyperparameters */}
            {selectedModel && (
              <div className="bg-white rounded-lg shadow-sm border">
                <div className="px-6 py-4 border-b">
                  <div className="flex items-center">
                    <Settings className="h-5 w-5 text-blue-600 mr-2" />
                    <h2 className="text-xl font-bold text-gray-900">Model Configuration</h2>
                  </div>
                  <p className="text-sm text-gray-600 mt-1">Training parameters and hyperparameters used</p>
                </div>
                <div className="p-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Basic Info */}
                    <div className="space-y-4">
                      <h3 className="font-semibold text-gray-900 mb-3">Model Information</h3>
                      <div className="flex justify-between items-center py-2 border-b">
                        <span className="text-gray-600">Algorithm</span>
                        <span className="font-semibold text-blue-600">{getModelTypeLabel(selectedModel.model_type)}</span>
                      </div>
                      <div className="flex justify-between items-center py-2 border-b">
                        <span className="text-gray-600">Dataset</span>
                        <span className="font-semibold">{selectedModel.dataset_id}</span>
                      </div>
                      <div className="flex justify-between items-center py-2 border-b">
                        <span className="text-gray-600">Version</span>
                        <span className="font-semibold">{selectedModel.version}</span>
                      </div>
                      <div className="flex justify-between items-center py-2 border-b">
                        <span className="text-gray-600">Training Time</span>
                        <span className="font-semibold">{selectedModel.training_time_seconds ? formatDuration(selectedModel.training_time_seconds) : 'N/A'}</span>
                      </div>
                      <div className="flex justify-between items-center py-2">
                        <span className="text-gray-600">Model Size</span>
                        <span className="font-semibold">{selectedModel.model_size_mb ? `${selectedModel.model_size_mb.toFixed(2)} MB` : 'N/A'}</span>
                      </div>
                    </div>

                    {/* Hyperparameters */}
                    <div className="space-y-4">
                      <h3 className="font-semibold text-gray-900 mb-3">Hyperparameters</h3>
                      {selectedModel.hyperparameters && Object.keys(selectedModel.hyperparameters).length > 0 ? (
                        <div className="space-y-2">
                          {Object.entries(selectedModel.hyperparameters).map(([key, value]) => (
                            <div key={key} className="flex justify-between items-center py-2 border-b">
                              <span className="text-gray-600 text-sm">{key}</span>
                              <span className="font-mono text-sm font-semibold">{JSON.stringify(value)}</span>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="bg-gray-50 rounded-lg p-4 text-center">
                          <p className="text-gray-600 text-sm">Default hyperparameters used</p>
                          <p className="text-xs text-gray-500 mt-1">No custom parameters specified</p>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Training Configuration */}
                  {selectedModel.training_config && (
                    <div className="mt-6 pt-6 border-t">
                      <h3 className="font-semibold text-gray-900 mb-3">Training Configuration</h3>
                      <div className="bg-blue-50 rounded-lg p-4">
                        <pre className="text-xs text-gray-800 overflow-x-auto">
                          {JSON.stringify(selectedModel.training_config, null, 2)}
                        </pre>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Feature Importance */}
            {selectedModel?.feature_importance && Object.keys(selectedModel.feature_importance).length > 0 && (
              <div className="bg-white rounded-lg shadow-sm border">
                <div className="px-6 py-4 border-b">
                  <div className="flex items-center">
                    <BarChart3 className="h-5 w-5 text-purple-600 mr-2" />
                    <h2 className="text-xl font-bold text-gray-900">Feature Importance</h2>
                  </div>
                  <p className="text-sm text-gray-600 mt-1">Top features contributing to model predictions</p>
                </div>
                <div className="p-6">
                  <div className="space-y-3">
                    {Object.entries(selectedModel.feature_importance)
                      .sort(([, a], [, b]) => (b as number) - (a as number))
                      .slice(0, 15)
                      .map(([feature, importance], index) => (
                        <div key={feature} className="flex items-center gap-3">
                          <div className="w-8 text-right text-sm font-semibold text-gray-500">#{index + 1}</div>
                          <div className="flex-1">
                            <div className="flex justify-between items-center mb-1">
                              <span className="text-sm font-medium text-gray-900">{feature}</span>
                              <span className="text-sm font-semibold text-blue-600">
                                {((importance as number) * 100).toFixed(2)}%
                              </span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div
                                className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full transition-all"
                                style={{ width: `${(importance as number) * 100}%` }}
                              />
                            </div>
                          </div>
                        </div>
                      ))}
                  </div>
                  {Object.keys(selectedModel.feature_importance).length > 15 && (
                    <div className="mt-4 text-center text-sm text-gray-500">
                      Showing top 15 of {Object.keys(selectedModel.feature_importance).length} features
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Performance Chart */}
            <div className="bg-white rounded-lg shadow-sm border">
              <div className="px-6 py-4 border-b">
                <h2 className="text-xl font-bold text-gray-900">Performance Visualization</h2>
              </div>
              <div className="p-6">
                <MetricsChart metrics={selectedMetrics} />
              </div>
            </div>

            {/* Detailed Metrics */}
            <div className="bg-white rounded-lg shadow-sm border">
              <div className="px-6 py-4 border-b">
                <h2 className="text-xl font-bold text-gray-900">Performance Metrics</h2>
              </div>
              <div className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div className="flex justify-between items-center py-2 border-b">
                      <span className="text-gray-600">AUC-ROC</span>
                      <span className="font-semibold">{formatMetric(selectedMetrics.auc_roc)}</span>
                    </div>
                    <div className="flex justify-between items-center py-2 border-b">
                      <span className="text-gray-600">AUC-PR</span>
                      <span className="font-semibold">{formatMetric(selectedMetrics.auc_pr)}</span>
                    </div>
                    <div className="flex justify-between items-center py-2 border-b">
                      <span className="text-gray-600">F1 Score</span>
                      <span className="font-semibold">{formatMetric(selectedMetrics.f1_score)}</span>
                    </div>
                    <div className="flex justify-between items-center py-2 border-b">
                      <span className="text-gray-600">Precision</span>
                      <span className="font-semibold">{formatMetric(selectedMetrics.precision)}</span>
                    </div>
                    <div className="flex justify-between items-center py-2">
                      <span className="text-gray-600">Recall</span>
                      <span className="font-semibold">{formatMetric(selectedMetrics.recall)}</span>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div className="flex justify-between items-center py-2 border-b">
                      <span className="text-gray-600">Accuracy</span>
                      <span className="font-semibold">{formatMetric(selectedMetrics.accuracy)}</span>
                    </div>
                    <div className="flex justify-between items-center py-2 border-b">
                      <span className="text-gray-600">Log Loss</span>
                      <span className="font-semibold">{formatMetric(selectedMetrics.log_loss)}</span>
                    </div>
                    <div className="flex justify-between items-center py-2 border-b">
                      <span className="text-gray-600">Brier Score</span>
                      <span className="font-semibold">{formatMetric(selectedMetrics.brier_score)}</span>
                    </div>
                    <div className="flex justify-between items-center py-2 border-b">
                      <span className="text-gray-600">ECE</span>
                      <span className="font-semibold">{formatMetric(selectedMetrics.expected_calibration_error)}</span>
                    </div>
                    <div className="flex justify-between items-center py-2">
                      <span className="text-gray-600">MCE</span>
                      <span className="font-semibold">{formatMetric(selectedMetrics.maximum_calibration_error)}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Confusion Matrix Heatmap */}
            {selectedMetrics.confusion_matrix && (
              <div className="bg-white rounded-lg shadow-sm border">
                <div className="px-6 py-4 border-b">
                  <h2 className="text-xl font-bold text-gray-900">Confusion Matrix</h2>
                  <p className="text-sm text-gray-600 mt-1">Visual representation of prediction accuracy</p>
                </div>
                <div className="p-6">
                  <ConfusionMatrixChart confusionMatrix={selectedMetrics.confusion_matrix} />
                </div>
              </div>
            )}

            {/* ROC Curve */}
            {selectedMetrics.roc_curve && selectedMetrics.auc_roc && (
              <div className="bg-white rounded-lg shadow-sm border">
                <div className="px-6 py-4 border-b">
                  <h2 className="text-xl font-bold text-gray-900">ROC Analysis</h2>
                  <p className="text-sm text-gray-600 mt-1">Model discrimination ability across all thresholds</p>
                </div>
                <div className="p-6">
                  <ROCCurveChart 
                    rocCurve={selectedMetrics.roc_curve} 
                    aucScore={selectedMetrics.auc_roc}
                  />
                </div>
              </div>
            )}

            {/* Precision-Recall Curve */}
            {selectedMetrics.pr_curve && selectedMetrics.auc_pr && (
              <div className="bg-white rounded-lg shadow-sm border">
                <div className="px-6 py-4 border-b">
                  <h2 className="text-xl font-bold text-gray-900">Precision-Recall Analysis</h2>
                  <p className="text-sm text-gray-600 mt-1">Performance on imbalanced fraud detection task</p>
                </div>
                <div className="p-6">
                  <PRCurveChart 
                    prCurve={selectedMetrics.pr_curve} 
                    aucPR={selectedMetrics.auc_pr}
                    classBalance={selectedModel?.dataset_id === 'ieee-cis-fraud' ? { '0': 398867, '1': 14511 } : undefined}
                  />
                </div>
              </div>
            )}

            {/* Actions */}
            <div className="flex flex-wrap gap-3">
              <button
                onClick={handleGenerateExplanation}
                disabled={isGeneratingExplanation || (selectedModel?.model_type !== 'xgboost' && selectedModel?.model_type !== 'catboost' && selectedModel?.model_type !== 'lightgbm' && selectedModel?.model_type !== 'random_forest')}
                className="flex items-center px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Sparkles className="h-4 w-4 mr-2" />
                {isGeneratingExplanation ? 'Generating...' : 'Generate SHAP'}
              </button>
              <button
                onClick={handleGenerateLime}
                disabled={isGeneratingLime || (selectedModel?.model_type !== 'xgboost' && selectedModel?.model_type !== 'catboost' && selectedModel?.model_type !== 'lightgbm' && selectedModel?.model_type !== 'random_forest')}
                className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Sparkles className="h-4 w-4 mr-2" />
                {isGeneratingLime ? 'Generating...' : 'Generate LIME'}
              </button>
              <Link
                href={`/models/${modelId}/compare`}
                className="flex items-center px-4 py-2 bg-gradient-to-r from-blue-600 to-green-600 text-white rounded-lg hover:from-blue-700 hover:to-green-700"
              >
                <TrendingUp className="h-4 w-4 mr-2" />
                Compare Methods
              </Link>
              <button
                className="flex items-center px-4 py-2 bg-gray-400 text-white rounded-lg cursor-not-allowed"
                disabled
              >
                <Download className="h-4 w-4 mr-2" />
                Download Model
              </button>
            </div>

            {/* Method Switcher */}
            {(shapExplanation || limeExplanation) && (
              <div className="bg-white rounded-lg shadow p-4">
                <div className="flex items-center gap-4">
                  <span className="text-sm font-medium text-gray-700">View Explanation:</span>
                  <div className="flex gap-2">
                    <button
                      onClick={() => setSelectedMethod('shap')}
                      disabled={!shapExplanation}
                      className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                        selectedMethod === 'shap'
                          ? 'bg-purple-600 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed'
                      }`}
                    >
                      🔮 SHAP
                    </button>
                    <button
                      onClick={() => setSelectedMethod('lime')}
                      disabled={!limeExplanation}
                      className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                        selectedMethod === 'lime'
                          ? 'bg-green-600 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed'
                      }`}
                    >
                      🍋 LIME
                    </button>
                  </div>
                  {shapExplanation && limeExplanation && (
                    <span className="text-xs text-green-600 font-medium">
                      ✓ Both methods available
                    </span>
                  )}
                </div>
              </div>
            )}

            {/* LIME Progress Indicator */}
            {limeProgress && (
              <div className="bg-gradient-to-r from-green-50 to-blue-50 border-2 border-green-300 rounded-lg p-6">
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      🔬 LIME Explanation Generation
                    </h3>
                    <p className="text-gray-700 font-medium mb-3">
                      {limeProgress}
                    </p>
                    <div className="bg-white rounded-full h-3 overflow-hidden mb-3">
                      <div 
                        className="bg-gradient-to-r from-green-500 to-blue-500 h-full transition-all duration-500 ease-out"
                        style={{ 
                          width: `${Math.min(100, (parseInt(limeProgress.match(/\((\d+)\/5/)?.[1] || '0') / 5) * 100)}%` 
                        }}
                      ></div>
                    </div>
                    <div className="text-sm text-gray-600 space-y-1">
                      <p>• LIME analyzes 200 samples with perturbations (OPTIMIZED!)</p>
                      <p>• This process takes approximately 3-5 minutes ⚡</p>
                      <p>• You can leave this page and come back later</p>
                      <p className="font-medium text-green-700">• Progress is saved automatically ✓</p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Explanation Section */}
            {(shapExplanation || limeExplanation) && (
              <div className="bg-white rounded-lg shadow-sm border">
                <div className="px-6 py-4 border-b flex justify-between items-center">
                  <div>
                    <h2 className="text-xl font-bold text-gray-900"> {selectedMethod === 'shap' ? 'SHAP' : 'LIME'} Explanation </h2>
                    <p className="text-sm text-gray-600 mt-1">
                      Understanding feature importance and model predictions
                    </p>
                  </div>
                  <button
                    onClick={() => {
                      const explanation = selectedMethod === 'shap' ? shapExplanation : limeExplanation;
                      const modelName = selectedModel?.name || 'model';
                      if (selectedMethod === 'shap') {
                        exportSHAPToCSV(explanation, modelName);
                      } else {
                        exportLIMEToCSV(explanation, modelName);
                      }
                    }}
                    className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    <FileDown className="h-4 w-4 mr-2" />
                    Export CSV
                  </button>
                </div>
                <div className="p-6">
                  <ExplanationViewer 
                    explanation={selectedMethod === 'shap' ? shapExplanation : limeExplanation} 
                    type="global"
                  />
                </div>
              </div>
            )}

            {/* Quality Metrics Section */}
            {(shapExplanation || limeExplanation) && (
              <div className="bg-white rounded-lg shadow-sm border">
                <div className="px-6 py-4 border-b flex justify-between items-center">
                  <div>
                    <h2 className="text-xl font-bold text-gray-900">Explanation Quality Metrics</h2>
                    <p className="text-sm text-gray-600 mt-1">
                      Evaluate the quality of {selectedMethod === 'shap' ? 'SHAP' : 'LIME'} explanations
                    </p>
                  </div>
                  <button
                    onClick={() => setShowQualityMetrics(!showQualityMetrics)}
                    className="flex items-center px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                  >
                    <Sparkles className="h-4 w-4 mr-2" />
                    {showQualityMetrics ? 'Hide' : 'Show'} Quality Metrics
                  </button>
                </div>
                {showQualityMetrics && (
                  <div className="p-6">
                    {isLoadingQuality ? (
                      <div className="flex items-center justify-center py-12">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
                        <span className="ml-3 text-gray-600">Loading quality metrics...</span>
                      </div>
                    ) : qualityMetrics ? (
                      <QualityMetrics metrics={qualityMetrics} method={selectedMethod} />
                    ) : (
                      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
                        <p className="text-blue-800 mb-4">
                          Quality metrics provide insights into the reliability and interpretability of explanations.
                        </p>
                        <p className="text-sm text-blue-600">
                          Note: Quality metrics are computed using demo data for this prototype.
                        </p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Error Message */}
            {explanationError && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-red-800">{explanationError}</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
