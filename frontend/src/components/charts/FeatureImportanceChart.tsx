'use client';

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

interface FeatureImportanceChartProps {
  features: Array<{
    feature: string;
    importance: number;
    rank: number;
  }>;
  maxFeatures?: number;
}

export default function FeatureImportanceChart({ features, maxFeatures = 20 }: FeatureImportanceChartProps) {
  // Take top N features
  const topFeatures = features.slice(0, maxFeatures);
  
  // Prepare data for chart
  const data = topFeatures.map(f => ({
    name: f.feature.length > 20 ? f.feature.substring(0, 17) + '...' : f.feature,
    fullName: f.feature,
    importance: f.importance,
    rank: f.rank
  }));

  // Color gradient from blue to light blue
  const getColor = (index: number) => {
    const colors = [
      '#1E40AF', '#2563EB', '#3B82F6', '#60A5FA', '#93C5FD',
      '#BFDBFE', '#DBEAFE', '#EFF6FF', '#F0F9FF', '#F8FAFC'
    ];
    return colors[Math.min(index, colors.length - 1)];
  };

  return (
    <div className="w-full">
      <ResponsiveContainer width="100%" height={Math.max(400, topFeatures.length * 25)}>
        <BarChart 
          data={data} 
          layout="vertical"
          margin={{ top: 20, right: 30, left: 120, bottom: 20 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
          <XAxis 
            type="number"
            tick={{ fontSize: 12 }}
            label={{ value: 'SHAP Importance', position: 'insideBottom', offset: -10 }}
          />
          <YAxis 
            type="category"
            dataKey="name"
            tick={{ fontSize: 11 }}
            width={110}
          />
          <Tooltip 
            content={({ active, payload }) => {
              if (active && payload && payload.length) {
                const value = payload[0].value;
                const importance = typeof value === 'number' ? value.toFixed(4) : value;
                return (
                  <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
                    <p className="font-semibold text-sm">{payload[0].payload.fullName}</p>
                    <p className="text-sm text-gray-600">
                      Importance: {importance}
                    </p>
                    <p className="text-xs text-gray-500">
                      Rank: #{payload[0].payload.rank}
                    </p>
                  </div>
                );
              }
              return null;
            }}
          />
          <Bar dataKey="importance" radius={[0, 4, 4, 0]}>
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={getColor(index)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
