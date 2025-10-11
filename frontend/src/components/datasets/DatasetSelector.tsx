'use client';

import { useState, useEffect } from 'react';
import { Database, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import { datasetsAPI } from '@/lib/api';

interface Dataset {
  id: string;
  name: string;
  display_name?: string;
  description: string;
  total_samples: number;  // Maps to total_rows in backend
  num_features: number;   // Maps to total_columns in backend
  status: string;
  tags: string[];
  fraud_count?: number;
  non_fraud_count?: number;
  fraud_percentage?: number;
}

interface DatasetSelectorProps {
  onSelect: (id: string) => void;
  selectedId?: string;
}

export function DatasetSelector({ onSelect, selectedId }: DatasetSelectorProps) {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDatasets();
  }, []);

  const fetchDatasets = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Real API call to backend
      const response = await datasetsAPI.getAll();
      const data = response.data;
      
      // Show all datasets (pending and completed)
      setDatasets(data);
    } catch (err: any) {
      console.error('Failed to fetch datasets:', err);
      setError(err.response?.data?.detail || 'Failed to load datasets. Make sure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
        <span className="ml-3 text-gray-600">Loading datasets...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
        <AlertCircle className="h-8 w-8 text-red-600 mx-auto mb-2" />
        <p className="text-red-800">{error}</p>
        <button
          onClick={fetchDatasets}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
        >
          Retry
        </button>
      </div>
    );
  }

  if (datasets.length === 0) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-12 text-center">
        <Database className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-gray-900 mb-2">No Datasets Available</h3>
        <p className="text-gray-600">Process a dataset to get started.</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {datasets.map(dataset => (
        <div
          key={dataset.id}
          onClick={() => onSelect(dataset.name)}
          className={`
            relative p-6 rounded-lg border-2 cursor-pointer transition-all
            hover:shadow-lg hover:scale-[1.02]
            ${selectedId === dataset.name 
              ? 'border-blue-500 bg-blue-50 shadow-md ring-2 ring-blue-200' 
              : 'border-gray-200 hover:border-blue-300 bg-white'
            }
          `}
        >
          {/* Status Badge */}
          <div className="absolute top-4 right-4">
            {dataset.status === 'completed' ? (
              <CheckCircle2 className="h-5 w-5 text-green-500" />
            ) : (
              <AlertCircle className="h-5 w-5 text-yellow-500" />
            )}
          </div>

          {/* Icon */}
          <Database className={`h-10 w-10 mb-4 ${
            selectedId === dataset.name ? 'text-blue-600' : 'text-gray-600'
          }`} />

          {/* Title */}
          <h3 className="text-lg font-bold text-gray-900 mb-2 pr-8">
            {dataset.display_name}
          </h3>

          {/* Description */}
          <p className="text-sm text-gray-600 mb-4 line-clamp-2">
            {dataset.description}
          </p>

          {/* Stats */}
          <div className="space-y-2 mb-4">
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Samples:</span>
              <span className="font-medium text-gray-900">
                {dataset.total_samples?.toLocaleString() || 0}
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Features:</span>
              <span className="font-medium text-gray-900">{dataset.num_features || 0}</span>
            </div>
            {dataset.fraud_percentage !== null && dataset.fraud_percentage !== undefined && (
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Fraud Rate:</span>
                <span className="font-medium text-gray-900">
                  {dataset.fraud_percentage.toFixed(1)}%
                </span>
              </div>
            )}
          </div>

          {/* Tags */}
          {dataset.tags && dataset.tags.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {dataset.tags.slice(0, 3).map(tag => (
                <span
                  key={tag}
                  className={`px-2 py-1 text-xs rounded ${
                    selectedId === dataset.name
                      ? 'bg-blue-100 text-blue-700'
                      : 'bg-gray-100 text-gray-700'
                  }`}
                >
                  {tag}
                </span>
              ))}
              {dataset.tags.length > 3 && (
                <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
                  +{dataset.tags.length - 3}
                </span>
              )}
            </div>
          )}

          {/* Selected Indicator */}
          {selectedId === dataset.name && (
            <div className="absolute inset-0 border-2 border-blue-500 rounded-lg pointer-events-none" />
          )}
        </div>
      ))}
    </div>
  );
}
