/**
 * ROC CURVE CHART COMPONENT
 * 
 * Displays Receiver Operating Characteristic (ROC) curve
 * Shows the trade-off between True Positive Rate and False Positive Rate
 * Includes AUC score and diagonal reference line
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

interface ROCCurveData {
  fpr: number[];
  tpr: number[];
  thresholds: number[];
}

interface ROCCurveChartProps {
  rocCurve: ROCCurveData;
  aucScore: number;
}

export default function ROCCurveChart({ rocCurve, aucScore }: ROCCurveChartProps) {
  // Transform data for Recharts
  const chartData = rocCurve.fpr.map((fpr, index) => ({
    fpr: fpr,
    tpr: rocCurve.tpr[index],
    threshold: rocCurve.thresholds[index]
  }));

  // Add diagonal reference line data
  const diagonalData = [
    { fpr: 0, tpr: 0 },
    { fpr: 1, tpr: 1 }
  ];

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="text-sm font-semibold text-gray-900 mb-1">ROC Point</p>
          <p className="text-xs text-gray-600">
            <span className="font-medium">FPR:</span> {(payload[0].payload.fpr * 100).toFixed(2)}%
          </p>
          <p className="text-xs text-gray-600">
            <span className="font-medium">TPR:</span> {(payload[0].payload.tpr * 100).toFixed(2)}%
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
      {/* Header with AUC Score */}
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">ROC Curve</h3>
          <p className="text-sm text-gray-600">Receiver Operating Characteristic</p>
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold text-blue-600">
            {(aucScore * 100).toFixed(2)}%
          </div>
          <div className="text-xs text-gray-600">AUC-ROC Score</div>
        </div>
      </div>

      {/* Chart */}
      <ResponsiveContainer width="100%" height={400}>
        <LineChart margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="fpr"
            type="number"
            domain={[0, 1]}
            tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
            label={{ value: 'False Positive Rate', position: 'insideBottom', offset: -5 }}
            stroke="#6b7280"
          />
          <YAxis
            dataKey="tpr"
            type="number"
            domain={[0, 1]}
            tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
            label={{ value: 'True Positive Rate', angle: -90, position: 'insideLeft' }}
            stroke="#6b7280"
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          
          {/* Diagonal reference line (random classifier) */}
          <Line
            data={diagonalData}
            dataKey="tpr"
            stroke="#9ca3af"
            strokeWidth={2}
            strokeDasharray="5 5"
            dot={false}
            name="Random Classifier"
            legendType="line"
          />
          
          {/* ROC Curve */}
          <Line
            data={chartData}
            dataKey="tpr"
            stroke="#3b82f6"
            strokeWidth={3}
            dot={false}
            name={`ROC Curve (AUC = ${aucScore.toFixed(3)})`}
            legendType="line"
          />
        </LineChart>
      </ResponsiveContainer>

      {/* Interpretation Guide */}
      <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-3">
        <div className="bg-green-50 border border-green-200 rounded-lg p-3">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span className="text-xs font-semibold text-green-900">Excellent</span>
          </div>
          <p className="text-xs text-green-700 mt-1">AUC &gt; 0.90</p>
        </div>
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
            <span className="text-xs font-semibold text-blue-900">Good</span>
          </div>
          <p className="text-xs text-blue-700 mt-1">0.80 &lt; AUC ≤ 0.90</p>
        </div>
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
            <span className="text-xs font-semibold text-yellow-900">Fair</span>
          </div>
          <p className="text-xs text-yellow-700 mt-1">0.70 &lt; AUC ≤ 0.80</p>
        </div>
      </div>

      {/* Additional Info */}
      <div className="mt-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="text-sm font-semibold text-blue-900 mb-2">📊 Understanding ROC Curve</h4>
        <ul className="text-xs text-blue-800 space-y-1">
          <li>• <strong>Perfect Model:</strong> Curve hugs the top-left corner (AUC = 1.0)</li>
          <li>• <strong>Random Model:</strong> Follows the diagonal line (AUC = 0.5)</li>
          <li>• <strong>Trade-off:</strong> Higher TPR means more true positives detected, but may increase false positives</li>
          <li>• <strong>Your Model:</strong> {aucScore >= 0.9 ? 'Excellent discrimination ability! 🎯' : aucScore >= 0.8 ? 'Good performance! 👍' : 'Fair performance, consider optimization'}</li>
        </ul>
      </div>
    </div>
  );
}
