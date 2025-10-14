"""
Interpretation Layer API endpoints.

Provides both LLM-driven and rule-based interpretation of SHAP values.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional, Literal
from pydantic import BaseModel, ConfigDict
import structlog

from app.api.dependencies import get_current_researcher
from app.services.interpretation_service import interpretation_service
from app.utils.supabase_client import supabase_db
from app.core.data_access import dal

router = APIRouter()
logger = structlog.get_logger()


class InterpretationRequest(BaseModel):
    """Request schema for generating interpretations."""
    model_config = ConfigDict(protected_namespaces=())
    
    model_id: str
    shap_data: Dict[str, Any]
    mode: Literal["llm", "rule-based"] = "rule-based"


class InterpretationFeedback(BaseModel):
    """Feedback schema for interpretation quality."""
    model_config = ConfigDict(protected_namespaces=())
    
    interpretation_id: str
    model_id: str
    mode: str
    clarity: int  # 1-5
    trustworthiness: int  # 1-5
    fairness: int  # 1-5
    comments: Optional[str] = None


@router.post("/generate")
async def generate_interpretation(
    request: InterpretationRequest,
    current_user: str = Depends(get_current_researcher)
):
    """
    Generate human-readable interpretation from SHAP data.
    
    Supports two modes:
    - llm: Uses OpenAI GPT-4 for natural language generation
    - rule-based: Uses deterministic SHAP reasoning rules
    
    Args:
        request: Interpretation request with model_id, SHAP data, and mode
        current_user: Authenticated user
        
    Returns:
        Interpretation text and metadata
    """
    try:
        # Strip _metrics suffix if present
        base_model_id = request.model_id.replace('_metrics', '')
        
        # Get model context via DAL
        model = dal.get_model(base_model_id, include_metrics=False)
        if not model:
            raise HTTPException(status_code=404, detail=f"Model {request.model_id} not found")
        
        model_context = {
            "model_type": model.get("model_type"),
            "dataset_id": model.get("dataset_id"),
            "name": model.get("name")
        }
        
        # Generate interpretation
        logger.info("Generating interpretation",
                   model_id=request.model_id,
                   mode=request.mode)
        
        result = interpretation_service.generate_interpretation(
            shap_data=request.shap_data,
            mode=request.mode,
            model_context=model_context
        )
        
        logger.info("Interpretation generated successfully",
                   model_id=request.model_id,
                   mode=request.mode)
        
        return result
        
    except ValueError as e:
        logger.error("Invalid request", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Failed to generate interpretation",
                    model_id=request.model_id,
                    error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/local")
async def generate_local_interpretation(
    model_id: str,
    instance_id: str,
    shap_data: Dict[str, Any],
    mode: Literal["llm", "rule-based", "both"] = "both",
    current_user: str = Depends(get_current_researcher)
):
    """
    Generate human-readable interpretation for a local (instance-level) explanation.
    
    This endpoint supports dual interpretation paradigms:
    - Rule-based: Deterministic SHAP reasoning
    - LLM-based: Natural language generation via GPT-4
    - Both: Side-by-side comparison
    
    Args:
        model_id: Model identifier
        instance_id: Sample instance identifier
        shap_data: SHAP explanation data
        mode: Interpretation mode ("llm", "rule-based", or "both")
        current_user: Authenticated user
        
    Returns:
        Interpretation(s) with metadata
    """
    try:
        # Strip _metrics suffix if present
        base_model_id = model_id.replace('_metrics', '')
        
        # Get model context via DAL
        model = dal.get_model(base_model_id, include_metrics=False)
        if not model:
            raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
        
        model_context = {
            "model_type": model.get("model_type"),
            "dataset_id": model.get("dataset_id"),
            "name": model.get("name")
        }
        
        logger.info("Generating local interpretation",
                   model_id=model_id,
                   instance_id=instance_id,
                   mode=mode)
        
        if mode == "both":
            # Generate both interpretations
            llm_result = interpretation_service.generate_interpretation(
                shap_data=shap_data,
                mode="llm",
                model_context=model_context
            )
            
            rule_based_result = interpretation_service.generate_interpretation(
                shap_data=shap_data,
                mode="rule-based",
                model_context=model_context
            )
            
            return {
                "llm_based": llm_result,
                "rule_based": rule_based_result,
                "metadata": {
                    "model_id": base_model_id,
                    "instance_id": instance_id,
                    "model_context": model_context
                }
            }
        else:
            # Generate single interpretation
            result = interpretation_service.generate_interpretation(
                shap_data=shap_data,
                mode=mode,
                model_context=model_context
            )
            
            return {
                mode.replace("-", "_"): result,
                "metadata": {
                    "model_id": base_model_id,
                    "instance_id": instance_id,
                    "model_context": model_context
                }
            }
        
    except Exception as e:
        logger.error("Failed to generate local interpretation",
                    model_id=model_id,
                    instance_id=instance_id,
                    error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare")
async def compare_interpretations(
    model_id: str,
    shap_data: Dict[str, Any],
    current_user: str = Depends(get_current_researcher)
):
    """
    Generate both LLM and rule-based interpretations for comparison.
    
    Args:
        model_id: Model identifier (with or without _metrics suffix)
        shap_data: SHAP explanation data
        current_user: Authenticated user
        
    Returns:
        Both interpretations side-by-side
    """
    try:
        # Strip _metrics suffix if present
        base_model_id = model_id.replace('_metrics', '')
        
        # Get model context via DAL
        model = dal.get_model(base_model_id, include_metrics=False)
        if not model:
            raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
        
        model_context = {
            "model_type": model.get("model_type"),
            "dataset_id": model.get("dataset_id"),
            "name": model.get("name")
        }
        
        logger.info("Generating both interpretations for comparison", model_id=model_id)
        
        # Generate both interpretations
        llm_result = interpretation_service.generate_interpretation(
            shap_data=shap_data,
            mode="llm",
            model_context=model_context
        )
        
        rule_based_result = interpretation_service.generate_interpretation(
            shap_data=shap_data,
            mode="rule-based",
            model_context=model_context
        )
        
        return {
            "llm": llm_result,
            "rule_based": rule_based_result,
            "model_context": model_context
        }
        
    except Exception as e:
        logger.error("Failed to generate comparison",
                    model_id=model_id,
                    error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback")
async def submit_feedback(
    feedback: InterpretationFeedback,
    current_user: str = Depends(get_current_researcher)
):
    """
    Submit feedback on interpretation quality.
    
    This data is used for master's thesis research on interpretability.
    
    Args:
        feedback: User ratings and comments
        current_user: Authenticated user
        
    Returns:
        Confirmation message
    """
    try:
        # Save feedback to Supabase
        feedback_data = {
            "interpretation_id": feedback.interpretation_id,
            "model_id": feedback.model_id,
            "mode": feedback.mode,
            "clarity": feedback.clarity,
            "trustworthiness": feedback.trustworthiness,
            "fairness": feedback.fairness,
            "comments": feedback.comments,
            "user_id": current_user
        }
        
        # Save via DAL
        dal.save_interpretation_feedback(feedback_data, source_module="interpretation_endpoint")
        logger.info("Feedback saved", interpretation_id=feedback.interpretation_id)
        
        return {
            "status": "success",
            "message": "Thank you for your feedback!"
        }
        
    except Exception as e:
        logger.error("Failed to save feedback", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/model/{model_id}/shap")
async def get_model_shap_data(
    model_id: str,
    current_user: str = Depends(get_current_researcher)
):
    """
    Get SHAP explanation data for a model.
    
    Args:
        model_id: Model identifier (with or without _metrics suffix)
        current_user: Authenticated user
        
    Returns:
        SHAP explanation data
    """
    try:
        # Strip _metrics suffix if present (models table has it, explanations don't)
        base_model_id = model_id.replace('_metrics', '')
        
        logger.info("Fetching SHAP data", model_id=model_id, base_model_id=base_model_id)
        
        # Get SHAP explanation via DAL
        shap_explanation = dal.get_explanation(base_model_id, method='shap', status='completed')
        
        if not shap_explanation:
            # Provide helpful error message
            logger.warning("No SHAP explanation found", 
                          model_id=model_id, 
                          base_model_id=base_model_id)
            
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "No SHAP explanation found for this model",
                    "model_id": base_model_id,
                    "help": "This model doesn't have a SHAP explanation yet. Please train a new model (SHAP is auto-generated) or select a different model."
                }
            )
        
        logger.info("SHAP explanation found", model_id=base_model_id)
        return shap_explanation
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get SHAP data", model_id=model_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
