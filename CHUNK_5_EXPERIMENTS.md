# CHUNK 5: EXPERIMENTS & BENCHMARKING - FRONTEND + BACKEND

## BACKEND: Benchmark Service
**File:** `backend/app/services/benchmark_service.py`

```python
"""Model and explanation benchmarking"""
import structlog
from typing import Dict, Any, List
from app.utils.supabase_client import supabase_db

logger = structlog.get_logger()

class BenchmarkService:
    
    def compare_models(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Compare all models"""
        
        # Get all models
        query = supabase_db.table('models').select('*')
        
        if filters:
            if 'dataset_id' in filters:
                query = query.eq('dataset_id', filters['dataset_id'])
            if 'algorithm' in filters:
                query = query.eq('model_type', filters['algorithm'])
        
        result = query.execute()
        models = result.data
        
        # Calculate aggregates
        comparison = {
            'models': models,
            'summary': {
                'total_models': len(models),
                'avg_auc': sum(m['metrics'].get('auc', 0) for m in models) / len(models) if models else 0,
                'best_model': max(models, key=lambda m: m['metrics'].get('auc', 0)) if models else None
            }
        }
        
        return comparison
    
    def generate_report(self, model_ids: List[str]) -> Dict[str, Any]:
        """Generate comparison report"""
        
        models = []
        for model_id in model_ids:
            result = supabase_db.table('models').select('*').eq('model_id', model_id).execute()
            if result.data:
                models.append(result.data[0])
        
        report = {
            'models': models,
            'comparison': {
                'metrics': ['auc', 'accuracy', 'f1'],
                'best_per_metric': {}
            }
        }
        
        for metric in ['auc', 'accuracy', 'f1']:
            best = max(models, key=lambda m: m['metrics'].get(metric, 0))
            report['comparison']['best_per_metric'][metric] = {
                'model_id': best['model_id'],
                'value': best['metrics'].get(metric, 0)
            }
        
        return report

benchmark_service = BenchmarkService()
```

## BACKEND: API Endpoints
**File:** `backend/app/api/v1/endpoints/benchmarks.py`

```python
"""Benchmark API"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import structlog
from app.services.benchmark_service import benchmark_service

router = APIRouter()
logger = structlog.get_logger()

class ReportRequest(BaseModel):
    model_ids: List[str]

@router.get("/compare")
async def compare_models(
    dataset_id: Optional[str] = None,
    algorithm: Optional[str] = None
):
    """Compare models with optional filters"""
    try:
        filters = {}
        if dataset_id:
            filters['dataset_id'] = dataset_id
        if algorithm:
            filters['algorithm'] = algorithm
        
        result = benchmark_service.compare_models(filters)
        return result
    except Exception as e:
        logger.error("Comparison failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/report")
async def generate_report(request: ReportRequest):
    """Generate comparison report"""
    try:
        result = benchmark_service.generate_report(request.model_ids)
        return result
    except Exception as e:
        logger.error("Report generation failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
```

## FRONTEND: Experiments Page
**File:** `frontend/src/app/experiments/page.tsx`

```typescript
'use client';

export const dynamic = 'force-dynamic';

import { useState, useEffect } from 'react';
import { FlaskConical, Download, TrendingUp, Award } from 'lucide-react';
import axios from 'axios';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export default function ExperimentsPage() {
  const [comparison, setComparison] = useState<any>(null);
  const [filterAlgorithm, setFilterAlgorithm] = useState('');

  useEffect(() => {
    loadComparison();
  }, [filterAlgorithm]);

  const loadComparison = async () => {
    try {
      const params = filterAlgorithm ? { algorithm: filterAlgorithm } : {};
      const response = await axios.get(`${API_BASE}/benchmarks/compare`, { params });
      setComparison(response.data);
    } catch (error) {
      console.error('Failed to load comparison', error);
    }
  };

  const exportReport = async () => {
    if (!comparison?.models) return;
    
    const modelIds = comparison.models.map((m: any) => m.model_id);
    try {
      const response = await axios.post(`${API_BASE}/benchmarks/report`, {
        model_ids: modelIds
      });
      
      // Download as JSON
      const blob = new Blob([JSON.stringify(response.data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'experiment_report.json';
      a.click();
    } catch (error) {
      alert('Failed to generate report');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-yellow-50 to-orange-50">
      <div className="bg-white border-b shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="p-3 bg-gradient-to-br from-yellow-500 to-orange-600 rounded-xl">
                <FlaskConical className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Experiments</h1>
                <p className="text-gray-600 mt-1">Model benchmarking and comparison</p>
              </div>
            </div>
            
            <button
              onClick={exportReport}
              className="flex items-center space-x-2 px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700"
            >
              <Download className="h-5 w-5" />
              <span>Export Report</span>
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Filters */}
        <div className="bg-white rounded-lg shadow-sm border p-4 mb-6">
          <div className="flex items-center space-x-4">
            <label className="text-sm font-medium text-gray-700">Filter by Algorithm:</label>
            <select
              value={filterAlgorithm}
              onChange={(e) => setFilterAlgorithm(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg"
            >
              <option value="">All</option>
              <option value="xgboost">XGBoost</option>
              <option value="random_forest">Random Forest</option>
              <option value="logistic_regression">Logistic Regression</option>
            </select>
          </div>
        </div>

        {/* Summary Cards */}
        {comparison && (
          <>
            <div className="grid grid-cols-3 gap-6 mb-6">
              <div className="bg-white rounded-lg shadow-sm border p-6">
                <div className="text-sm text-gray-600 mb-1">Total Models</div>
                <div className="text-3xl font-bold text-gray-900">
                  {comparison.summary.total_models}
                </div>
              </div>
              
              <div className="bg-white rounded-lg shadow-sm border p-6">
                <div className="text-sm text-gray-600 mb-1">Average AUC</div>
                <div className="text-3xl font-bold text-gray-900">
                  {(comparison.summary.avg_auc * 100).toFixed(2)}%
                </div>
              </div>
              
              <div className="bg-white rounded-lg shadow-sm border p-6">
                <div className="flex items-center space-x-2 mb-1">
                  <Award className="h-5 w-5 text-yellow-500" />
                  <div className="text-sm text-gray-600">Best Model</div>
                </div>
                <div className="text-lg font-bold text-gray-900">
                  {comparison.summary.best_model?.name || 'N/A'}
                </div>
              </div>
            </div>

            {/* Models Table */}
            <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Model
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Algorithm
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      AUC
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Accuracy
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      F1 Score
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {comparison.models.map((model: any) => (
                    <tr key={model.model_id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {model.name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {model.model_type}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {(model.metrics?.auc * 100).toFixed(2)}%
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {(model.metrics?.accuracy * 100).toFixed(2)}%
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {(model.metrics?.f1 * 100).toFixed(2)}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
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
from app.api.v1.endpoints import benchmarks
api_router.include_router(benchmarks.router, prefix="/benchmarks", tags=["benchmarks"])
```

## Update Navigation
Add to `frontend/src/components/Navbar.tsx`:
```typescript
{ href: '/interpret', label: 'Interpret' },
{ href: '/experiments', label: 'Experiments' },
```
