"""
XAI explanation generation endpoints.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
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


@router.get("/compare")
async def compare_explanations_query(model_id: str):
    """Compare SHAP and LIME explanations for a model (query parameter version)."""
    return await compare_explanations(model_id)


@router.get("/compare/{model_id}")
async def compare_explanations(model_id: str):
    """Compare SHAP and LIME explanations for a model."""
    # Get all explanations for this model
    explanations = []
    for key in redis_client.scan_iter(match="explanation:*"):
        data = redis_client.get(key)
        if data:
            exp = json.loads(data)
            if exp["model_id"] == model_id and exp["status"] == "completed":
                explanations.append(exp)
    
    # Separate by method
    shap_exp = None
    lime_exp = None
    
    for exp in explanations:
        result = json.loads(exp["result"])
        method = result.get("method", exp.get("method", "unknown"))
        if method == "shap":
            shap_exp = result
        elif method == "lime":
            lime_exp = result
    
    if not shap_exp or not lime_exp:
        raise HTTPException(
            status_code=404, 
            detail="Both SHAP and LIME explanations required for comparison"
        )
    
    # Calculate agreement metrics
    shap_features = {f["feature"]: f for f in shap_exp["feature_importance"][:20]}
    lime_features = {f["feature"]: f for f in lime_exp["feature_importance"][:20]}
    
    common_features = set(shap_features.keys()) & set(lime_features.keys())
    
    # Top-k agreement
    top_5_shap = set([f["feature"] for f in shap_exp["feature_importance"][:5]])
    top_5_lime = set([f["feature"] for f in lime_exp["feature_importance"][:5]])
    top_5_agreement = len(top_5_shap & top_5_lime) / 5
    
    top_10_shap = set([f["feature"] for f in shap_exp["feature_importance"][:10]])
    top_10_lime = set([f["feature"] for f in lime_exp["feature_importance"][:10]])
    top_10_agreement = len(top_10_shap & top_10_lime) / 10
    
    # Rank correlation for common features
    if len(common_features) > 0:
        shap_ranks = {f: i for i, f in enumerate([x["feature"] for x in shap_exp["feature_importance"]])}
        lime_ranks = {f: i for i, f in enumerate([x["feature"] for x in lime_exp["feature_importance"]])}
        
        from scipy.stats import spearmanr
        common_list = list(common_features)
        shap_rank_list = [shap_ranks[f] for f in common_list]
        lime_rank_list = [lime_ranks[f] for f in common_list]
        correlation, p_value = spearmanr(shap_rank_list, lime_rank_list)
    else:
        correlation = 0
        p_value = 1
    
    return {
        "model_id": model_id,
        "shap": shap_exp,
        "lime": lime_exp,
        "comparison": {
            "common_features": len(common_features),
            "top_5_agreement": float(top_5_agreement),
            "top_10_agreement": float(top_10_agreement),
            "rank_correlation": float(correlation),
            "p_value": float(p_value)
        }
    }


@router.post("/evaluate-quality/{explanation_id}")
async def evaluate_explanation_quality(explanation_id: str, background_tasks: BackgroundTasks):
    """
    Evaluate explanation quality using Quantus metrics.
    
    This endpoint triggers a background task to evaluate:
    - Faithfulness (monotonicity, selectivity)
    - Robustness (stability under perturbations)
    - Complexity (sparsity, interpretability)
    """
    # Get explanation
    data = redis_client.get(f"explanation:{explanation_id}")
    
    if not data:
        raise HTTPException(status_code=404, detail="Explanation not found")
    
    explanation = json.loads(data)
    
    if explanation["status"] != "completed":
        raise HTTPException(status_code=400, detail="Explanation not yet completed")
    
    # Create quality evaluation task ID
    eval_id = str(uuid.uuid4())
    
    # Store evaluation task in Redis
    eval_data = {
        "id": eval_id,
        "explanation_id": explanation_id,
        "status": "pending",
        "result": None
    }
    redis_client.setex(
        f"quality_eval:{eval_id}",
        3600,
        json.dumps(eval_data)
    )
    
    # Trigger Celery task for quality evaluation
    from app.tasks.explanation_tasks import evaluate_explanation_quality_task
    task = evaluate_explanation_quality_task.delay(eval_id, explanation_id)
    
    return {
        "id": eval_id,
        "status": "pending",
        "message": "Quality evaluation started",
        "task_id": task.id
    }


@router.get("/quality/{eval_id}")
async def get_quality_evaluation(eval_id: str):
    """Get quality evaluation results."""
    data = redis_client.get(f"quality_eval:{eval_id}")
    
    if not data:
        raise HTTPException(status_code=404, detail="Quality evaluation not found")
    
    return json.loads(data)


@router.get("/{explanation_id}/quality")
async def get_explanation_quality_metrics(explanation_id: str):
    """
    Get quality metrics for an explanation.
    Returns cached results if available, otherwise returns mock data for demo.
    """
    # Get explanation
    data = redis_client.get(f"explanation:{explanation_id}")
    
    if not data:
        raise HTTPException(status_code=404, detail="Explanation not found")
    
    explanation = json.loads(data)
    
    if explanation["status"] != "completed":
        raise HTTPException(status_code=400, detail="Explanation not yet completed")
    
    # Check if quality metrics already exist
    quality_key = f"quality:{explanation_id}"
    quality_data = redis_client.get(quality_key)
    
    if quality_data:
        return json.loads(quality_data)
    
    # Return demo metrics based on method
    method = explanation.get("method", "shap")
    
    if method == "shap":
        metrics = {
            "faithfulness": 0.85,
            "robustness": 0.92,
            "complexity": 0.73,
            "method": "shap"
        }
    else:  # lime
        metrics = {
            "faithfulness": 0.78,
            "robustness": 0.81,
            "complexity": 0.68,
            "method": "lime"
        }
    
    result = {
        "explanation_id": explanation_id,
        "model_id": explanation["model_id"],
        "method": method,
        "quality_metrics": metrics,
        "note": "Demo metrics - run full evaluation for accurate results"
    }
    
    # Cache the result
    redis_client.setex(quality_key, 3600, json.dumps(result))
    
    return result
