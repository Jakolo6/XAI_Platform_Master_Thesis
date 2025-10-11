"""
XAI explanation generation endpoints.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import Dict, Any, Optional
from pydantic import BaseModel
import structlog

from app.api.dependencies import get_current_researcher
from app.services.explanation_service import explanation_service
from app.utils.supabase_client import supabase_db

router = APIRouter()
logger = structlog.get_logger()


class ExplanationRequest(BaseModel):
    """Request schema for generating explanations."""
    model_id: str
    method: str = "shap"  # 'shap' or 'lime'
    sample_size: int = 100


class LocalExplanationRequest(BaseModel):
    """Request schema for local (instance-level) explanations."""
    model_id: str
    sample_index: int  # Index of the sample in test set
    method: str = "shap"


@router.post("/generate")
async def create_explanation(
    request: ExplanationRequest,
    background_tasks: BackgroundTasks,
    current_user: str = Depends(get_current_researcher)
):
    """
    Generate XAI explanation for a model using SHAP or LIME.
    
    Args:
        request: Explanation generation request
        background_tasks: FastAPI background tasks
        current_user: Authenticated user
        
    Returns:
        Explanation generation status
    """
    try:
        # Validate method
        if request.method.lower() not in ['shap', 'lime']:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported method: {request.method}. Use 'shap' or 'lime'."
            )
        
        # Validate model exists
        model = supabase_db.get_model(request.model_id)
        if not model:
            raise HTTPException(
                status_code=404,
                detail=f"Model {request.model_id} not found"
            )
        
        # Start explanation generation in background
        background_tasks.add_task(
            explanation_service.generate_explanation,
            request.model_id,
            request.method.lower(),
            request.sample_size
        )
        
        logger.info("Explanation generation queued",
                   model_id=request.model_id,
                   method=request.method)
        
        return {
            "message": "Explanation generation started",
            "model_id": request.model_id,
            "method": request.method,
            "status": "processing",
            "note": "Check status with GET /explanations/model/{model_id}"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to start explanation generation",
                    model_id=request.model_id,
                    error=str(e))
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/{explanation_id}")
async def get_explanation(
    explanation_id: str,
    current_user: str = Depends(get_current_researcher)
):
    """Get explanation by ID."""
    try:
        explanation = supabase_db.get_explanation(explanation_id)
        
        if not explanation:
            raise HTTPException(
                status_code=404,
                detail=f"Explanation {explanation_id} not found"
            )
        
        return explanation
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get explanation",
                    explanation_id=explanation_id,
                    error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/model/{model_id}")
async def get_model_explanations(
    model_id: str,
    current_user: str = Depends(get_current_researcher)
):
    """Get all explanations for a model."""
    try:
        explanations = supabase_db.list_explanations(model_id=model_id)
        return explanations
    
    except Exception as e:
        logger.error("Failed to get model explanations",
                    model_id=model_id,
                    error=str(e))
        return []


@router.get("/compare/{model_id}")
async def compare_explanations(
    model_id: str,
    current_user: str = Depends(get_current_researcher)
):
    """Compare SHAP and LIME explanations for a model."""
    try:
        # Get all completed explanations for this model
        all_explanations = supabase_db.list_explanations(model_id=model_id)
        explanations = [e for e in all_explanations if e.get('status') == 'completed']
        
        # Separate by method
        shap_exp = None
        lime_exp = None
        
        for exp in explanations:
            method = exp.get('method', 'unknown')
            if method == 'shap':
                shap_exp = exp
            elif method == 'lime':
                lime_exp = exp
        
        if not shap_exp or not lime_exp:
            raise HTTPException(
                status_code=404,
                detail="Both SHAP and LIME explanations required for comparison. Generate both first."
            )
        
        # Return both explanations for comparison
        return {
            "model_id": model_id,
            "shap": shap_exp,
            "lime": lime_exp
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to compare explanations",
                    model_id=model_id,
                    error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/local")
async def generate_local_explanation(
    request: LocalExplanationRequest,
    current_user: str = Depends(get_current_researcher)
):
    """
    Generate local (instance-level) SHAP explanation for a single sample.
    
    This computes SHAP values on-demand for one specific prediction,
    showing which features contributed to that individual decision.
    
    Args:
        request: Local explanation request with model_id and sample_index
        current_user: Authenticated user
        
    Returns:
        Local SHAP explanation with force plot data
    """
    try:
        from app.services.explanation_service import explanation_service
        import asyncio
        
        logger.info("Generating local explanation",
                   model_id=request.model_id,
                   sample_index=request.sample_index)
        
        # Run with timeout to prevent hanging
        try:
            result = await asyncio.wait_for(
                asyncio.to_thread(
                    explanation_service.generate_local_explanation,
                    request.model_id,
                    request.sample_index,
                    request.method
                ),
                timeout=30.0  # 30 second timeout
            )
            
            return {
                "status": "success",
                "model_id": request.model_id,
                "sample_index": request.sample_index,
                "method": request.method,
                "explanation": result
            }
            
        except asyncio.TimeoutError:
            raise HTTPException(
                status_code=504,
                detail="Explanation generation timed out. Try a different sample."
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to generate local explanation",
                    model_id=request.model_id,
                    sample_index=request.sample_index,
                    error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate local explanation: {str(e)}"
        )
