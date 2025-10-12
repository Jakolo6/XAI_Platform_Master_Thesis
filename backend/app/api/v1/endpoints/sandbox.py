"""
API endpoints for Explainability Sandbox.
Interactive XAI exploration and human interpretability study.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import uuid
from datetime import datetime
import structlog

from app.services.sandbox_service import sandbox_service
from app.schemas.sandbox import (
    SampleInstance,
    ExplanationData,
    WhatIfRequest,
    WhatIfResponse,
    InterpretabilityRating,
    RatingResponse
)
from app.utils.supabase_client import supabase_db

router = APIRouter()
logger = structlog.get_logger()


@router.get("/sample/{model_id}", response_model=SampleInstance)
async def get_sample_instance(model_id: str):
    """
    Get a random test sample with prediction for sandbox exploration.
    
    Args:
        model_id: ID of the trained model
        
    Returns:
        Sample instance with features, prediction, and true label
    """
    try:
        logger.info("API: Getting sample instance", model_id=model_id)
        result = sandbox_service.get_sample_instance(model_id)
        return result
        
    except ValueError as e:
        logger.error("Model not found", model_id=model_id, error=str(e))
        raise HTTPException(status_code=404, detail=str(e))
        
    except FileNotFoundError as e:
        logger.error("Data not found", model_id=model_id, error=str(e))
        raise HTTPException(
            status_code=404,
            detail=f"Test data not found for model {model_id}. Please ensure dataset is processed."
        )
        
    except Exception as e:
        logger.error("Failed to get sample", model_id=model_id, error=str(e))
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to load sample: {str(e)}"
        )


@router.get("/local/{model_id}/{instance_id}", response_model=ExplanationData)
async def get_local_explanation(
    model_id: str,
    instance_id: str,
    method: str = 'shap'
):
    """
    Get SHAP or LIME explanation for a specific instance.
    
    Args:
        model_id: ID of the trained model
        instance_id: ID of the sample instance (e.g., 'sample_42')
        method: Explanation method ('shap' or 'lime')
        
    Returns:
        Explanation data with feature contributions
    """
    try:
        logger.info("API: Getting local explanation", 
                   model_id=model_id, 
                   instance_id=instance_id,
                   method=method)
        
        if method.lower() == 'shap':
            result = sandbox_service.generate_shap_explanation(model_id, instance_id)
        elif method.lower() == 'lime':
            result = sandbox_service.generate_lime_explanation(model_id, instance_id)
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid method: {method}. Use 'shap' or 'lime'"
            )
        
        return result
        
    except ValueError as e:
        logger.error("Model not found", model_id=model_id, error=str(e))
        raise HTTPException(status_code=404, detail=str(e))
        
    except FileNotFoundError as e:
        logger.error("Data not found", model_id=model_id, error=str(e))
        raise HTTPException(
            status_code=404,
            detail=f"Test data not found for model {model_id}"
        )
        
    except Exception as e:
        logger.error("Failed to generate explanation", 
                    model_id=model_id, 
                    instance_id=instance_id,
                    method=method,
                    error=str(e))
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate explanation: {str(e)}"
        )


@router.post("/rating", response_model=RatingResponse)
async def submit_interpretability_rating(rating: InterpretabilityRating):
    """
    Submit human interpretability rating for research purposes.
    
    Args:
        rating: Rating data (clarity, trustworthiness, actionability)
        
    Returns:
        Rating ID and confirmation message
    """
    try:
        logger.info("API: Submitting rating", 
                   model_id=rating.model_id,
                   instance_id=rating.instance_id)
        
        # Generate unique rating ID
        rating_id = f"rating_{uuid.uuid4().hex[:12]}"
        
        # Save to database
        rating_data = {
            "rating_id": rating_id,
            "model_id": rating.model_id,
            "instance_id": rating.instance_id,
            "clarity": rating.clarity,
            "trustworthiness": rating.trustworthiness,
            "actionability": rating.actionability,
            "shap_method": rating.shap_method,
            "lime_method": rating.lime_method,
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = supabase_db.table('explanation_ratings').insert(rating_data).execute()
        
        logger.info("Rating saved", rating_id=rating_id)
        
        return RatingResponse(
            rating_id=rating_id,
            message="Rating saved successfully. Thank you for your feedback!"
        )
        
    except Exception as e:
        logger.error("Failed to save rating", error=str(e))
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to save rating: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint for sandbox service"""
    return {
        "status": "healthy",
        "service": "explainability_sandbox",
        "endpoints": [
            "GET /sample/{model_id}",
            "GET /local/{model_id}/{instance_id}",
            "POST /rating"
        ]
    }
