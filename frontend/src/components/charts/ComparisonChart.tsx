'use client';

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface ComparisonChartProps {
  models: Array<{
    model_name: string;
    model_type: string;
    auc_roc: number;
    auc_pr: number;
    f1_score: number;
    accuracy: number;
  }>;
}

export default function ComparisonChart({ models }: ComparisonChartProps) {
  const data = models.map(model => ({
    name: model.model_type.replace('_', ' ').toUpperCase(),
    'AUC-ROC': parseFloat((model.auc_roc * 100).toFixed(1)),
    'AUC-PR': parseFloat((model.auc_pr * 100).toFixed(1)),
    'F1 Score': parseFloat((model.f1_score * 100).toFixed(1)),
    'Accuracy': parseFloat((model.accuracy * 100).toFixed(1)),
  }));

  return (
    <ResponsiveContainer width="100%" height={400}>
      <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
        <XAxis 
          dataKey="name" 
          tick={{ fontSize: 11 }}
          angle={-45}
          textAnchor="end"
          height={100}
        />
        <YAxis 
          domain={[0, 100]}
          tick={{ fontSize: 12 }}
          label={{ value: 'Score (%)', angle: -90, position: 'insideLeft' }}
        />
        <Tooltip 
          formatter={(value: number) => `${value}%`}
          contentStyle={{ backgroundColor: '#FFF', border: '1px solid #E5E7EB', borderRadius: '8px' }}
        />
        <Legend 
          wrapperStyle={{ paddingTop: '20px' }}
          iconType="circle"
        />
        <Bar dataKey="AUC-ROC" fill="#3B82F6" radius={[4, 4, 0, 0]} />
        <Bar dataKey="AUC-PR" fill="#10B981" radius={[4, 4, 0, 0]} />
        <Bar dataKey="F1 Score" fill="#8B5CF6" radius={[4, 4, 0, 0]} />
        <Bar dataKey="Accuracy" fill="#F59E0B" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
