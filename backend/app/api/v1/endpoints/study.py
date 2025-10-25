"""
Study API Endpoints - Master Thesis User Study
Handles study session creation, case delivery, and response collection.

Dataset: UCI German Credit (Statlog)
Model: german_credit_xgb
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import structlog

from app.services.study_service import study_service

router = APIRouter()
logger = structlog.get_logger()


# ============================================================================
# Request/Response Models
# ============================================================================

class SessionStartRequest(BaseModel):
    """Request to start a new study session."""
    participant_code: Optional[str] = None


class SessionStartResponse(BaseModel):
    """Response when starting a session."""
    session_id: str
    participant_code: str
    total_cases: int
    layer_assignments: list


class CaseRequest(BaseModel):
    """Request to get a specific case."""
    session_id: str
    case_index: int
    layer_assignment: str


class CaseResponse(BaseModel):
    """Response containing case data."""
    case_index: int
    session_id: str
    instance_id: str
    loan_data: Dict[str, Any]
    decision: Dict[str, Any]
    explanation: Dict[str, Any]
    explanation_layer: str


class CaseRatingRequest(BaseModel):
    """Request to submit ratings for a case."""
    session_id: str
    case_index: int
    instance_id: str
    explanation_layer: str
    trust: int = Field(..., ge=1, le=5, description="Trust rating (1-5)")
    understanding: int = Field(..., ge=1, le=5, description="Understanding rating (1-5)")
    usefulness: int = Field(..., ge=1, le=5, description="Usefulness rating (1-5)")
    mental_effort: int = Field(..., ge=1, le=5, description="Mental effort rating (1-5)")
    time_spent: float = Field(..., gt=0, description="Time spent on case in seconds")
    comments: Optional[str] = None
    decision_label: Optional[str] = None
    risk_score: Optional[float] = None
    explanation_data: Optional[Dict[str, Any]] = None  # Serialized explanation for audit


class FinalRankingRequest(BaseModel):
    """Request to submit final layer rankings."""
    session_id: str
    rankings: Dict[str, int] = Field(..., description="Map of layer_type to rank (1-4)")


# ============================================================================
# API Endpoints
# ============================================================================

@router.post("/session/start", response_model=SessionStartResponse)
async def start_study_session(request: SessionStartRequest):
    """
    Start a new study session.
    
    Creates a session with randomized layer assignments for 6 cases.
    Each participant sees all 4 explanation layers at least once.
    
    Returns:
        Session data with session_id and layer assignments
    """
    try:
        logger.info("Starting study session", participant_code=request.participant_code)
        
        session_data = study_service.create_study_session(
            participant_code=request.participant_code
        )
        
        return SessionStartResponse(
            session_id=session_data["session_id"],
            participant_code=session_data["participant_code"],
            total_cases=session_data["total_cases"],
            layer_assignments=session_data["layer_assignments"]
        )
        
    except Exception as e:
        logger.error("Failed to start study session", error=str(e), exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start study session: {str(e)}"
        )


@router.post("/case", response_model=CaseResponse)
async def get_study_case(request: CaseRequest):
    """
    Get a study case with loan data and explanation.
    
    Loads a sample from UCI German Credit dataset, generates SHAP explanation,
    and formats it according to the assigned explanation layer.
    
    Args:
        request: Case request with session_id, case_index, and layer_assignment
        
    Returns:
        Case data with loan information, decision, and formatted explanation
    """
    try:
        logger.info("Getting study case",
                   session_id=request.session_id,
                   case_index=request.case_index,
                   layer=request.layer_assignment)
        
        case_data = study_service.get_study_case(
            session_id=request.session_id,
            case_index=request.case_index,
            layer_assignment=request.layer_assignment
        )
        
        return CaseResponse(**case_data)
        
    except ValueError as e:
        logger.error("Invalid case request", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Failed to get study case", error=str(e), exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get study case: {str(e)}"
        )


@router.post("/response")
async def submit_case_response(request: CaseRatingRequest):
    """
    Submit participant's ratings for a case.
    
    Stores ratings in human_evaluations table and updates session progress.
    
    Args:
        request: Ratings including trust, understanding, usefulness, mental_effort
        
    Returns:
        Confirmation with progress update
    """
    try:
        logger.info("Submitting case response",
                   session_id=request.session_id,
                   case_index=request.case_index,
                   layer=request.explanation_layer)
        
        # Validate ratings
        if not all(1 <= rating <= 5 for rating in [
            request.trust,
            request.understanding,
            request.usefulness,
            request.mental_effort
        ]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="All ratings must be between 1 and 5"
            )
        
        result = study_service.save_case_response(
            session_id=request.session_id,
            case_index=request.case_index,
            instance_id=request.instance_id,
            explanation_layer=request.explanation_layer,
            ratings={
                "trust": request.trust,
                "understanding": request.understanding,
                "usefulness": request.usefulness,
                "mental_effort": request.mental_effort,
                "time_spent": request.time_spent,
                "comments": request.comments,
                "decision_label": request.decision_label,
                "risk_score": request.risk_score,
                "explanation_data": request.explanation_data  # Include serialized explanation
            }
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to submit case response", error=str(e), exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit response: {str(e)}"
        )


@router.get("/session/{session_id}/final")
async def get_final_comparison(session_id: str):
    """
    Get aggregated data for final comparison screen.
    
    Shows participant summary of all cases grouped by explanation layer.
    
    Args:
        session_id: Study session ID
        
    Returns:
        Summary data for comparison and ranking
    """
    try:
        logger.info("Getting final comparison data", session_id=session_id)
        
        comparison_data = study_service.get_final_comparison_data(session_id)
        
        return comparison_data
        
    except Exception as e:
        logger.error("Failed to get final comparison data", error=str(e), exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get comparison data: {str(e)}"
        )


@router.post("/session/{session_id}/ranking")
async def submit_final_ranking(session_id: str, request: FinalRankingRequest):
    """
    Submit participant's final ranking of explanation layers.
    
    Marks session as completed and stores layer preferences.
    
    Args:
        session_id: Study session ID
        request: Rankings mapping layer_type to rank (1-4)
        
    Returns:
        Confirmation
    """
    try:
        logger.info("Submitting final ranking",
                   session_id=session_id,
                   rankings=request.rankings)
        
        # Validate rankings
        ranks = list(request.rankings.values())
        if sorted(ranks) != [1, 2, 3, 4]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rankings must be 1, 2, 3, 4 (one of each)"
            )
        
        result = study_service.save_final_ranking(
            session_id=session_id,
            rankings=request.rankings
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to submit final ranking", error=str(e), exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit ranking: {str(e)}"
        )


@router.get("/session/{session_id}/progress")
async def get_session_progress(session_id: str):
    """
    Get current progress for a study session.
    
    Args:
        session_id: Study session ID
        
    Returns:
        Progress information
    """
    try:
        from app.utils.supabase_client import supabase_db
        
        if not supabase_db.is_available():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database not available"
            )
        
        result = supabase_db.client.table('study_sessions').select('*').eq('id', session_id).execute()
        
        if not result.data or len(result.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
        
        session = result.data[0]
        
        return {
            "session_id": session_id,
            "total_questions": session.get('total_questions', 6),
            "completed_questions": session.get('completed_questions', 0),
            "status": session.get('status', 'in_progress'),
            "progress_percentage": (session.get('completed_questions', 0) / session.get('total_questions', 6)) * 100
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get session progress", error=str(e), exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get progress: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check for study endpoints."""
    return {
        "status": "healthy",
        "service": "study",
        "dataset": "uci_german_credit",
        "model": "german_credit_xgb",
        "endpoints": [
            "POST /session/start",
            "POST /case",
            "POST /response",
            "GET /session/{id}/final",
            "POST /session/{id}/ranking",
            "GET /session/{id}/progress"
        ]
    }
