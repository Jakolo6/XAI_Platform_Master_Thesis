# CHUNK 4: INTERPRETABILITY BRIDGE - FRONTEND + BACKEND

## BACKEND: Interpretation Service
**File:** `backend/app/services/interpretation_service.py`

```python
"""Convert SHAP/LIME to human-readable text"""
import structlog
from typing import Dict, Any, List

logger = structlog.get_logger()

class InterpretationService:
    
    def generate_interpretation(self, explanations: Dict[str, Any]) -> Dict[str, Any]:
        """Generate human-readable interpretation"""
        
        shap_data = explanations.get('shap', {})
        lime_data = explanations.get('lime', {})
        
        # Technical interpretation
        technical = self._generate_technical(shap_data, lime_data)
        
        # Human interpretation
        human = self._generate_human(shap_data, lime_data)
        
        return {
            'technical': technical,
            'human': human,
            'key_insights': self._extract_insights(shap_data, lime_data)
        }
    
    def _generate_technical(self, shap_data, lime_data):
        """Technical feature-based interpretation"""
        lines = []
        
        if shap_data and 'global_importance' in shap_data:
            lines.append("SHAP Analysis:")
            for feature, importance in list(shap_data['global_importance'].items())[:5]:
                lines.append(f"  • {feature}: {importance:.4f}")
        
        if lime_data and 'global_importance' in lime_data:
            lines.append("\nLIME Analysis:")
            for feature, importance in list(lime_data['global_importance'].items())[:5]:
                lines.append(f"  • {feature}: {importance:.4f}")
        
        return '\n'.join(lines)
    
    def _generate_human(self, shap_data, lime_data):
        """Plain-language interpretation"""
        insights = []
        
        if shap_data and 'global_importance' in shap_data:
            top_feature = list(shap_data['global_importance'].keys())[0]
            insights.append(
                f"Your {self._humanize_feature(top_feature)} is the most important factor "
                f"in determining credit risk."
            )
        
        if lime_data and 'global_importance' in lime_data:
            top_feature = list(lime_data['global_importance'].keys())[0]
            insights.append(
                f"Local analysis shows {self._humanize_feature(top_feature)} "
                f"has significant impact on individual predictions."
            )
        
        return ' '.join(insights)
    
    def _humanize_feature(self, feature: str) -> str:
        """Convert feature names to human-readable"""
        mapping = {
            'AMT_INCOME_TOTAL': 'income level',
            'AMT_CREDIT': 'credit amount',
            'AMT_ANNUITY': 'loan annuity',
            'DAYS_BIRTH': 'age',
            'DAYS_EMPLOYED': 'employment history',
            'EXT_SOURCE_1': 'external credit score 1',
            'EXT_SOURCE_2': 'external credit score 2',
            'EXT_SOURCE_3': 'external credit score 3'
        }
        return mapping.get(feature, feature.lower().replace('_', ' '))
    
    def _extract_insights(self, shap_data, lime_data):
        """Extract key insights"""
        insights = []
        
        if shap_data and lime_data:
            shap_top = set(list(shap_data.get('global_importance', {}).keys())[:5])
            lime_top = set(list(lime_data.get('global_importance', {}).keys())[:5])
            
            overlap = shap_top & lime_top
            if overlap:
                insights.append({
                    'type': 'agreement',
                    'message': f"Both methods agree on {len(overlap)} key features",
                    'features': list(overlap)
                })
        
        return insights

interpretation_service = InterpretationService()
```

## BACKEND: API Endpoint
**File:** `backend/app/api/v1/endpoints/interpretation.py`

```python
"""Interpretation API"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import structlog
from app.services.interpretation_service import interpretation_service

router = APIRouter()
logger = structlog.get_logger()

class InterpretRequest(BaseModel):
    explanations: dict

@router.post("/generate")
async def generate_interpretation(request: InterpretRequest):
    """Generate human-readable interpretation"""
    try:
        result = interpretation_service.generate_interpretation(request.explanations)
        return result
    except Exception as e:
        logger.error("Interpretation failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
```

## FRONTEND: Interpretation Component
**File:** `frontend/src/app/interpret/page.tsx`

```typescript
'use client';

export const dynamic = 'force-dynamic';

import { useState } from 'react';
import { MessageSquare, ToggleLeft, ToggleRight } from 'lucide-react';
import axios from 'axios';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export default function InterpretPage() {
  const [mode, setMode] = useState<'technical' | 'human'>('human');
  const [explanations, setExplanations] = useState<any>(null);
  const [interpretation, setInterpretation] = useState<any>(null);

  const handleInterpret = async (explainData: any) => {
    try {
      const response = await axios.post(`${API_BASE}/interpretation/generate`, {
        explanations: explainData
      });
      setInterpretation(response.data);
    } catch (error) {
      console.error('Interpretation failed', error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-purple-50">
      <div className="bg-white border-b shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="p-3 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl">
                <MessageSquare className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Interpretability Bridge</h1>
                <p className="text-gray-600 mt-1">Human-readable AI explanations</p>
              </div>
            </div>
            
            <button
              onClick={() => setMode(mode === 'technical' ? 'human' : 'technical')}
              className="flex items-center space-x-2 px-4 py-2 bg-indigo-100 text-indigo-900 rounded-lg hover:bg-indigo-200"
            >
              {mode === 'technical' ? <ToggleRight className="h-5 w-5" /> : <ToggleLeft className="h-5 w-5" />}
              <span>{mode === 'technical' ? 'Technical' : 'Human'} Mode</span>
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {interpretation && (
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              AI Explanation Summary
            </h2>
            
            <div className="prose max-w-none">
              {mode === 'human' ? (
                <p className="text-lg text-gray-700 leading-relaxed">
                  {interpretation.human}
                </p>
              ) : (
                <pre className="text-sm text-gray-700 whitespace-pre-wrap bg-gray-50 p-4 rounded">
                  {interpretation.technical}
                </pre>
              )}
            </div>

            {interpretation.key_insights && interpretation.key_insights.length > 0 && (
              <div className="mt-6 pt-6 border-t">
                <h3 className="font-semibold text-gray-900 mb-3">Key Insights</h3>
                {interpretation.key_insights.map((insight: any, idx: number) => (
                  <div key={idx} className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <p className="text-blue-900">{insight.message}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
```

## Register Routes
Add to `backend/app/api/v1/api.py`:
```python
from app.api.v1.endpoints import interpretation
api_router.include_router(interpretation.router, prefix="/interpretation", tags=["interpretation"])
```
