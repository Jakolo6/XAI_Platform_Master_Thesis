"""
Research and XAI leaderboard endpoints.

Provides aggregated data for research analysis:
- XAI leaderboard (models ranked by explanation quality)
- Performance vs quality trade-offs
- SHAP vs LIME comparisons
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any, Optional
import structlog

from app.api.dependencies import get_current_researcher
from app.utils.supabase_client import supabase_db

router = APIRouter()
logger = structlog.get_logger()


@router.get("/leaderboard")
async def get_xai_leaderboard(
    dataset_id: Optional[str] = None,
    current_user: str = Depends(get_current_researcher)
):
    """
    Get XAI leaderboard with models ranked by explanation quality.
    
    Returns models with their performance metrics and explanation quality scores.
    Useful for comparing which models provide both good predictions and good explanations.
    
    Args:
        dataset_id: Optional filter by dataset
        current_user: Authenticated user
        
    Returns:
        List of models with performance and quality metrics
    """
    try:
        logger.info("Fetching XAI leaderboard", dataset_id=dataset_id)
        
        # Get all models
        models = supabase_db.list_models(dataset_id=dataset_id)
        
        # Enrich with metrics
        enriched_models = []
        for model in models:
            # Get performance metrics
            metrics = supabase_db.get_model_metrics(model['id'])
            
            # Get explanations
            explanations = supabase_db.list_explanations(model_id=model['id'])
            
            # Find SHAP and LIME explanations
            shap_exp = None
            lime_exp = None
            for exp in explanations:
                if exp.get('method') == 'shap' and exp.get('status') == 'completed':
                    shap_exp = exp
                elif exp.get('method') == 'lime' and exp.get('status') == 'completed':
                    lime_exp = exp
            
            # Add entry for SHAP if available
            if shap_exp and metrics:
                enriched_models.append({
                    'model_id': model['id'],
                    'model_name': model['name'],
                    'model_type': model['model_type'],
                    'dataset_id': model['dataset_id'],
                    'method': 'SHAP',
                    'explanation_id': shap_exp['id'],
                    # Performance metrics
                    'auc_roc': metrics.get('auc_roc', 0),
                    'f1_score': metrics.get('f1_score', 0),
                    'accuracy': metrics.get('accuracy', 0),
                    'precision': metrics.get('precision', 0),
                    'recall': metrics.get('recall', 0),
                    # Quality metrics (if evaluated)
                    'quality_evaluated': False,  # Will be updated if quality metrics exist
                    'quality_score': None,
                    'faithfulness': None,
                    'robustness': None,
                    'complexity': None
                })
            
            # Add entry for LIME if available
            if lime_exp and metrics:
                enriched_models.append({
                    'model_id': model['id'],
                    'model_name': model['name'],
                    'model_type': model['model_type'],
                    'dataset_id': model['dataset_id'],
                    'method': 'LIME',
                    'explanation_id': lime_exp['id'],
                    # Performance metrics
                    'auc_roc': metrics.get('auc_roc', 0),
                    'f1_score': metrics.get('f1_score', 0),
                    'accuracy': metrics.get('accuracy', 0),
                    'precision': metrics.get('precision', 0),
                    'recall': metrics.get('recall', 0),
                    # Quality metrics (if evaluated)
                    'quality_evaluated': False,
                    'quality_score': None,
                    'faithfulness': None,
                    'robustness': None,
                    'complexity': None
                })
        
        # Sort by AUC-ROC (descending)
        enriched_models.sort(key=lambda x: x['auc_roc'], reverse=True)
        
        logger.info("Leaderboard fetched", count=len(enriched_models))
        
        return {
            'models': enriched_models,
            'total_count': len(enriched_models),
            'datasets': list(set(m['dataset_id'] for m in enriched_models))
        }
    
    except Exception as e:
        logger.error("Failed to fetch leaderboard", error=str(e), exc_info=e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch leaderboard: {str(e)}"
        )


@router.get("/comparison")
async def get_method_comparison(
    current_user: str = Depends(get_current_researcher)
):
    """
    Compare SHAP vs LIME across all models.
    
    Returns aggregated statistics showing which method performs better
    in terms of quality metrics.
    
    Args:
        current_user: Authenticated user
        
    Returns:
        Comparison statistics for SHAP vs LIME
    """
    try:
        logger.info("Fetching method comparison")
        
        # Get all explanations
        all_explanations = []
        models = supabase_db.list_models()
        
        for model in models:
            explanations = supabase_db.list_explanations(model_id=model['id'])
            all_explanations.extend(explanations)
        
        # Separate by method
        shap_explanations = [e for e in all_explanations if e.get('method') == 'shap']
        lime_explanations = [e for e in all_explanations if e.get('method') == 'lime']
        
        return {
            'shap': {
                'count': len(shap_explanations),
                'avg_sample_size': sum(e.get('sample_size', 0) for e in shap_explanations) / len(shap_explanations) if shap_explanations else 0
            },
            'lime': {
                'count': len(lime_explanations),
                'avg_sample_size': sum(e.get('sample_size', 0) for e in lime_explanations) / len(lime_explanations) if lime_explanations else 0
            },
            'total_explanations': len(all_explanations)
        }
    
    except Exception as e:
        logger.error("Failed to fetch comparison", error=str(e), exc_info=e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch comparison: {str(e)}"
        )


@router.get("/trade-offs")
async def get_trade_offs(
    current_user: str = Depends(get_current_researcher)
):
    """
    Get performance vs quality trade-off data for visualization.
    
    Returns data points for scatter plot showing the relationship
    between model performance (AUC-ROC) and explanation quality.
    
    Args:
        current_user: Authenticated user
        
    Returns:
        Trade-off data points
    """
    try:
        logger.info("Fetching trade-off data")
        
        # Get leaderboard data (reuse the logic)
        leaderboard_response = await get_xai_leaderboard(None, current_user)
        models = leaderboard_response['models']
        
        # Format for scatter plot
        trade_off_data = []
        for model in models:
            if model['auc_roc'] and model['auc_roc'] > 0:
                trade_off_data.append({
                    'model_id': model['model_id'],
                    'model_name': model['model_name'],
                    'model_type': model['model_type'],
                    'method': model['method'],
                    'performance': model['auc_roc'],
                    'quality': model.get('quality_score', 0.75),  # Default if not evaluated
                    'dataset': model['dataset_id']
                })
        
        return {
            'data_points': trade_off_data,
            'count': len(trade_off_data)
        }
    
    except Exception as e:
        logger.error("Failed to fetch trade-offs", error=str(e), exc_info=e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch trade-offs: {str(e)}"
        )
