"""
Human Evaluation Study API Endpoints

Provides endpoints for conducting human evaluation studies of XAI methods.
Participants rate trust, understanding, and usefulness of explanations.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
import uuid
import random
import logging

# from app.core.database import get_db  # Not used - Supabase only

# Setup logger
logger = logging.getLogger(__name__)

# Placeholder auth functions (replace with actual auth when implemented)
async def get_current_user():
    """Placeholder for current user - returns None for now"""
    return None

async def get_current_researcher():
    """Placeholder for researcher auth - returns None for now"""
    return None

router = APIRouter()


# ============================================================================
# Pydantic Models
# ============================================================================

class StudyQuestionResponse(BaseModel):
    """Response model for a study question"""
    model_config = ConfigDict(protected_namespaces=())
    
    question_id: str
    model_id: str
    dataset_id: Optional[str]
    prediction_outcome: str
    prediction_confidence: float
    context_description: str
    method: str  # SHAP or LIME (randomized)
    explanation_data: Dict[str, Any]
    true_label: Optional[str] = None  # Hidden from participant


class EvaluationRequest(BaseModel):
    """Request model for submitting an evaluation"""
    model_config = ConfigDict(protected_namespaces=())
    
    question_id: str
    session_id: str
    model_id: str
    method: str
    trust_score: int = Field(..., ge=1, le=5)
    understanding_score: int = Field(..., ge=1, le=5)
    usefulness_score: int = Field(..., ge=1, le=5)
    time_spent: float = Field(..., gt=0)
    explanation_shown: bool = True
    comments: Optional[str] = None


class SessionStartRequest(BaseModel):
    """Request to start a new study session"""
    participant_code: Optional[str] = None
    num_questions: int = Field(default=10, ge=1, le=20)


class SessionResponse(BaseModel):
    """Response when starting a session"""
    session_id: str
    num_questions: int
    randomization_seed: int


class AggregatedResults(BaseModel):
    """Aggregated results for researchers"""
    model_config = ConfigDict(protected_namespaces=())
    
    model_id: str
    method: str
    num_evaluations: int
    mean_trust: float
    std_trust: float
    mean_understanding: float
    std_understanding: float
    mean_usefulness: float
    std_usefulness: float
    mean_time_spent: float
    composite_human_score: float


# ============================================================================
# Helper Functions
# ============================================================================

def generate_participant_code() -> str:
    """Generate anonymous participant code"""
    return f"P{uuid.uuid4().hex[:8].upper()}"


async def get_or_create_session(
    db: AsyncSession,
    user_id: Optional[str],
    participant_code: Optional[str],
    num_questions: int
) -> Dict[str, Any]:
    """Get existing session or create new one"""
    
    # For demo purposes, create new session
    # In production, check for existing incomplete sessions
    
    session_id = str(uuid.uuid4())
    randomization_seed = random.randint(1, 1000000)
    
    if not participant_code:
        participant_code = generate_participant_code()
    
    # In production, insert into study_sessions table
    # For now, return session data
    
    return {
        "session_id": session_id,
        "participant_code": participant_code,
        "num_questions": num_questions,
        "randomization_seed": randomization_seed,
        "started_at": datetime.utcnow().isoformat()
    }


def randomize_method(seed: int, question_index: int) -> str:
    """Deterministically randomize explanation method"""
    random.seed(seed + question_index)
    return random.choice(['SHAP', 'LIME'])


# ============================================================================
# API Endpoints
# ============================================================================

@router.post("/session/start", response_model=SessionResponse)
async def start_study_session(
    request: SessionStartRequest,
    current_user = Depends(get_current_user)
):
    """
    Start a new human evaluation study session.
    
    Creates a session with randomized question order and method assignment.
    """
    try:
        user_id = current_user.id if current_user else None
        
        session_data = await get_or_create_session(
            db=db,
            user_id=user_id,
            participant_code=request.participant_code,
            num_questions=request.num_questions
        )
        
        logger.info(
            "Study session started",
            session_id=session_data["session_id"],
            user_id=user_id,
            num_questions=request.num_questions
        )
        
        return SessionResponse(
            session_id=session_data["session_id"],
            num_questions=session_data["num_questions"],
            randomization_seed=session_data["randomization_seed"]
        )
        
    except Exception as e:
        logger.error("Failed to start study session", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start study session"
        )


@router.get("/session/{session_id}/questions", response_model=List[StudyQuestionResponse])
async def get_session_questions(
    session_id: str,
    num_questions: int = 10,
    randomization_seed: Optional[int] = None,
    current_user = Depends(get_current_user)
):
    """
    Get randomized study questions for a session.
    
    Returns a list of questions with pre-computed explanations.
    Method (SHAP/LIME) is randomized per question.
    """
    try:
        # For demo purposes, return mock questions
        # In production, fetch from study_questions table
        
        if not randomization_seed:
            randomization_seed = random.randint(1, 1000000)
        
        # Mock question data
        mock_questions = []
        
        for i in range(num_questions):
            method = randomize_method(randomization_seed, i)
            
            # Generate mock explanation data
            if method == 'SHAP':
                explanation_data = {
                    "feature_values": {
                        "TransactionAmt": 150.0,
                        "card1": 12345,
                        "addr1": 299.0,
                        "D1": 14.0,
                        "C1": 1.0
                    },
                    "shap_values": {
                        "TransactionAmt": 0.15,
                        "card1": -0.08,
                        "addr1": 0.12,
                        "D1": -0.05,
                        "C1": 0.03
                    },
                    "base_value": 0.035,
                    "prediction": 0.125
                }
            else:  # LIME
                explanation_data = {
                    "feature_weights": {
                        "TransactionAmt": 0.18,
                        "card1": -0.10,
                        "addr1": 0.14,
                        "D1": -0.06,
                        "C1": 0.04
                    },
                    "prediction": 0.125,
                    "intercept": 0.035
                }
            
            question = StudyQuestionResponse(
                question_id=str(uuid.uuid4()),
                model_id="xgboost_ieee_cis",
                dataset_id="ieee-cis-fraud",
                prediction_outcome="Fraud Detected" if i % 3 == 0 else "Legitimate Transaction",
                prediction_confidence=0.85 + (i * 0.01),
                context_description=f"Transaction #{1000 + i}: Online purchase of ${150 + i * 10}",
                method=method,
                explanation_data=explanation_data,
                true_label="fraud" if i % 3 == 0 else "legitimate"
            )
            
            mock_questions.append(question)
        
        logger.info(
            "Study questions generated",
            session_id=session_id,
            num_questions=len(mock_questions)
        )
        
        return mock_questions
        
    except Exception as e:
        logger.error("Failed to get study questions", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get study questions"
        )


@router.post("/response")
async def submit_evaluation(
    evaluation: EvaluationRequest,
    current_user = Depends(get_current_user)
):
    """
    Submit a participant's evaluation response.
    
    Stores ratings for trust, understanding, and usefulness.
    """
    try:
        user_id = current_user.id if current_user else None
        
        # In production, insert into human_evaluations table
        # For now, log the response
        
        logger.info(
            "Evaluation response submitted",
            session_id=evaluation.session_id,
            question_id=evaluation.question_id,
            model_id=evaluation.model_id,
            method=evaluation.method,
            trust=evaluation.trust_score,
            understanding=evaluation.understanding_score,
            usefulness=evaluation.usefulness_score,
            time_spent=evaluation.time_spent
        )
        
        # Calculate composite score
        composite_score = (
            evaluation.trust_score + 
            evaluation.understanding_score + 
            evaluation.usefulness_score
        ) / 3.0
        
        return {
            "status": "success",
            "message": "Evaluation recorded",
            "composite_score": composite_score,
            "question_id": evaluation.question_id
        }
        
    except Exception as e:
        logger.error("Failed to submit evaluation", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit evaluation"
        )


@router.get("/results/aggregated", response_model=List[AggregatedResults])
async def get_aggregated_results(
    model_id: Optional[str] = None,
    method: Optional[str] = None,
    current_user = Depends(get_current_researcher)
):
    """
    Get aggregated evaluation results (researcher only).
    
    Returns mean and standard deviation for all metrics,
    grouped by model and method.
    """
    try:
        # For demo purposes, return mock aggregated data
        # In production, query human_evaluation_summary view
        
        mock_results = [
            AggregatedResults(
                model_id="xgboost_ieee_cis",
                method="SHAP",
                num_evaluations=45,
                mean_trust=4.2,
                std_trust=0.8,
                mean_understanding=4.5,
                std_understanding=0.6,
                mean_usefulness=4.3,
                std_usefulness=0.7,
                mean_time_spent=28.5,
                composite_human_score=4.33
            ),
            AggregatedResults(
                model_id="xgboost_ieee_cis",
                method="LIME",
                num_evaluations=42,
                mean_trust=3.8,
                std_trust=0.9,
                mean_understanding=3.9,
                std_understanding=0.8,
                mean_usefulness=3.7,
                std_usefulness=0.9,
                mean_time_spent=32.1,
                composite_human_score=3.80
            ),
            AggregatedResults(
                model_id="random_forest_ieee_cis",
                method="SHAP",
                num_evaluations=38,
                mean_trust=4.0,
                std_trust=0.7,
                mean_understanding=4.2,
                std_understanding=0.7,
                mean_usefulness=4.1,
                std_usefulness=0.6,
                mean_time_spent=26.8,
                composite_human_score=4.10
            ),
            AggregatedResults(
                model_id="random_forest_ieee_cis",
                method="LIME",
                num_evaluations=40,
                mean_trust=3.6,
                std_trust=1.0,
                mean_understanding=3.7,
                std_understanding=0.9,
                mean_usefulness=3.5,
                std_usefulness=1.0,
                mean_time_spent=30.5,
                composite_human_score=3.60
            )
        ]
        
        # Filter by model_id and method if provided
        results = mock_results
        if model_id:
            results = [r for r in results if r.model_id == model_id]
        if method:
            results = [r for r in results if r.method == method]
        
        logger.info(
            "Aggregated results retrieved",
            num_results=len(results),
            model_id=model_id,
            method=method
        )
        
        return results
        
    except Exception as e:
        logger.error("Failed to get aggregated results", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get aggregated results"
        )


@router.get("/results/correlation")
async def get_human_quantitative_correlation(
    current_user = Depends(get_current_researcher)
):
    """
    Get correlation between human ratings and quantitative metrics.
    
    Calculates Spearman correlation between:
    - Human trust/understanding/usefulness
    - Quantitative faithfulness/robustness/complexity
    """
    try:
        # For demo purposes, return mock correlation data
        # In production, calculate from actual data
        
        correlation_data = {
            "SHAP": {
                "trust_vs_faithfulness": 0.72,
                "understanding_vs_complexity": 0.68,
                "usefulness_vs_robustness": 0.65,
                "composite_correlation": 0.68
            },
            "LIME": {
                "trust_vs_faithfulness": 0.58,
                "understanding_vs_complexity": 0.62,
                "usefulness_vs_robustness": 0.54,
                "composite_correlation": 0.58
            },
            "overall_alignment": 0.63,
            "interpretation": "Moderate positive correlation between human perception and quantitative metrics"
        }
        
        logger.info("Correlation analysis retrieved")
        
        return correlation_data
        
    except Exception as e:
        logger.error("Failed to get correlation analysis", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get correlation analysis"
        )


@router.get("/session/{session_id}/progress")
async def get_session_progress(
    session_id: str,
    current_user = Depends(get_current_user)
):
    """
    Get progress for a study session.
    
    Returns number of completed questions and total questions.
    """
    try:
        # For demo purposes, return mock progress
        # In production, query study_sessions table
        
        progress = {
            "session_id": session_id,
            "total_questions": 10,
            "completed_questions": 3,
            "progress_percentage": 30.0,
            "status": "in_progress"
        }
        
        return progress
        
    except Exception as e:
        logger.error("Failed to get session progress", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get session progress"
        )
