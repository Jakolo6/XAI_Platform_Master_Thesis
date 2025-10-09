'use client';

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, ReferenceLine } from 'recharts';

interface ShapWaterfallChartProps {
  features: Array<{
    feature: string;
    value: number;
    shap_value: number;
    abs_shap_value: number;
  }>;
  baseValue: number;
  prediction: {
    probability: number;
    label: string;
  };
  maxFeatures?: number;
}

export default function ShapWaterfallChart({ 
  features, 
  baseValue, 
  prediction,
  maxFeatures = 10 
}: ShapWaterfallChartProps) {
  // Take top N features by absolute SHAP value
  const topFeatures = features.slice(0, maxFeatures);
  
  // Prepare data for waterfall chart
  const data = topFeatures.map(f => ({
    name: f.feature.length > 15 ? f.feature.substring(0, 12) + '...' : f.feature,
    fullName: f.feature,
    value: f.shap_value,
    absValue: f.abs_shap_value,
    featureValue: f.value,
    color: f.shap_value > 0 ? '#EF4444' : '#10B981' // Red for positive, green for negative
  }));

  return (
    <div className="w-full space-y-4">
      {/* Prediction Summary */}
      <div className="bg-gray-50 rounded-lg p-4 border">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-sm text-gray-600">Prediction</div>
            <div className={`text-2xl font-bold ${prediction.label === 'Fraud' ? 'text-red-600' : 'text-green-600'}`}>
              {prediction.label}
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-600">Probability</div>
            <div className="text-2xl font-bold text-gray-900">
              {(prediction.probability * 100).toFixed(1)}%
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-600">Base Value</div>
            <div className="text-2xl font-bold text-gray-900">
              {baseValue.toFixed(3)}
            </div>
          </div>
        </div>
      </div>

      {/* SHAP Values Chart */}
      <div className="bg-white rounded-lg border p-4">
        <h3 className="text-lg font-semibold mb-4">Feature Contributions</h3>
        <ResponsiveContainer width="100%" height={Math.max(300, topFeatures.length * 40)}>
          <BarChart 
            data={data} 
            layout="vertical"
            margin={{ top: 20, right: 30, left: 100, bottom: 20 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            <XAxis 
              type="number"
              tick={{ fontSize: 12 }}
              label={{ value: 'SHAP Value', position: 'insideBottom', offset: -10 }}
            />
            <YAxis 
              type="category"
              dataKey="name"
              tick={{ fontSize: 11 }}
              width={90}
            />
            <ReferenceLine x={0} stroke="#9CA3AF" strokeWidth={2} />
            <Tooltip 
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const data = payload[0].payload;
                  return (
                    <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
                      <p className="font-semibold text-sm mb-2">{data.fullName}</p>
                      <p className="text-sm text-gray-600">
                        Feature Value: {typeof data.featureValue === 'number' 
                          ? data.featureValue.toFixed(2) 
                          : data.featureValue}
                      </p>
                      <p className={`text-sm font-semibold ${data.value > 0 ? 'text-red-600' : 'text-green-600'}`}>
                        SHAP: {data.value > 0 ? '+' : ''}{data.value.toFixed(4)}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        {data.value > 0 ? 'Increases fraud probability' : 'Decreases fraud probability'}
                      </p>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Bar dataKey="value" radius={[0, 4, 4, 0]}>
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Legend */}
      <div className="flex justify-center space-x-6 text-sm">
        <div className="flex items-center">
          <div className="w-4 h-4 bg-red-500 rounded mr-2"></div>
          <span className="text-gray-600">Increases fraud probability</span>
        </div>
        <div className="flex items-center">
          <div className="w-4 h-4 bg-green-500 rounded mr-2"></div>
          <span className="text-gray-600">Decreases fraud probability</span>
        </div>
      </div>
    </div>
  );
}
