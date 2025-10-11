/**
 * QUALITY METRICS RADAR CHART
 * 
 * Displays explanation quality metrics in a radar/spider chart
 * Compares SHAP vs LIME across multiple dimensions
 * Used for XAI evaluation and comparison
 */

'use client';

import React from 'react';
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Legend,
  Tooltip
} from 'recharts';

interface QualityMetrics {
  faithfulness: number;
  robustness: number;
  complexity: number;
  stability: number;
  sparsity: number;
}

interface QualityMetricsRadarProps {
  shapMetrics?: QualityMetrics;
  limeMetrics?: QualityMetrics;
  title?: string;
}

export default function QualityMetricsRadar({ 
  shapMetrics, 
  limeMetrics,
  title = "Explanation Quality Comparison"
}: QualityMetricsRadarProps) {
  
  // Transform metrics into radar chart format
  const data = [
    {
      metric: 'Faithfulness',
      SHAP: shapMetrics?.faithfulness || 0,
      LIME: limeMetrics?.faithfulness || 0,
      fullMark: 1.0
    },
    {
      metric: 'Robustness',
      SHAP: shapMetrics?.robustness || 0,
      LIME: limeMetrics?.robustness || 0,
      fullMark: 1.0
    },
    {
      metric: 'Complexity',
      SHAP: shapMetrics?.complexity || 0,
      LIME: limeMetrics?.complexity || 0,
      fullMark: 1.0
    },
    {
      metric: 'Stability',
      SHAP: shapMetrics?.stability || 0,
      LIME: limeMetrics?.stability || 0,
      fullMark: 1.0
    },
    {
      metric: 'Sparsity',
      SHAP: shapMetrics?.sparsity || 0,
      LIME: limeMetrics?.sparsity || 0,
      fullMark: 1.0
    }
  ];

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-gray-900 border border-gray-700 rounded-lg p-3 shadow-xl">
          <p className="text-sm font-semibold text-white mb-2">{payload[0].payload.metric}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} className="text-xs" style={{ color: entry.color }}>
              {entry.name}: {(entry.value * 100).toFixed(1)}%
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{title}</h3>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Comparing explanation methods across quality dimensions
        </p>
      </div>

      <ResponsiveContainer width="100%" height={400}>
        <RadarChart data={data}>
          <PolarGrid stroke="#374151" />
          <PolarAngleAxis 
            dataKey="metric" 
            tick={{ fill: '#6b7280', fontSize: 12 }}
          />
          <PolarRadiusAxis 
            angle={90} 
            domain={[0, 1]} 
            tick={{ fill: '#6b7280', fontSize: 10 }}
            tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
          />
          
          {shapMetrics && (
            <Radar
              name="SHAP"
              dataKey="SHAP"
              stroke="#3b82f6"
              fill="#3b82f6"
              fillOpacity={0.3}
              strokeWidth={2}
            />
          )}
          
          {limeMetrics && (
            <Radar
              name="LIME"
              dataKey="LIME"
              stroke="#f97316"
              fill="#f97316"
              fillOpacity={0.3}
              strokeWidth={2}
            />
          )}
          
          <Legend 
            wrapperStyle={{ paddingTop: '20px' }}
            iconType="circle"
          />
          <Tooltip content={<CustomTooltip />} />
        </RadarChart>
      </ResponsiveContainer>

      {/* Metric Descriptions */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-3">
        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-3">
          <h4 className="text-xs font-semibold text-blue-900 dark:text-blue-300 mb-1">
            Faithfulness
          </h4>
          <p className="text-xs text-blue-700 dark:text-blue-400">
            How accurately the explanation reflects the model's behavior
          </p>
        </div>
        
        <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-3">
          <h4 className="text-xs font-semibold text-green-900 dark:text-green-300 mb-1">
            Robustness
          </h4>
          <p className="text-xs text-green-700 dark:text-green-400">
            Consistency of explanations across similar inputs
          </p>
        </div>
        
        <div className="bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg p-3">
          <h4 className="text-xs font-semibold text-purple-900 dark:text-purple-300 mb-1">
            Complexity
          </h4>
          <p className="text-xs text-purple-700 dark:text-purple-400">
            Simplicity and interpretability of the explanation
          </p>
        </div>
        
        <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-3">
          <h4 className="text-xs font-semibold text-yellow-900 dark:text-yellow-300 mb-1">
            Stability
          </h4>
          <p className="text-xs text-yellow-700 dark:text-yellow-400">
            Low variance in explanations for similar predictions
          </p>
        </div>
      </div>
    </div>
  );
}
