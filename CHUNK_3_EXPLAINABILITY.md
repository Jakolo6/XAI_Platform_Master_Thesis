# CHUNK 3: EXPLAINABILITY (SHAP/LIME) - FRONTEND + BACKEND

## BACKEND: Explanation Service
**File:** `backend/app/services/home_credit_explanation_service.py`

```python
"""SHAP and LIME explanation service for Home Credit models"""
import pandas as pd
import numpy as np
import shap
import lime.lime_tabular
import joblib
from pathlib import Path
import structlog
from typing import Dict, Any

logger = structlog.get_logger()

class HomeCreditExplanationService:
    MODELS_DIR = Path("models")
    DATA_DIR = Path("data/processed")
    
    def generate_explanations(self, model_id: str, method: str = 'both') -> Dict[str, Any]:
        """Generate SHAP and/or LIME explanations"""
        try:
            # Load model
            model = joblib.load(self.MODELS_DIR / f"{model_id}.pkl")
            
            # Load test data
            test_df = pd.read_csv(self.DATA_DIR / "home_credit_test.csv")
            X_test = test_df.drop('TARGET', axis=1)
            y_test = test_df['TARGET']
            
            # Sample 100 instances
            sample_indices = np.random.choice(len(X_test), 100, replace=False)
            X_sample = X_test.iloc[sample_indices]
            
            result = {'model_id': model_id}
            
            if method in ['shap', 'both']:
                result['shap'] = self._generate_shap(model, X_sample, X_test)
            
            if method in ['lime', 'both']:
                result['lime'] = self._generate_lime(model, X_sample, X_test)
            
            return result
            
        except Exception as e:
            logger.error("Explanation generation failed", error=str(e))
            raise
    
    def _generate_shap(self, model, X_sample, X_test):
        """Generate SHAP explanations"""
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_sample)
        
        # Handle binary classification output
        if isinstance(shap_values, list):
            shap_values = shap_values[1]
        
        # Global feature importance
        global_importance = np.abs(shap_values).mean(axis=0)
        feature_names = X_sample.columns.tolist()
        
        # Top 10 features
        top_indices = np.argsort(global_importance)[-10:][::-1]
        
        return {
            'global_importance': {
                feature_names[i]: float(global_importance[i])
                for i in top_indices
            },
            'shap_values': shap_values.tolist(),
            'base_value': float(explainer.expected_value[1] if isinstance(explainer.expected_value, list) else explainer.expected_value),
            'feature_names': feature_names
        }
    
    def _generate_lime(self, model, X_sample, X_test):
        """Generate LIME explanations"""
        explainer = lime.lime_tabular.LimeTabularExplainer(
            X_test.values,
            feature_names=X_test.columns.tolist(),
            class_names=['No Default', 'Default'],
            mode='classification'
        )
        
        # Generate explanations for sample
        lime_explanations = []
        for idx in range(min(10, len(X_sample))):
            exp = explainer.explain_instance(
                X_sample.iloc[idx].values,
                model.predict_proba,
                num_features=10
            )
            lime_explanations.append({
                'instance_id': idx,
                'explanation': dict(exp.as_list())
            })
        
        # Aggregate feature importance
        all_features = {}
        for exp in lime_explanations:
            for feature, importance in exp['explanation'].items():
                if feature not in all_features:
                    all_features[feature] = []
                all_features[feature].append(importance)
        
        global_importance = {
            feature: float(np.mean(np.abs(values)))
            for feature, values in all_features.items()
        }
        
        return {
            'global_importance': dict(sorted(global_importance.items(), key=lambda x: x[1], reverse=True)[:10]),
            'local_explanations': lime_explanations[:5]
        }

explanation_service = HomeCreditExplanationService()
```

## BACKEND: API Endpoints
**File:** `backend/app/api/v1/endpoints/home_credit_explanations.py`

```python
"""Explanation API endpoints"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import structlog
from app.services.home_credit_explanation_service import explanation_service
from app.utils.supabase_client import supabase_db

router = APIRouter()
logger = structlog.get_logger()

class ExplanationRequest(BaseModel):
    model_id: str
    method: str = 'both'

@router.post("/generate")
async def generate_explanations(request: ExplanationRequest):
    """Generate SHAP and/or LIME explanations"""
    try:
        result = explanation_service.generate_explanations(
            request.model_id,
            request.method
        )
        
        # Save to Supabase
        supabase_db.table('explanations').insert({
            'model_id': request.model_id,
            'method': request.method,
            'shap_data': result.get('shap'),
            'lime_data': result.get('lime'),
            'status': 'completed'
        }).execute()
        
        return result
    except Exception as e:
        logger.error("Explanation generation failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/model/{model_id}")
async def get_explanations(model_id: str):
    """Get explanations for a model"""
    result = supabase_db.table('explanations').select('*').eq('model_id', model_id).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Explanations not found")
    
    return result.data[0]
```

## FRONTEND: Explainability Page
**File:** `frontend/src/app/explain/page.tsx`

```typescript
'use client';

export const dynamic = 'force-dynamic';

import { useState, useEffect } from 'react';
import { Lightbulb, Download, Loader2, BarChart3, TrendingUp } from 'lucide-react';
import axios from 'axios';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export default function ExplainPage() {
  const [models, setModels] = useState<any[]>([]);
  const [selectedModel, setSelectedModel] = useState('');
  const [activeTab, setActiveTab] = useState<'shap' | 'lime' | 'comparison'>('shap');
  const [explanations, setExplanations] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadModels();
  }, []);

  const loadModels = async () => {
    try {
      const response = await axios.get(`${API_BASE}/training/models`);
      setModels(response.data.models);
    } catch (error) {
      console.error('Failed to load models', error);
    }
  };

  const handleGenerate = async () => {
    if (!selectedModel) {
      alert('Please select a model');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/explanations/generate`, {
        model_id: selectedModel,
        method: 'both'
      });
      setExplanations(response.data);
      alert('Explanations generated successfully!');
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to generate explanations');
    } finally {
      setLoading(false);
    }
  };

  const exportCSV = () => {
    if (!explanations) return;
    
    const data = activeTab === 'shap' 
      ? explanations.shap?.global_importance 
      : explanations.lime?.global_importance;
    
    const csv = Object.entries(data || {})
      .map(([feature, importance]) => `${feature},${importance}`)
      .join('\n');
    
    const blob = new Blob([`Feature,Importance\n${csv}`], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${activeTab}_explanations.csv`;
    a.click();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-teal-50">
      <div className="bg-white border-b shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="p-3 bg-gradient-to-br from-green-500 to-teal-600 rounded-xl">
                <Lightbulb className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Explainable AI</h1>
                <p className="text-gray-600 mt-1">SHAP and LIME Explanations</p>
              </div>
            </div>
            {explanations && (
              <button
                onClick={exportCSV}
                className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
              >
                <Download className="h-5 w-5" />
                <span>Export CSV</span>
              </button>
            )}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Model Selection */}
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Select Model</h2>
          <div className="flex space-x-4">
            <select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg"
            >
              <option value="">Choose a model...</option>
              {models.map(model => (
                <option key={model.model_id} value={model.model_id}>
                  {model.name} - AUC: {(model.metrics?.auc * 100).toFixed(2)}%
                </option>
              ))}
            </select>
            <button
              onClick={handleGenerate}
              disabled={loading || !selectedModel}
              className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 flex items-center space-x-2"
            >
              {loading ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin" />
                  <span>Generating...</span>
                </>
              ) : (
                <>
                  <Lightbulb className="h-5 w-5" />
                  <span>Generate Explanations</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Tabs */}
        {explanations && (
          <>
            <div className="bg-white rounded-lg shadow-sm border mb-6">
              <div className="border-b">
                <div className="flex space-x-1 p-2">
                  {(['shap', 'lime', 'comparison'] as const).map(tab => (
                    <button
                      key={tab}
                      onClick={() => setActiveTab(tab)}
                      className={`px-6 py-3 rounded-lg font-medium transition-colors ${
                        activeTab === tab
                          ? 'bg-green-100 text-green-900'
                          : 'text-gray-600 hover:bg-gray-100'
                      }`}
                    >
                      {tab.toUpperCase()}
                    </button>
                  ))}
                </div>
              </div>

              <div className="p-6">
                {/* SHAP Tab */}
                {activeTab === 'shap' && explanations.shap && (
                  <div>
                    <h3 className="text-lg font-bold text-gray-900 mb-4">
                      SHAP Feature Importance
                    </h3>
                    <div className="space-y-3">
                      {Object.entries(explanations.shap.global_importance).map(([feature, importance]: [string, any]) => {
                        const maxImportance = Math.max(...Object.values(explanations.shap.global_importance) as number[]);
                        const width = (importance / maxImportance) * 100;
                        
                        return (
                          <div key={feature}>
                            <div className="flex justify-between mb-1">
                              <span className="text-sm font-medium text-gray-700">{feature}</span>
                              <span className="text-sm text-gray-600">{importance.toFixed(4)}</span>
                            </div>
                            <div className="h-6 bg-gray-100 rounded overflow-hidden">
                              <div
                                className="h-full bg-gradient-to-r from-blue-500 to-blue-600"
                                style={{ width: `${width}%` }}
                              />
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* LIME Tab */}
                {activeTab === 'lime' && explanations.lime && (
                  <div>
                    <h3 className="text-lg font-bold text-gray-900 mb-4">
                      LIME Feature Importance
                    </h3>
                    <div className="space-y-3">
                      {Object.entries(explanations.lime.global_importance).map(([feature, importance]: [string, any]) => {
                        const maxImportance = Math.max(...Object.values(explanations.lime.global_importance) as number[]);
                        const width = (importance / maxImportance) * 100;
                        
                        return (
                          <div key={feature}>
                            <div className="flex justify-between mb-1">
                              <span className="text-sm font-medium text-gray-700">{feature}</span>
                              <span className="text-sm text-gray-600">{importance.toFixed(4)}</span>
                            </div>
                            <div className="h-6 bg-gray-100 rounded overflow-hidden">
                              <div
                                className="h-full bg-gradient-to-r from-orange-500 to-orange-600"
                                style={{ width: `${width}%` }}
                              />
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* Comparison Tab */}
                {activeTab === 'comparison' && (
                  <div>
                    <h3 className="text-lg font-bold text-gray-900 mb-4">
                      SHAP vs LIME Comparison
                    </h3>
                    <div className="grid grid-cols-2 gap-6">
                      <div>
                        <h4 className="font-semibold text-blue-900 mb-3">SHAP Top Features</h4>
                        <ol className="list-decimal list-inside space-y-2">
                          {Object.keys(explanations.shap?.global_importance || {}).slice(0, 5).map(feature => (
                            <li key={feature} className="text-sm text-gray-700">{feature}</li>
                          ))}
                        </ol>
                      </div>
                      <div>
                        <h4 className="font-semibold text-orange-900 mb-3">LIME Top Features</h4>
                        <ol className="list-decimal list-inside space-y-2">
                          {Object.keys(explanations.lime?.global_importance || {}).slice(0, 5).map(feature => (
                            <li key={feature} className="text-sm text-gray-700">{feature}</li>
                          ))}
                        </ol>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
```

## Register Routes
Add to `backend/app/api/v1/api.py`:
```python
from app.api.v1.endpoints import home_credit_explanations
api_router.include_router(home_credit_explanations.router, prefix="/explanations", tags=["explanations"])
```

## Update Navigation
Add to `frontend/src/components/Navbar.tsx`:
```typescript
{ href: '/explain', label: 'Explain' },
```
