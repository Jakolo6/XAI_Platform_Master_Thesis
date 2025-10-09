"""
XAI explanation generation endpoints.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import uuid
import json
import redis

router = APIRouter()

# Use Redis for persistent storage
redis_client = redis.Redis(host='redis', port=6379, db=2, decode_responses=True)


@router.post("/generate")
async def create_explanation(
    model_id: str,
    method: str = "shap",
    config: Dict[str, Any] = {}
):
    """Generate XAI explanation for a model."""
    
    # Create explanation record in Redis
    explanation_id = str(uuid.uuid4())
    explanation_data = {
        "id": explanation_id,
        "model_id": model_id,
        "method": method,
        "status": "pending",
        "config": config,
        "result": None
    }
    redis_client.setex(
        f"explanation:{explanation_id}",
        3600,  # Expire after 1 hour
        json.dumps(explanation_data)
    )
    
    # Start async task
    from app.tasks.explanation_tasks import generate_explanation
    generate_explanation.delay(
        explanation_id=explanation_id,
        model_id=model_id,
        method=method,
        config=config
    )
    
    return {
        "id": explanation_id,
        "status": "pending",
        "message": "Explanation generation started"
    }


@router.get("/{explanation_id}")
async def get_explanation(explanation_id: str):
    """Get explanation by ID."""
    data = redis_client.get(f"explanation:{explanation_id}")
    
    if not data:
        raise HTTPException(status_code=404, detail="Explanation not found")
    
    return json.loads(data)


@router.get("/model/{model_id}")
async def get_model_explanations(model_id: str):
    """Get all explanations for a model."""
    # Scan all explanation keys
    explanations = []
    for key in redis_client.scan_iter(match="explanation:*"):
        data = redis_client.get(key)
        if data:
            exp = json.loads(data)
            if exp["model_id"] == model_id:
                explanations.append(exp)
    
    return explanations
