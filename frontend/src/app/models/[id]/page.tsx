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
import { createClient } from '@/lib/supabase/client';
import { useModelsStore } from '@/store/models';
import type { User } from '@supabase/supabase-js';
import { ArrowLeft, Download, TrendingUp, Target, Zap, Sparkles, FileDown, Settings, BarChart3, PieChart, Info } from 'lucide-react';
import { formatPercentage, formatMetric, formatDuration, getModelTypeLabel } from '@/lib/utils';
import MetricsChart from '@/components/charts/MetricsChart';
import ConfusionMatrixChart from '@/components/charts/ConfusionMatrixChart';
import ROCCurveChart from '@/components/charts/ROCCurveChart';
import PRCurveChart from '@/components/charts/PRCurveChart';
import ExplanationViewer from '@/components/explanations/ExplanationViewer';
import QualityMetrics from '@/components/explanations/QualityMetrics';
import { explanationsAPI, reportsAPI } from '@/lib/api';
import { exportSHAPToCSV, exportLIMEToCSV } from '@/utils/export';

// Enable debug logging in development
const DEBUG = process.env.NODE_ENV === 'development';
const log = (...args: any[]) => DEBUG && console.log(...args);

export default function ModelDetailPage() {
  const router = useRouter();
  const params = useParams();
  const modelId = params.id as string;
  const supabase = createClient();
  
  const [user, setUser] = useState<User | null>(null);
  const { selectedModel, selectedMetrics, fetchModelById, fetchModelMetrics, isLoading } = useModelsStore();
  
  const [shapExplanation, setShapExplanation] = useState<any>(null);
  const [shapExplanationId, setShapExplanationId] = useState<string | null>(null);
  const [limeExplanation, setLimeExplanation] = useState<any>(null);
  const [limeExplanationId, setLimeExplanationId] = useState<string | null>(null);
  const [selectedMethod, setSelectedMethod] = useState<'shap' | 'lime'>('shap');
  const [explanationType, setExplanationType] = useState<'global' | 'local'>('global');
  const [localExplanation, setLocalExplanation] = useState<any>(null);
  const [sampleIndex, setSampleIndex] = useState<number>(0);
  const [isGeneratingLocal, setIsGeneratingLocal] = useState(false);
  const [isGeneratingExplanation, setIsGeneratingExplanation] = useState(false);
  const [isGeneratingLime, setIsGeneratingLime] = useState(false);
  const [limeProgress, setLimeProgress] = useState<string>('');
  const [limeTaskId, setLimeTaskId] = useState<string | null>(null);
  const [explanationError, setExplanationError] = useState<string | null>(null);
  const [qualityMetrics, setQualityMetrics] = useState<any>(null);
  const [isLoadingQuality, setIsLoadingQuality] = useState(false);
  const [showQualityMetrics, setShowQualityMetrics] = useState(false);

  useEffect(() => {
    // Get current user
    supabase.auth.getUser().then(({ data: { user } }) => {
      setUser(user);
      if (user && modelId) {
        fetchModelById(modelId);
        fetchModelMetrics(modelId);
        // Load existing explanations
        loadExistingExplanations();
      }
    });
  }, [modelId, fetchModelById, fetchModelMetrics]);

  // Debug logging
  useEffect(() => {
    if (selectedMetrics) {
      console.log('selectedMetrics:', selectedMetrics);
      console.log('auc_roc:', selectedMetrics.auc_roc);
      console.log('f1_score:', selectedMetrics.f1_score);
    }
  }, [selectedMetrics]);

  /**
   * Load existing explanations for the model
   */
  const loadExistingExplanations = async () => {
    if (!modelId) return;
    
    try {
      const response = await explanationsAPI.getByModel(modelId);
      const explanations = response.data;
      
      // Find SHAP and LIME explanations
      for (const exp of explanations) {
        if (exp.method === 'shap' && exp.status === 'completed') {
          setShapExplanation(exp.explanation_data || exp);
          setShapExplanationId(exp.id);
        } else if (exp.method === 'lime' && exp.status === 'completed') {
          setLimeExplanation(exp.explanation_data || exp);
          setLimeExplanationId(exp.id);
        }
      }
    } catch (error) {
      log('Failed to load existing explanations:', error);
    }
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
            setShapExplanationId(explanationId); // Store explanation ID
            setSelectedMethod('shap');
            setIsGeneratingExplanation(false);
            // Reload to get fresh data
            await loadExistingExplanations();
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
    const explanationId = selectedMethod === 'shap' ? shapExplanationId : limeExplanationId;
    if (!explanationId) {
      log('No explanation ID available for quality evaluation');
      return;
    }

    setIsLoadingQuality(true);
    try {
      log('Evaluating quality for explanation:', explanationId);
      const response = await explanationsAPI.evaluateQuality(explanationId);
      const metrics = response.data.quality_metrics;
      
      log('Quality metrics received:', metrics);
      setQualityMetrics(metrics);
    } catch (error: any) {
      log('Failed to load quality metrics:', error);
      const errorMsg = error.response?.data?.detail || error.message || 'Failed to load quality metrics';
      alert(`Backend Error: ${errorMsg}\n\nQuality metrics could not be loaded. Please ensure the backend is running.`);
      setQualityMetrics(null);
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
   * Generate local (instance-level) SHAP explanation for a specific sample
   */
  const handleGenerateLocalExplanation = async () => {
    if (!modelId) return;
    
    setIsGeneratingLocal(true);
    setExplanationError(null);
    
    try {
      const response = await explanationsAPI.generateLocal({
        model_id: modelId,
        sample_index: sampleIndex,
        method: 'shap'
      });
      
      setLocalExplanation(response.data.explanation);
      log('Local explanation generated:', response.data);
    } catch (error: any) {
      log('Local explanation error:', error);
      setExplanationError(error.response?.data?.detail || 'Failed to generate local explanation');
    } finally {
      setIsGeneratingLocal(false);
    }
  };

  /**
   * Export model performance report as CSV
   */
  const handleExportModelCSV = async () => {
    if (!modelId) return;
    
    try {
      const response = await reportsAPI.exportModelCSV(modelId);
      const blob = new Blob([response.data], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `model_${modelId}_${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      log('Failed to export model CSV:', error);
    }
  };

  /**
   * Export SHAP vs LIME comparison as JSON
   */
  const handleExportComparison = async () => {
    if (!modelId) return;
    
    try {
      const response = await reportsAPI.exportComparisonJSON(modelId);
      const blob = new Blob([response.data], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `comparison_${modelId}_${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      log('Failed to export comparison:', error);
    }
  };

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
            setLimeExplanationId(explanationId); // Store explanation ID
            setSelectedMethod('lime');
            setIsGeneratingLime(false);
            
            // Reload to get fresh data
            await loadExistingExplanations();
            
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

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">

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

            {/* Info Box for Global Explanations */}
            {!shapExplanation && !limeExplanation && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                <div className="flex items-start gap-3">
                  <Info className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
                  <div className="flex-1">
                    <h4 className="font-semibold text-blue-900 mb-1">Generate Global Explanations</h4>
                    <p className="text-sm text-blue-800 mb-2">
                      Global explanations show which features are most important for this model's predictions across the entire dataset.
                      These are required to use the <strong>Global View</strong> in the Explainable AI sandbox.
                    </p>
                    <ul className="text-sm text-blue-700 space-y-1 list-disc list-inside">
                      <li><strong>SHAP:</strong> Computes Shapley values - takes ~1-2 minutes for 100 samples</li>
                      <li><strong>LIME:</strong> Trains local surrogate models - takes ~3-5 minutes for 200 samples</li>
                      <li>Both run in the background - you can navigate away while they compute</li>
                    </ul>
                  </div>
                </div>
              </div>
            )}

            {/* Progress Indicators */}
            {(isGeneratingExplanation || isGeneratingLime) && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
                <div className="flex items-center gap-3">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-yellow-600"></div>
                  <div className="flex-1">
                    <p className="font-medium text-yellow-900">
                      {isGeneratingExplanation && 'Generating SHAP explanation...'}
                      {isGeneratingLime && 'Generating LIME explanation...'}
                    </p>
                    <p className="text-sm text-yellow-700">
                      This may take a few minutes. The page will update automatically when complete.
                    </p>
                    {limeProgress && (
                      <p className="text-sm text-yellow-600 mt-1 font-mono">{limeProgress}</p>
                    )}
                  </div>
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
                {isGeneratingExplanation ? 'Generating...' : shapExplanation ? 'Regenerate SHAP' : 'Generate SHAP'}
              </button>
              <button
                onClick={handleGenerateLime}
                disabled={isGeneratingLime || (selectedModel?.model_type !== 'xgboost' && selectedModel?.model_type !== 'catboost' && selectedModel?.model_type !== 'lightgbm' && selectedModel?.model_type !== 'random_forest')}
                className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Sparkles className="h-4 w-4 mr-2" />
                {isGeneratingLime ? 'Generating...' : limeExplanation ? 'Regenerate LIME' : 'Generate LIME'}
              </button>
              <Link
                href={`/models/${modelId}/compare`}
                className="flex items-center px-4 py-2 bg-gradient-to-r from-blue-600 to-green-600 text-white rounded-lg hover:from-blue-700 hover:to-green-700"
              >
                <TrendingUp className="h-4 w-4 mr-2" />
                Compare Methods
              </Link>
              <button
                onClick={handleExportModelCSV}
                className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
              >
                <Download className="h-4 w-4 mr-2" />
                Export Model Report
              </button>
              {shapExplanation && limeExplanation && (
                <button
                  onClick={handleExportComparison}
                  className="flex items-center px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
                >
                  <FileDown className="h-4 w-4 mr-2" />
                  Export Comparison
                </button>
              )}
            </div>

            {/* Feature Highlight Banner */}
            {(shapExplanation || limeExplanation) && (
              <div className="bg-gradient-to-r from-purple-50 to-pink-50 border-2 border-purple-200 rounded-lg p-4 mb-4">
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0">
                    <Sparkles className="h-6 w-6 text-purple-600" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-sm font-semibold text-purple-900 mb-1">
                      ✨ New: Global & Local Explanations
                    </h3>
                    <p className="text-xs text-purple-700">
                      <strong>Global:</strong> Average importance across all predictions • 
                      <strong> Local:</strong> Explain ONE specific prediction • 
                      Try entering a sample index below!
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Method Switcher */}
            {(shapExplanation || limeExplanation) && (
              <div className="bg-white rounded-lg shadow p-4 space-y-4">
                {/* Global/Local Toggle */}
                <div className="flex items-center gap-4 pb-4 border-b">
                  <span className="text-sm font-medium text-gray-700">Explanation Type:</span>
                  <div className="flex gap-2">
                    <button
                      onClick={() => setExplanationType('global')}
                      className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                        explanationType === 'global'
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      🌍 Global
                    </button>
                    <button
                      onClick={() => setExplanationType('local')}
                      className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                        explanationType === 'local'
                          ? 'bg-orange-600 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      🎯 Local
                    </button>
                  </div>
                  <span className="text-xs text-gray-500">
                    {explanationType === 'global' 
                      ? 'Average importance across all predictions' 
                      : 'Explanation for one specific prediction'}
                  </span>
                </div>

                {/* Method Switcher (only for global) */}
                {explanationType === 'global' && (
                  <div className="flex items-center gap-4">
                    <span className="text-sm font-medium text-gray-700">Method:</span>
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
                )}

                {/* Local Explanation Controls */}
                {explanationType === 'local' && (
                  <div className="flex items-center gap-4">
                    <span className="text-sm font-medium text-gray-700">Sample Index:</span>
                    <input
                      type="number"
                      min="0"
                      max="999"
                      value={sampleIndex}
                      onChange={(e) => setSampleIndex(parseInt(e.target.value) || 0)}
                      className="px-3 py-2 border border-gray-300 rounded-lg w-24"
                    />
                    <button
                      onClick={handleGenerateLocalExplanation}
                      disabled={isGeneratingLocal}
                      className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:opacity-50 text-sm font-medium"
                    >
                      {isGeneratingLocal ? 'Generating...' : 'Generate Local SHAP'}
                    </button>
                    <span className="text-xs text-gray-500">
                      Enter a sample index (0-999) from the test set
                    </span>
                  </div>
                )}
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
                  {explanationType === 'global' ? (
                    <ExplanationViewer 
                      explanation={selectedMethod === 'shap' ? shapExplanation : limeExplanation} 
                      type="global"
                    />
                  ) : localExplanation ? (
                    <div className="space-y-6">
                      {/* Prediction Info */}
                      <div className="bg-gradient-to-r from-orange-50 to-yellow-50 border border-orange-200 rounded-lg p-4">
                        <div className="grid grid-cols-3 gap-4">
                          <div>
                            <div className="text-sm text-gray-600">Prediction</div>
                            <div className="text-2xl font-bold text-gray-900">
                              {localExplanation.prediction.class === 1 ? 'Fraud' : 'Not Fraud'}
                            </div>
                          </div>
                          <div>
                            <div className="text-sm text-gray-600">Probability</div>
                            <div className="text-2xl font-bold text-orange-600">
                              {(localExplanation.prediction.probability * 100).toFixed(1)}%
                            </div>
                          </div>
                          <div>
                            <div className="text-sm text-gray-600">True Label</div>
                            <div className="text-2xl font-bold text-gray-900">
                              {localExplanation.true_label === 1 ? 'Fraud' : 'Not Fraud'}
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* SHAP Force Plot Data */}
                      <div>
                        <h3 className="text-lg font-semibold mb-4">Feature Contributions (SHAP Values)</h3>
                        <div className="space-y-2">
                          {Object.entries(localExplanation.shap_values)
                            .sort(([, a]: any, [, b]: any) => Math.abs(b) - Math.abs(a))
                            .slice(0, 15)
                            .map(([feature, value]: any) => (
                              <div key={feature} className="flex items-center gap-2">
                                <div className="w-32 text-sm font-medium text-gray-700 truncate">
                                  {feature}
                                </div>
                                <div className="flex-1 h-8 bg-gray-100 rounded relative overflow-hidden">
                                  <div
                                    className={`absolute h-full ${value > 0 ? 'bg-red-500' : 'bg-blue-500'}`}
                                    style={{
                                      width: `${Math.min(Math.abs(value) * 100, 100)}%`,
                                      left: value > 0 ? '50%' : `${50 - Math.min(Math.abs(value) * 100, 50)}%`
                                    }}
                                  />
                                  <div className="absolute inset-0 flex items-center justify-center">
                                    <span className="text-xs font-medium text-gray-700">
                                      {value.toFixed(4)}
                                    </span>
                                  </div>
                                </div>
                                <div className="w-24 text-sm text-gray-600">
                                  = {localExplanation.feature_values[feature]?.toFixed(2) || 'N/A'}
                                </div>
                              </div>
                            ))}
                        </div>
                      </div>

                      {/* Base Value Info */}
                      <div className="text-sm text-gray-600">
                        <strong>Base value:</strong> {localExplanation.base_value.toFixed(4)} 
                        <span className="ml-2 text-xs">(Expected model output)</span>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center py-12 text-gray-500">
                      <p>Select a sample index and click "Generate Local SHAP" to see instance-level explanations</p>
                    </div>
                  )}
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
                        <p className="text-sm text-gray-600 mb-4">
                          Quality metrics provide insights into the reliability and interpretability of explanations.
                          These are computed from real backend evaluation.
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
