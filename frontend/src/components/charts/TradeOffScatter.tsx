/**
 * TRADE-OFF SCATTER PLOT
 * 
 * Visualizes the trade-off between model performance (AUC) and explanation quality
 * Shows Pareto frontier for optimal models
 * Compares SHAP vs LIME methods
 */

'use client';

import React from 'react';
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
  Label
} from 'recharts';

interface ModelPoint {
  model_id: string;
  model_name: string;
  model_type: string;
  auc_roc: number;
  quality_score: number;
  method: 'SHAP' | 'LIME';
  dataset?: string;
}

interface TradeOffScatterProps {
  data: ModelPoint[];
  title?: string;
  showParetoFrontier?: boolean;
}

export default function TradeOffScatter({ 
  data, 
  title = "Performance vs Interpretability Trade-off",
  showParetoFrontier = true
}: TradeOffScatterProps) {
  
  // Separate SHAP and LIME data
  const shapData = data.filter(d => d.method === 'SHAP');
  const limeData = data.filter(d => d.method === 'LIME');

  // Calculate Pareto frontier (simplified - top-right boundary)
  const calculateParetoFrontier = (points: ModelPoint[]) => {
    const sorted = [...points].sort((a, b) => b.auc_roc - a.auc_roc);
    const frontier: ModelPoint[] = [];
    let maxQuality = -Infinity;
    
    for (const point of sorted) {
      if (point.quality_score > maxQuality) {
        frontier.push(point);
        maxQuality = point.quality_score;
      }
    }
    
    return frontier.sort((a, b) => a.auc_roc - b.auc_roc);
  };

  const paretoFrontier = showParetoFrontier ? calculateParetoFrontier(data) : [];

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-gray-900 border border-gray-700 rounded-lg p-4 shadow-xl">
          <p className="text-sm font-semibold text-white mb-2">{data.model_name}</p>
          <div className="space-y-1">
            <p className="text-xs text-gray-300">
              <span className="font-medium">Type:</span> {data.model_type}
            </p>
            <p className="text-xs text-gray-300">
              <span className="font-medium">Method:</span> {data.method}
            </p>
            {data.dataset && (
              <p className="text-xs text-gray-300">
                <span className="font-medium">Dataset:</span> {data.dataset}
              </p>
            )}
            <div className="border-t border-gray-700 mt-2 pt-2">
              <p className="text-xs text-blue-400">
                <span className="font-medium">AUC-ROC:</span> {(data.auc_roc * 100).toFixed(2)}%
              </p>
              <p className="text-xs text-purple-400">
                <span className="font-medium">Quality:</span> {(data.quality_score * 100).toFixed(2)}%
              </p>
            </div>
          </div>
        </div>
      );
    }
    return null;
  };

  const CustomDot = (props: any) => {
    const { cx, cy, payload } = props;
    const isPareto = paretoFrontier.some(p => p.model_id === payload.model_id);
    
    return (
      <circle
        cx={cx}
        cy={cy}
        r={isPareto ? 8 : 6}
        fill={payload.method === 'SHAP' ? '#3b82f6' : '#f97316'}
        stroke={isPareto ? '#fbbf24' : 'none'}
        strokeWidth={isPareto ? 2 : 0}
        opacity={0.8}
      />
    );
  };

  return (
    <div className="w-full">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{title}</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Higher and to the right is better
          </p>
        </div>
        {showParetoFrontier && paretoFrontier.length > 0 && (
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-yellow-400 border-2 border-yellow-500"></div>
            <span className="text-xs text-gray-600 dark:text-gray-400">Pareto Optimal</span>
          </div>
        )}
      </div>

      <ResponsiveContainer width="100%" height={500}>
        <ScatterChart margin={{ top: 20, right: 30, bottom: 60, left: 60 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          
          <XAxis 
            type="number" 
            dataKey="auc_roc" 
            domain={[0.5, 1.0]}
            tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
            stroke="#6b7280"
          >
            <Label 
              value="Model Performance (AUC-ROC)" 
              position="bottom" 
              offset={40}
              style={{ fill: '#6b7280', fontSize: 14, fontWeight: 600 }}
            />
          </XAxis>
          
          <YAxis 
            type="number" 
            dataKey="quality_score" 
            domain={[0, 1.0]}
            tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
            stroke="#6b7280"
          >
            <Label 
              value="Explanation Quality" 
              angle={-90} 
              position="left" 
              offset={40}
              style={{ fill: '#6b7280', fontSize: 14, fontWeight: 600 }}
            />
          </YAxis>
          
          <Tooltip content={<CustomTooltip />} />
          <Legend 
            wrapperStyle={{ paddingTop: '20px' }}
            iconType="circle"
          />
          
          {/* Reference lines for "good" thresholds */}
          <ReferenceLine 
            x={0.8} 
            stroke="#10b981" 
            strokeDasharray="5 5" 
            strokeWidth={1}
            label={{ value: 'Good AUC', position: 'top', fill: '#10b981', fontSize: 11 }}
          />
          <ReferenceLine 
            y={0.7} 
            stroke="#8b5cf6" 
            strokeDasharray="5 5" 
            strokeWidth={1}
            label={{ value: 'Good Quality', position: 'right', fill: '#8b5cf6', fontSize: 11 }}
          />
          
          {/* Pareto frontier line */}
          {showParetoFrontier && paretoFrontier.length > 1 && (
            <Scatter
              name="Pareto Frontier"
              data={paretoFrontier}
              line={{ stroke: '#fbbf24', strokeWidth: 2, strokeDasharray: '5 5' }}
              shape={() => null}
            />
          )}
          
          {/* SHAP points */}
          {shapData.length > 0 && (
            <Scatter
              name="SHAP"
              data={shapData}
              fill="#3b82f6"
              shape={<CustomDot />}
            />
          )}
          
          {/* LIME points */}
          {limeData.length > 0 && (
            <Scatter
              name="LIME"
              data={limeData}
              fill="#f97316"
              shape={<CustomDot />}
            />
          )}
        </ScatterChart>
      </ResponsiveContainer>

      {/* Interpretation Guide */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-3">
        <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-3">
          <div className="flex items-center space-x-2 mb-1">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span className="text-xs font-semibold text-green-900 dark:text-green-300">
              Ideal Zone
            </span>
          </div>
          <p className="text-xs text-green-700 dark:text-green-400">
            High AUC (&gt;0.8) + High Quality (&gt;0.7)
          </p>
        </div>
        
        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-3">
          <div className="flex items-center space-x-2 mb-1">
            <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
            <span className="text-xs font-semibold text-blue-900 dark:text-blue-300">
              SHAP Method
            </span>
          </div>
          <p className="text-xs text-blue-700 dark:text-blue-400">
            Game-theoretic, consistent attributions
          </p>
        </div>
        
        <div className="bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded-lg p-3">
          <div className="flex items-center space-x-2 mb-1">
            <div className="w-3 h-3 bg-orange-500 rounded-full"></div>
            <span className="text-xs font-semibold text-orange-900 dark:text-orange-300">
              LIME Method
            </span>
          </div>
          <p className="text-xs text-orange-700 dark:text-orange-400">
            Local surrogate, model-agnostic
          </p>
        </div>
      </div>
    </div>
  );
}
