# CHUNK 2: MODEL TRAINING - FRONTEND

## File: Training Page
**Path:** `frontend/src/app/train/page.tsx`

```typescript
'use client';

export const dynamic = 'force-dynamic';

import { useState } from 'react';
import { Brain, Sliders, Zap, CheckCircle, Loader2 } from 'lucide-react';
import axios from 'axios';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export default function TrainPage() {
  const [algorithm, setAlgorithm] = useState('xgboost');
  const [optimize, setOptimize] = useState(false);
  const [training, setTraining] = useState(false);
  const [result, setResult] = useState<any>(null);
  
  // XGBoost params
  const [nEstimators, setNEstimators] = useState(100);
  const [maxDepth, setMaxDepth] = useState(6);
  const [learningRate, setLearningRate] = useState(0.1);
  const [subsample, setSubsample] = useState(0.8);
  const [colsample, setColsample] = useState(0.8);

  const handleTrain = async () => {
    setTraining(true);
    setResult(null);
    
    try {
      const params = algorithm === 'xgboost' ? {
        n_estimators: nEstimators,
        max_depth: maxDepth,
        learning_rate: learningRate,
        subsample: subsample,
        colsample_bytree: colsample
      } : {};
      
      const response = await axios.post(`${API_BASE}/training/train`, {
        algorithm,
        params,
        optimize
      });
      
      setResult(response.data);
      alert('Model trained successfully!');
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Training failed');
    } finally {
      setTraining(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-50">
      <div className="bg-white border-b shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center space-x-4">
            <div className="p-3 bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl">
              <Brain className="h-8 w-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Model Training</h1>
              <p className="text-gray-600 mt-1">Train ML models on Home Credit dataset</p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Algorithm Selection */}
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Select Algorithm</h2>
          <div className="grid grid-cols-3 gap-4">
            {['xgboost', 'random_forest', 'logistic_regression'].map(algo => (
              <button
                key={algo}
                onClick={() => setAlgorithm(algo)}
                className={`p-4 rounded-lg border-2 transition-all ${
                  algorithm === algo
                    ? 'border-purple-600 bg-purple-50'
                    : 'border-gray-200 hover:border-purple-300'
                }`}
              >
                <div className="font-semibold text-gray-900 capitalize">
                  {algo.replace('_', ' ')}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Parameters */}
        {algorithm === 'xgboost' && (
          <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center space-x-2">
              <Sliders className="h-5 w-5" />
              <span>Hyperparameters</span>
            </h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  n_estimators: {nEstimators}
                </label>
                <input
                  type="range"
                  min="50"
                  max="300"
                  value={nEstimators}
                  onChange={(e) => setNEstimators(Number(e.target.value))}
                  className="w-full"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  max_depth: {maxDepth}
                </label>
                <input
                  type="range"
                  min="3"
                  max="10"
                  value={maxDepth}
                  onChange={(e) => setMaxDepth(Number(e.target.value))}
                  className="w-full"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  learning_rate: {learningRate.toFixed(2)}
                </label>
                <input
                  type="range"
                  min="0.01"
                  max="0.3"
                  step="0.01"
                  value={learningRate}
                  onChange={(e) => setLearningRate(Number(e.target.value))}
                  className="w-full"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  subsample: {subsample.toFixed(2)}
                </label>
                <input
                  type="range"
                  min="0.6"
                  max="1.0"
                  step="0.05"
                  value={subsample}
                  onChange={(e) => setSubsample(Number(e.target.value))}
                  className="w-full"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  colsample_bytree: {colsample.toFixed(2)}
                </label>
                <input
                  type="range"
                  min="0.6"
                  max="1.0"
                  step="0.05"
                  value={colsample}
                  onChange={(e) => setColsample(Number(e.target.value))}
                  className="w-full"
                />
              </div>
            </div>
          </div>
        )}

        {/* Optimization */}
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
          <label className="flex items-center space-x-3 cursor-pointer">
            <input
              type="checkbox"
              checked={optimize}
              onChange={(e) => setOptimize(e.target.checked)}
              className="w-5 h-5 text-purple-600"
            />
            <div>
              <div className="font-semibold text-gray-900 flex items-center space-x-2">
                <Zap className="h-5 w-5 text-yellow-500" />
                <span>Enable Hyperparameter Optimization (Optuna)</span>
              </div>
              <p className="text-sm text-gray-600">
                Automatically find best parameters (takes longer)
              </p>
            </div>
          </label>
        </div>

        {/* Train Button */}
        <button
          onClick={handleTrain}
          disabled={training}
          className="w-full flex items-center justify-center space-x-2 px-6 py-4 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50 text-lg font-semibold"
        >
          {training ? (
            <>
              <Loader2 className="h-6 w-6 animate-spin" />
              <span>Training Model...</span>
            </>
          ) : (
            <>
              <Brain className="h-6 w-6" />
              <span>Train Model</span>
            </>
          )}
        </button>

        {/* Results */}
        {result && (
          <div className="mt-6 bg-white rounded-lg shadow-sm border p-6">
            <div className="flex items-center space-x-2 mb-4">
              <CheckCircle className="h-6 w-6 text-green-600" />
              <h2 className="text-xl font-bold text-gray-900">Training Complete!</h2>
            </div>
            
            <div className="grid grid-cols-3 gap-4 mb-4">
              <div className="bg-blue-50 rounded-lg p-4">
                <div className="text-sm text-blue-700 mb-1">AUC Score</div>
                <div className="text-2xl font-bold text-blue-900">
                  {(result.metrics.auc * 100).toFixed(2)}%
                </div>
              </div>
              <div className="bg-green-50 rounded-lg p-4">
                <div className="text-sm text-green-700 mb-1">Accuracy</div>
                <div className="text-2xl font-bold text-green-900">
                  {(result.metrics.accuracy * 100).toFixed(2)}%
                </div>
              </div>
              <div className="bg-purple-50 rounded-lg p-4">
                <div className="text-sm text-purple-700 mb-1">F1 Score</div>
                <div className="text-2xl font-bold text-purple-900">
                  {(result.metrics.f1 * 100).toFixed(2)}%
                </div>
              </div>
            </div>
            
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="text-sm text-gray-600 mb-1">Model ID</div>
              <code className="text-sm font-mono text-gray-900">{result.model_id}</code>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
```

## Update Navigation
Add to `frontend/src/components/Navbar.tsx`:
```typescript
{ href: '/train', label: 'Train Model' },
```
