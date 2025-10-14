/**
 * REPORTS PAGE
 * Route: /reports
 * 
 * Central hub for exporting research data and generating reports
 * Allows users to download CSV/JSON exports for thesis documentation
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { FileDown, Download, FileText, Database, BarChart3, Sparkles, Loader2, CheckCircle2 } from 'lucide-react';
import { reportsAPI, researchAPI } from '@/lib/api';

export const dynamic = 'force-dynamic';

export default function ReportsPage() {
  const router = useRouter();
  const [models, setModels] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [exportStatus, setExportStatus] = useState<{ [key: string]: 'idle' | 'loading' | 'success' }>({});

  useEffect(() => {
    fetchModels();
  }, []);

  const fetchModels = async () => {
    setIsLoading(true);
    try {
      const response = await researchAPI.getLeaderboard();
      // Get unique models (remove duplicates from SHAP/LIME entries)
      const uniqueModels = response.data.models.reduce((acc: any[], model: any) => {
        const modelId = model.id || model.model_id;
        if (!acc.find(m => (m.id || m.model_id) === modelId)) {
          acc.push(model);
        }
        return acc;
      }, []);
      setModels(uniqueModels);
    } catch (error) {
      console.error('Failed to fetch models:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleExport = async (type: string, modelId?: string) => {
    const key = `${type}-${modelId || 'all'}`;
    setExportStatus(prev => ({ ...prev, [key]: 'loading' }));

    try {
      let response;
      let filename;

      switch (type) {
        case 'model':
          response = await reportsAPI.exportModelCSV(modelId!);
          filename = `model_${modelId}_${new Date().toISOString().split('T')[0]}.csv`;
          break;
        case 'comparison':
          response = await reportsAPI.exportComparisonJSON(modelId!);
          filename = `comparison_${modelId}_${new Date().toISOString().split('T')[0]}.json`;
          break;
        case 'leaderboard':
          response = await reportsAPI.exportLeaderboardCSV();
          filename = `leaderboard_${new Date().toISOString().split('T')[0]}.csv`;
          break;
        default:
          return;
      }

      // Download file
      const blob = new Blob([response.data], { 
        type: type === 'comparison' ? 'application/json' : 'text/csv' 
      });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      setExportStatus(prev => ({ ...prev, [key]: 'success' }));
      setTimeout(() => {
        setExportStatus(prev => ({ ...prev, [key]: 'idle' }));
      }, 2000);
    } catch (error) {
      console.error('Export failed:', error);
      setExportStatus(prev => ({ ...prev, [key]: 'idle' }));
      alert('Export failed. Please try again.');
    }
  };

  // Auth is handled by middleware

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <div className="bg-white border-b shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex items-center gap-4 mb-4">
            <div className="p-3 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl">
              <FileText className="h-8 w-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Research Reports & Exports
              </h1>
              <p className="text-gray-600 mt-1">
                Download data and reports for your thesis documentation
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Quick Export Section */}
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-purple-600" />
            Quick Exports
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button
              onClick={() => handleExport('leaderboard')}
              disabled={exportStatus['leaderboard-all'] === 'loading'}
              className="flex items-center justify-between p-4 border-2 border-blue-200 rounded-lg hover:border-blue-400 hover:bg-blue-50 transition-all disabled:opacity-50"
            >
              <div className="flex items-center gap-3">
                <Database className="h-6 w-6 text-blue-600" />
                <div className="text-left">
                  <div className="font-semibold text-gray-900">Full Leaderboard</div>
                  <div className="text-xs text-gray-600">All models CSV</div>
                </div>
              </div>
              {exportStatus['leaderboard-all'] === 'loading' ? (
                <Loader2 className="h-5 w-5 animate-spin text-blue-600" />
              ) : exportStatus['leaderboard-all'] === 'success' ? (
                <CheckCircle2 className="h-5 w-5 text-green-600" />
              ) : (
                <Download className="h-5 w-5 text-gray-400" />
              )}
            </button>

            <div className="flex items-center justify-between p-4 border-2 border-gray-200 rounded-lg bg-gray-50">
              <div className="flex items-center gap-3">
                <BarChart3 className="h-6 w-6 text-gray-400" />
                <div className="text-left">
                  <div className="font-semibold text-gray-700">Quality Metrics</div>
                  <div className="text-xs text-gray-500">Coming soon</div>
                </div>
              </div>
            </div>

            <div className="flex items-center justify-between p-4 border-2 border-gray-200 rounded-lg bg-gray-50">
              <div className="flex items-center gap-3">
                <FileText className="h-6 w-6 text-gray-400" />
                <div className="text-left">
                  <div className="font-semibold text-gray-700">Study Results</div>
                  <div className="text-xs text-gray-500">Coming soon</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Individual Model Reports */}
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Individual Model Reports
          </h2>
          
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
            </div>
          ) : models.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <Database className="h-12 w-12 mx-auto mb-4 text-gray-300" />
              <p>No models found. Train a model first!</p>
            </div>
          ) : (
            <div className="space-y-3">
              {models.map((model) => (
                <div
                  key={model.id || model.model_id}
                  className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50"
                >
                  <div className="flex-1">
                    <div className="font-medium text-gray-900">{model.model_name}</div>
                    <div className="text-sm text-gray-600">
                      {model.model_type} • {model.dataset_id}
                      {model.auc_roc && ` • AUC-ROC: ${model.auc_roc.toFixed(3)}`}
                    </div>
                  </div>
                  <div className="flex gap-2">
                    {(() => {
                      const modelId = model.id || model.model_id;
                      return (
                        <>
                          <button
                            onClick={() => handleExport('model', modelId)}
                            disabled={exportStatus[`model-${modelId}`] === 'loading'}
                            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 text-sm"
                          >
                            {exportStatus[`model-${modelId}`] === 'loading' ? (
                              <Loader2 className="h-4 w-4 animate-spin" />
                            ) : exportStatus[`model-${modelId}`] === 'success' ? (
                              <CheckCircle2 className="h-4 w-4" />
                            ) : (
                              <FileDown className="h-4 w-4" />
                            )}
                            Model CSV
                          </button>
                          <button
                            onClick={() => handleExport('comparison', modelId)}
                            disabled={exportStatus[`comparison-${modelId}`] === 'loading'}
                            className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 text-sm"
                          >
                            {exportStatus[`comparison-${modelId}`] === 'loading' ? (
                              <Loader2 className="h-4 w-4 animate-spin" />
                            ) : exportStatus[`comparison-${modelId}`] === 'success' ? (
                              <CheckCircle2 className="h-4 w-4" />
                            ) : (
                              <FileDown className="h-4 w-4" />
                            )}
                            Comparison CSV
                          </button>
                        </>
                      );
                    })()}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Export Guide */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="font-semibold text-blue-900 mb-3">📊 Export Guide</h3>
          <ul className="space-y-2 text-sm text-blue-800">
            <li><strong>Model CSV:</strong> Performance metrics, feature importance, training details</li>
            <li><strong>Comparison JSON:</strong> SHAP vs LIME side-by-side for analysis</li>
            <li><strong>Leaderboard CSV:</strong> All models with metrics for thesis tables</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
