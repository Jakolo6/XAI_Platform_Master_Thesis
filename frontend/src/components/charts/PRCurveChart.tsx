/**
 * PRECISION-RECALL CURVE CHART COMPONENT
 * 
 * Displays Precision-Recall (PR) curve
 * Particularly useful for imbalanced datasets
 * Shows the trade-off between Precision and Recall
 */

'use client';

import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts';

interface PRCurveData {
  precision: number[];
  recall: number[];
  thresholds: number[];
}

interface PRCurveChartProps {
  prCurve: PRCurveData;
  aucPR: number;
  classBalance?: { [key: string]: number };
}

export default function PRCurveChart({ prCurve, aucPR, classBalance }: PRCurveChartProps) {
  // Transform data for Recharts
  const chartData = prCurve.recall.map((recall, index) => ({
    recall: recall,
    precision: prCurve.precision[index],
    threshold: prCurve.thresholds[index]
  }));

  // Calculate baseline (random classifier for imbalanced data)
  let baseline = 0.5;
  if (classBalance) {
    const total = Object.values(classBalance).reduce((a, b) => a + b, 0);
    const positives = classBalance['1'] || 0;
    baseline = positives / total;
  }

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="text-sm font-semibold text-gray-900 mb-1">PR Point</p>
          <p className="text-xs text-gray-600">
            <span className="font-medium">Recall:</span> {(payload[0].payload.recall * 100).toFixed(2)}%
          </p>
          <p className="text-xs text-gray-600">
            <span className="font-medium">Precision:</span> {(payload[0].payload.precision * 100).toFixed(2)}%
          </p>
          {payload[0].payload.threshold !== undefined && (
            <p className="text-xs text-gray-600">
              <span className="font-medium">Threshold:</span> {payload[0].payload.threshold.toFixed(4)}
            </p>
          )}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full">
      {/* Header with AUC-PR Score */}
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Precision-Recall Curve</h3>
          <p className="text-sm text-gray-600">Optimal for Imbalanced Datasets</p>
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold text-purple-600">
            {(aucPR * 100).toFixed(2)}%
          </div>
          <div className="text-xs text-gray-600">AUC-PR Score</div>
        </div>
      </div>

      {/* Chart */}
      <ResponsiveContainer width="100%" height={400}>
        <LineChart margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="recall"
            type="number"
            domain={[0, 1]}
            tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
            label={{ value: 'Recall (Sensitivity)', position: 'insideBottom', offset: -5 }}
            stroke="#6b7280"
          />
          <YAxis
            dataKey="precision"
            type="number"
            domain={[0, 1]}
            tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
            label={{ value: 'Precision', angle: -90, position: 'insideLeft' }}
            stroke="#6b7280"
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          
          {/* Baseline reference line */}
          <ReferenceLine
            y={baseline}
            stroke="#9ca3af"
            strokeWidth={2}
            strokeDasharray="5 5"
            label={{
              value: `Baseline (${(baseline * 100).toFixed(1)}%)`,
              position: 'right',
              fill: '#6b7280',
              fontSize: 12
            }}
          />
          
          {/* PR Curve */}
          <Line
            data={chartData}
            dataKey="precision"
            stroke="#9333ea"
            strokeWidth={3}
            dot={false}
            name={`PR Curve (AUC = ${aucPR.toFixed(3)})`}
            legendType="line"
          />
        </LineChart>
      </ResponsiveContainer>

      {/* Interpretation Guide */}
      <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-3">
        <div className="bg-purple-50 border border-purple-200 rounded-lg p-3">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
            <span className="text-xs font-semibold text-purple-900">High Precision</span>
          </div>
          <p className="text-xs text-purple-700 mt-1">Few false positives, high confidence in positive predictions</p>
        </div>
        <div className="bg-green-50 border border-green-200 rounded-lg p-3">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span className="text-xs font-semibold text-green-900">High Recall</span>
          </div>
          <p className="text-xs text-green-700 mt-1">Few false negatives, catches most positive cases</p>
        </div>
      </div>

      {/* Additional Info */}
      <div className="mt-4 bg-purple-50 border border-purple-200 rounded-lg p-4">
        <h4 className="text-sm font-semibold text-purple-900 mb-2">📊 Why PR Curve for Fraud Detection?</h4>
        <ul className="text-xs text-purple-800 space-y-1">
          <li>• <strong>Imbalanced Data:</strong> Fraud cases are rare (~3.5% in this dataset)</li>
          <li>• <strong>Focus on Positives:</strong> PR curve emphasizes performance on the minority class</li>
          <li>• <strong>Business Impact:</strong> Balance between catching fraud (recall) and avoiding false alarms (precision)</li>
          <li>• <strong>Baseline:</strong> Random classifier would achieve {(baseline * 100).toFixed(1)}% precision</li>
          <li>• <strong>Your Model:</strong> {aucPR >= baseline * 2 ? 'Significantly outperforms baseline! 🎯' : aucPR >= baseline * 1.5 ? 'Good improvement over baseline! 👍' : 'Consider optimization for better performance'}</li>
        </ul>
      </div>
    </div>
  );
}
