'use client';

import { useState } from 'react';
import { DatasetSelector } from '@/components/datasets/DatasetSelector';
import { Plus, Download, RefreshCw, Info } from 'lucide-react';
import { datasetsAPI } from '@/lib/api';

export default function DatasetsPage() {
  const [selectedDataset, setSelectedDataset] = useState<string>('');
  const [processing, setProcessing] = useState(false);

  const handleProcess = async (datasetId: string) => {
    setProcessing(true);
    try {
      // Real API call to backend
      const response = await datasetsAPI.preprocess(datasetId);
      
      if (response.status === 200) {
        alert(`Dataset processing started for: ${datasetId}\n\nCheck the datasets page for progress.`);
      }
    } catch (error: any) {
      console.error('Failed to process dataset:', error);
      const errorMsg = error.response?.data?.detail || 'Failed to start processing. Dataset may already be processed or backend is not running.';
      alert(errorMsg);
    } finally {
      setProcessing(false);
    }
  };

  const handleRefresh = () => {
    window.location.reload();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Datasets</h1>
            <p className="text-gray-600 mt-2">
              Manage datasets for model training and evaluation
            </p>
          </div>

          <div className="flex gap-3">
            <button
              onClick={handleRefresh}
              className="flex items-center px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <RefreshCw className="h-5 w-5 mr-2" />
              Refresh
            </button>
            <button
              className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Plus className="h-5 w-5 mr-2" />
              Add Dataset
            </button>
          </div>
        </div>

        {/* Info Banner */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-8 flex items-start">
          <Info className="h-5 w-5 text-blue-600 mr-3 mt-0.5 flex-shrink-0" />
          <div className="text-sm text-blue-800">
            <p className="font-medium mb-1">Multi-Dataset Research Platform</p>
            <p>
              Select a dataset to view details, or process a new dataset for model training.
              Datasets are configured in <code className="bg-blue-100 px-1 rounded">config/datasets.yaml</code>
            </p>
          </div>
        </div>

        {/* Dataset Selector */}
        <div className="mb-8">
          <DatasetSelector
            onSelect={setSelectedDataset}
            selectedId={selectedDataset}
          />
        </div>

        {/* Actions Panel */}
        {selectedDataset && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Actions</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Process Dataset */}
              <button
                onClick={() => handleProcess(selectedDataset)}
                disabled={processing}
                className="flex flex-col items-center p-6 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Download className="h-8 w-8 text-blue-600 mb-3" />
                <span className="font-medium text-gray-900 mb-1">
                  {processing ? 'Processing...' : 'Process Dataset'}
                </span>
                <span className="text-sm text-gray-600 text-center">
                  Download and preprocess data
                </span>
              </button>

              {/* Train Model */}
              <button
                onClick={() => window.location.href = `/models/train?dataset=${selectedDataset}`}
                className="flex flex-col items-center p-6 border-2 border-gray-200 rounded-lg hover:border-green-500 hover:bg-green-50 transition-all"
              >
                <svg className="h-8 w-8 text-green-600 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                <span className="font-medium text-gray-900 mb-1">Train Model</span>
                <span className="text-sm text-gray-600 text-center">
                  Start model training
                </span>
              </button>

              {/* View Details */}
              <button
                onClick={() => window.location.href = `/datasets/${selectedDataset}`}
                className="flex flex-col items-center p-6 border-2 border-gray-200 rounded-lg hover:border-purple-500 hover:bg-purple-50 transition-all"
              >
                <Info className="h-8 w-8 text-purple-600 mb-3" />
                <span className="font-medium text-gray-900 mb-1">View Details</span>
                <span className="text-sm text-gray-600 text-center">
                  See dataset information
                </span>
              </button>
            </div>

            {/* Quick Stats */}
            <div className="mt-6 pt-6 border-t border-gray-200">
              <h3 className="text-sm font-medium text-gray-700 mb-3">Quick Commands</h3>
              <div className="bg-gray-50 rounded-lg p-4 font-mono text-sm">
                <div className="text-gray-600 mb-2"># Process dataset:</div>
                <div className="text-gray-900">python scripts/process_dataset.py {selectedDataset}</div>
                
                <div className="text-gray-600 mt-4 mb-2"># Train model:</div>
                <div className="text-gray-900">python scripts/train_model_simple.py {selectedDataset} xgboost</div>
              </div>
            </div>
          </div>
        )}

        {/* Help Section */}
        <div className="mt-8 bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Getting Started</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">1. Process a Dataset</h3>
              <p className="text-sm text-gray-600">
                Select a dataset and click "Process Dataset" to download and preprocess the data.
                This will create train/validation/test splits.
              </p>
            </div>
            
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">2. Train Models</h3>
              <p className="text-sm text-gray-600">
                Once processed, train multiple models (XGBoost, LightGBM, Random Forest, etc.)
                on the dataset to compare performance.
              </p>
            </div>
            
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">3. Generate Explanations</h3>
              <p className="text-sm text-gray-600">
                Use SHAP or LIME to generate explanations for your trained models
                and understand feature importance.
              </p>
            </div>
            
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">4. Compare Results</h3>
              <p className="text-sm text-gray-600">
                View benchmarks to compare model performance across different datasets
                and identify the best approaches.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
