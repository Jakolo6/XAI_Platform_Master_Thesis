'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import Link from 'next/link';
import { useAuthStore } from '@/store/auth';
import { useModelsStore } from '@/store/models';
import { Brain, LogOut, ArrowLeft, Download, TrendingUp, Target, Zap, Sparkles } from 'lucide-react';
import { formatPercentage, formatMetric, formatDuration, getModelTypeLabel } from '@/lib/utils';
import MetricsChart from '@/components/charts/MetricsChart';
import ConfusionMatrixChart from '@/components/charts/ConfusionMatrixChart';
import ExplanationViewer from '@/components/explanations/ExplanationViewer';
import { explanationsAPI } from '@/lib/api';

export default function ModelDetailPage() {
  const router = useRouter();
  const params = useParams();
  const modelId = params.id as string;
  
  const { isAuthenticated, logout, user } = useAuthStore();
  const { selectedModel, selectedMetrics, fetchModelById, fetchModelMetrics, isLoading } = useModelsStore();
  
  const [explanation, setExplanation] = useState<any>(null);
  const [isGeneratingExplanation, setIsGeneratingExplanation] = useState(false);
  const [isGeneratingLime, setIsGeneratingLime] = useState(false);
  const [limeProgress, setLimeProgress] = useState<string>('');
  const [limeTaskId, setLimeTaskId] = useState<string | null>(null);
  const [explanationError, setExplanationError] = useState<string | null>(null);

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

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  const handleGenerateExplanation = async () => {
    setIsGeneratingExplanation(true);
    setExplanationError(null);
    
    try {
      console.log('Generating explanation for model:', modelId);
      const response = await explanationsAPI.generate(modelId, 'shap', {});
      console.log('Explanation started:', response.data);
      
      // Poll for completion
      const explanationId = response.data.id;
      let pollCount = 0;
      const maxPolls = 60; // 2 minutes at 2 second intervals
      
      const pollInterval = setInterval(async () => {
        try {
          pollCount++;
          console.log(`Polling attempt ${pollCount}/${maxPolls}...`);
          
          const result = await explanationsAPI.getById(explanationId);
          console.log('Poll result:', result.data.status);
          
          if (result.data.status === 'completed') {
            clearInterval(pollInterval);
            console.log('Explanation completed! Result:', result.data.result);
            const parsedResult = JSON.parse(result.data.result);
            console.log('Parsed result:', parsedResult);
            setExplanation(parsedResult);
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
          console.error('Polling error:', error);
          clearInterval(pollInterval);
          setExplanationError(error.response?.data?.detail || 'Failed to fetch explanation');
          setIsGeneratingExplanation(false);
        }
      }, 2000);
      
    } catch (error: any) {
      console.error('Generation error:', error);
      setExplanationError(error.response?.data?.detail || 'Failed to generate explanation');
      setIsGeneratingExplanation(false);
    }
  };

  const handleGenerateLime = async () => {
    setIsGeneratingLime(true);
    setExplanationError(null);
    setLimeProgress('Starting LIME generation...');
    
    try {
      console.log('Generating LIME explanation for model:', modelId);
      const response = await explanationsAPI.generate(modelId, 'lime', {});
      console.log('LIME explanation started:', response.data);
      
      const explanationId = response.data.id;
      setLimeTaskId(explanationId);
      setLimeProgress('LIME generation in progress... (0/15 min)');
      
      // Poll for completion
      let pollCount = 0;
      const maxPolls = 450; // 15 minutes at 2 second intervals
      const startTime = Date.now();
      
      const pollInterval = setInterval(async () => {
        try {
          pollCount++;
          const elapsed = Math.floor((Date.now() - startTime) / 1000 / 60); // minutes
          const remaining = Math.max(0, 15 - elapsed);
          
          setLimeProgress(`LIME generation in progress... (${elapsed}/15 min, ~${remaining} min remaining)`);
          
          const result = await explanationsAPI.getById(explanationId);
          console.log('LIME poll result:', result.data.status);
          
          if (result.data.status === 'completed') {
            clearInterval(pollInterval);
            setLimeProgress('LIME generation complete! ✅');
            setIsGeneratingLime(false);
            
            // Show success
            setTimeout(() => {
              setLimeProgress('');
              setLimeTaskId(null);
            }, 3000);
            
            console.log('LIME completed!');
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
          console.error('Polling error:', pollError);
        }
      }, 2000);
      
    } catch (error: any) {
      console.error('LIME generation error:', error);
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
                          width: `${Math.min(100, (parseInt(limeProgress.match(/\((\d+)\/15/)?.[1] || '0') / 15) * 100)}%` 
                        }}
                      ></div>
                    </div>
                    <div className="text-sm text-gray-600 space-y-1">
                      <p>• LIME analyzes 1,000 samples with perturbations</p>
                      <p>• This process takes approximately 15 minutes</p>
                      <p>• You can leave this page and come back later</p>
                      <p className="font-medium text-green-700">• Progress is saved automatically ✓</p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Explanation Section */}
            {explanation && (
              <div className="bg-white rounded-lg shadow-sm border">
                <div className="px-6 py-4 border-b">
                  <h2 className="text-xl font-bold text-gray-900">SHAP Explanation</h2>
                  <p className="text-sm text-gray-600 mt-1">
                    Understanding feature importance and model predictions
                  </p>
                </div>
                <div className="p-6">
                  <ExplanationViewer 
                    explanation={explanation} 
                    type="global"
                  />
                </div>
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
