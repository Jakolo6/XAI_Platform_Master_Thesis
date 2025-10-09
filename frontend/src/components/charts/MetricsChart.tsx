'use client';

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';

interface MetricsChartProps {
  metrics: {
    auc_roc: number;
    auc_pr: number;
    f1_score: number;
    precision: number;
    recall: number;
    accuracy: number;
  };
}

export default function MetricsChart({ metrics }: MetricsChartProps) {
  const data = [
    { name: 'AUC-ROC', value: metrics.auc_roc * 100, color: '#3B82F6' },
    { name: 'AUC-PR', value: metrics.auc_pr * 100, color: '#10B981' },
    { name: 'F1 Score', value: metrics.f1_score * 100, color: '#8B5CF6' },
    { name: 'Precision', value: metrics.precision * 100, color: '#F59E0B' },
    { name: 'Recall', value: metrics.recall * 100, color: '#EF4444' },
    { name: 'Accuracy', value: metrics.accuracy * 100, color: '#06B6D4' },
  ];

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
        <XAxis 
          dataKey="name" 
          tick={{ fontSize: 12 }}
          angle={-45}
          textAnchor="end"
          height={80}
        />
        <YAxis 
          domain={[0, 100]}
          tick={{ fontSize: 12 }}
          label={{ value: 'Score (%)', angle: -90, position: 'insideLeft' }}
        />
        <Tooltip 
          formatter={(value: number) => `${value.toFixed(1)}%`}
          contentStyle={{ backgroundColor: '#FFF', border: '1px solid #E5E7EB', borderRadius: '8px' }}
        />
        <Bar dataKey="value" radius={[8, 8, 0, 0]}>
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.color} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
