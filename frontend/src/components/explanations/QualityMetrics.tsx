'use client';

import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Legend, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Cell } from 'recharts';
import { CheckCircle2, AlertCircle, TrendingUp, Zap } from 'lucide-react';

interface QualityMetrics {
  faithfulness: {
    monotonicity: number;
    selectivity: number;
  };
  robustness: {
    stability: number;
    stability_std: number;
  };
  complexity: {
    sparsity: number;
    gini_coefficient: number;
    effective_features: number;
  };
  overall_quality: number;
}

interface QualityMetricsProps {
  metrics: QualityMetrics;
  method: 'shap' | 'lime';
}

export default function QualityMetrics({ metrics, method }: QualityMetricsProps) {
  const methodColor = method === 'shap' ? '#3B82F6' : '#10B981';
  const methodName = method.toUpperCase();

  // Prepare radar chart data
  const radarData = [
    {
      metric: 'Monotonicity',
      value: metrics.faithfulness.monotonicity * 100,
      fullMark: 100,
    },
    {
      metric: 'Selectivity',
      value: Math.min(metrics.faithfulness.selectivity * 20, 100), // Scale down
      fullMark: 100,
    },
    {
      metric: 'Stability',
      value: metrics.robustness.stability * 100,
      fullMark: 100,
    },
    {
      metric: 'Simplicity',
      value: (1 - metrics.complexity.sparsity) * 100,
      fullMark: 100,
    },
    {
      metric: 'Concentration',
      value: metrics.complexity.gini_coefficient * 100,
      fullMark: 100,
    },
  ];

  // Prepare bar chart data
  const barData = [
    {
      name: 'Faithfulness',
      score: (metrics.faithfulness.monotonicity + Math.min(metrics.faithfulness.selectivity / 5, 1)) / 2,
    },
    {
      name: 'Robustness',
      score: metrics.robustness.stability,
    },
    {
      name: 'Complexity',
      score: 1 - metrics.complexity.sparsity,
    },
  ];

  // Get quality level
  const getQualityLevel = (score: number) => {
    if (score >= 0.8) return { label: 'Excellent', color: 'text-green-600', bg: 'bg-green-100' };
    if (score >= 0.6) return { label: 'Good', color: 'text-blue-600', bg: 'bg-blue-100' };
    if (score >= 0.4) return { label: 'Fair', color: 'text-yellow-600', bg: 'bg-yellow-100' };
    return { label: 'Poor', color: 'text-red-600', bg: 'bg-red-100' };
  };

  const qualityLevel = getQualityLevel(metrics.overall_quality);

  return (
    <div className="space-y-6">
      {/* Overall Quality Score */}
      <div className="bg-white rounded-lg shadow-lg p-6 border-2" style={{ borderColor: methodColor }}>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold text-gray-900">
            {methodName} Explanation Quality
          </h3>
          <div className={`px-4 py-2 rounded-full ${qualityLevel.bg}`}>
            <span className={`font-semibold ${qualityLevel.color}`}>
              {qualityLevel.label}
            </span>
          </div>
        </div>

        <div className="flex items-center justify-center py-8">
          <div className="text-center">
            <div className="text-6xl font-bold" style={{ color: methodColor }}>
              {(metrics.overall_quality * 100).toFixed(1)}
            </div>
            <div className="text-gray-600 mt-2">Overall Quality Score</div>
            <div className="text-sm text-gray-500 mt-1">out of 100</div>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4 mt-6">
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-gray-900">
              {(metrics.faithfulness.monotonicity * 100).toFixed(0)}
            </div>
            <div className="text-sm text-gray-600 mt-1">Faithfulness</div>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-gray-900">
              {(metrics.robustness.stability * 100).toFixed(0)}
            </div>
            <div className="text-sm text-gray-600 mt-1">Robustness</div>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-gray-900">
              {((1 - metrics.complexity.sparsity) * 100).toFixed(0)}
            </div>
            <div className="text-sm text-gray-600 mt-1">Simplicity</div>
          </div>
        </div>
      </div>

      {/* Radar Chart */}
      <div className="bg-white rounded-lg shadow p-6">
        <h4 className="text-lg font-semibold text-gray-900 mb-4">Quality Dimensions</h4>
        <ResponsiveContainer width="100%" height={400}>
          <RadarChart data={radarData}>
            <PolarGrid />
            <PolarAngleAxis dataKey="metric" />
            <PolarRadiusAxis angle={90} domain={[0, 100]} />
            <Radar
              name={methodName}
              dataKey="value"
              stroke={methodColor}
              fill={methodColor}
              fillOpacity={0.6}
            />
            <Legend />
          </RadarChart>
        </ResponsiveContainer>
      </div>

      {/* Detailed Metrics */}
      <div className="bg-white rounded-lg shadow p-6">
        <h4 className="text-lg font-semibold text-gray-900 mb-4">Detailed Metrics</h4>
        
        <div className="space-y-4">
          {/* Faithfulness */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="font-medium text-gray-700">Faithfulness</span>
              <CheckCircle2 className="w-5 h-5 text-green-500" />
            </div>
            <div className="space-y-2 ml-4">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Monotonicity:</span>
                <span className="font-medium">{(metrics.faithfulness.monotonicity * 100).toFixed(1)}%</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Selectivity:</span>
                <span className="font-medium">{metrics.faithfulness.selectivity.toFixed(2)}</span>
              </div>
            </div>
          </div>

          {/* Robustness */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="font-medium text-gray-700">Robustness</span>
              <Zap className="w-5 h-5 text-blue-500" />
            </div>
            <div className="space-y-2 ml-4">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Stability:</span>
                <span className="font-medium">{(metrics.robustness.stability * 100).toFixed(1)}%</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Stability STD:</span>
                <span className="font-medium">{metrics.robustness.stability_std.toFixed(3)}</span>
              </div>
            </div>
          </div>

          {/* Complexity */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="font-medium text-gray-700">Complexity</span>
              <TrendingUp className="w-5 h-5 text-purple-500" />
            </div>
            <div className="space-y-2 ml-4">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Sparsity:</span>
                <span className="font-medium">{(metrics.complexity.sparsity * 100).toFixed(1)}%</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Gini Coefficient:</span>
                <span className="font-medium">{metrics.complexity.gini_coefficient.toFixed(3)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Effective Features:</span>
                <span className="font-medium">{metrics.complexity.effective_features.toFixed(0)}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Interpretation Guide */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h5 className="font-semibold text-blue-900 mb-2">📊 Interpretation Guide</h5>
        <ul className="space-y-1 text-sm text-blue-800">
          <li>• <strong>Faithfulness:</strong> How well the explanation reflects the model's behavior</li>
          <li>• <strong>Robustness:</strong> Stability of explanations under small perturbations</li>
          <li>• <strong>Complexity:</strong> Simplicity and interpretability (fewer features = better)</li>
          <li>• <strong>Overall Score:</strong> Weighted average (40% + 30% + 30%)</li>
        </ul>
      </div>
    </div>
  );
}
