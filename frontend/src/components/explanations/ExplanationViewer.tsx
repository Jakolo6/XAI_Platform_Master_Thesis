'use client';

import { useState } from 'react';
import { Brain, Sparkles, TrendingUp, AlertCircle } from 'lucide-react';
import FeatureImportanceChart from '../charts/FeatureImportanceChart';
import ShapWaterfallChart from '../charts/ShapWaterfallChart';

interface ExplanationViewerProps {
  explanation: {
    prediction?: {
      class: number;
      probability: number;
      label: string;
    };
    base_value?: number;
    feature_contributions?: Array<{
      feature: string;
      value: number;
      shap_value: number;
      abs_shap_value: number;
    }>;
    top_features?: Array<{
      feature: string;
      value: number;
      shap_value: number;
      abs_shap_value: number;
    }>;
    feature_importance?: Array<{
      feature: string;
      importance: number;
      rank: number;
    }>;
    num_samples?: number;
    num_features?: number;
  };
  type: 'instance' | 'global';
}

export default function ExplanationViewer({ explanation, type }: ExplanationViewerProps) {
  const [showAllFeatures, setShowAllFeatures] = useState(false);

  if (type === 'instance' && explanation.prediction) {
    // Individual instance explanation
    const topFeatures = showAllFeatures 
      ? explanation.feature_contributions || []
      : explanation.top_features || [];

    return (
      <div className="space-y-6">
        {/* SHAP Waterfall Chart */}
        <ShapWaterfallChart
          features={topFeatures}
          baseValue={explanation.base_value || 0}
          prediction={explanation.prediction}
          maxFeatures={showAllFeatures ? 20 : 10}
        />

        {/* Top Contributing Features Table */}
        <div className="bg-white rounded-lg border">
          <div className="px-6 py-4 border-b">
            <h3 className="text-lg font-semibold">Top Contributing Features</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rank</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Feature</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Value</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">SHAP Value</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Impact</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {topFeatures.slice(0, showAllFeatures ? undefined : 10).map((feature, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      #{index + 1}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {feature.feature}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {typeof feature.value === 'number' ? feature.value.toFixed(2) : feature.value}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className={`font-semibold ${feature.shap_value > 0 ? 'text-red-600' : 'text-green-600'}`}>
                        {feature.shap_value > 0 ? '+' : ''}{feature.shap_value.toFixed(4)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        feature.shap_value > 0 
                          ? 'bg-red-100 text-red-800' 
                          : 'bg-green-100 text-green-800'
                      }`}>
                        {feature.shap_value > 0 ? 'Increases Risk' : 'Decreases Risk'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {(explanation.feature_contributions?.length || 0) > 10 && (
            <div className="px-6 py-4 border-t bg-gray-50">
              <button
                onClick={() => setShowAllFeatures(!showAllFeatures)}
                className="text-blue-600 hover:text-blue-700 text-sm font-medium"
              >
                {showAllFeatures ? 'Show Less' : `Show All ${explanation.feature_contributions?.length} Features`}
              </button>
            </div>
          )}
        </div>

        {/* Explanation Summary */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <div className="flex items-start space-x-3">
            <Brain className="h-6 w-6 text-blue-600 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="font-semibold text-blue-900 mb-2">How to Read This Explanation</h4>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>• <strong>SHAP values</strong> show how much each feature contributed to the prediction</li>
                <li>• <strong>Positive values (red)</strong> increase the probability of fraud</li>
                <li>• <strong>Negative values (green)</strong> decrease the probability of fraud</li>
                <li>• Features are ranked by their absolute impact on the prediction</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Global feature importance
  const featureImportanceList = explanation.feature_importance || [];
  const topFeatures = showAllFeatures 
    ? featureImportanceList
    : featureImportanceList.slice(0, 20);

  return (
    <div className="space-y-6">
      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center justify-between mb-2">
            <div className="bg-blue-100 p-2 rounded-lg">
              <TrendingUp className="h-5 w-5 text-blue-600" />
            </div>
          </div>
          <div className="text-2xl font-bold text-gray-900">
            {explanation.num_features || 0}
          </div>
          <div className="text-sm text-gray-600">Total Features</div>
        </div>

        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center justify-between mb-2">
            <div className="bg-green-100 p-2 rounded-lg">
              <Sparkles className="h-5 w-5 text-green-600" />
            </div>
          </div>
          <div className="text-2xl font-bold text-gray-900">
            {topFeatures.length}
          </div>
          <div className="text-sm text-gray-600">Top Features Shown</div>
        </div>

        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center justify-between mb-2">
            <div className="bg-purple-100 p-2 rounded-lg">
              <Brain className="h-5 w-5 text-purple-600" />
            </div>
          </div>
          <div className="text-2xl font-bold text-gray-900">
            {explanation.num_samples?.toLocaleString() || 0}
          </div>
          <div className="text-sm text-gray-600">Samples Analyzed</div>
        </div>
      </div>

      {/* Feature Importance Chart */}
      <div className="bg-white rounded-lg border">
        <div className="px-6 py-4 border-b">
          <h3 className="text-lg font-semibold">Global Feature Importance</h3>
          <p className="text-sm text-gray-600 mt-1">
            Features ranked by their average impact across all predictions
          </p>
        </div>
        <div className="p-6">
          <FeatureImportanceChart 
            features={topFeatures} 
            maxFeatures={showAllFeatures ? 50 : 20}
          />
        </div>
        {(explanation.feature_importance?.length || 0) > 20 && (
          <div className="px-6 py-4 border-t bg-gray-50">
            <button
              onClick={() => setShowAllFeatures(!showAllFeatures)}
              className="text-blue-600 hover:text-blue-700 text-sm font-medium"
            >
              {showAllFeatures ? 'Show Top 20' : `Show All ${explanation.feature_importance?.length} Features`}
            </button>
          </div>
        )}
      </div>

      {/* Explanation Info */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <div className="flex items-start space-x-3">
          <AlertCircle className="h-6 w-6 text-blue-600 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="font-semibold text-blue-900 mb-2">Understanding Feature Importance</h4>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• <strong>Higher values</strong> indicate features that have more impact on predictions</li>
              <li>• Based on <strong>SHAP values</strong> calculated across {explanation.num_samples?.toLocaleString()} samples</li>
              <li>• Features at the top are the most important for fraud detection</li>
              <li>• This helps understand what the model learned from the data</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
