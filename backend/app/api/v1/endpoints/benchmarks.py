"""
Benchmark comparison endpoints.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
import structlog

from app.api.dependencies import get_current_researcher
from app.utils.supabase_client import supabase_db

router = APIRouter()
logger = structlog.get_logger()


class BenchmarkResponse(BaseModel):
    """Benchmark response schema."""
    dataset_id: str
    dataset_name: str
    models: Dict[str, Dict[str, Any]]


@router.get("/", response_model=List[BenchmarkResponse])
async def get_benchmarks(
    current_user = Depends(get_current_researcher)
):
    """
    Get cross-dataset benchmark results.
    
    Returns performance comparison across all datasets and models.
    """
    try:
        # Get all datasets
        datasets = supabase_db.list_datasets()
        
        # Get all models with metrics
        models = supabase_db.list_models()
        
        # Group by dataset
        benchmarks = []
        
        for dataset in datasets:
            dataset_id = dataset['id']
            dataset_name = dataset['name']
            
            # Get models for this dataset
            dataset_models = [m for m in models if m.get('dataset_id') == dataset_id]
            
            # Group by model type
            models_by_type = {}
            for model in dataset_models:
                model_type = model['model_type']
                
                if model_type not in models_by_type:
                    # Metrics are stored directly in the model object
                    models_by_type[model_type] = {
                        'model_id': model['id'],
                        'auc_roc': model.get('auc_roc'),
                        'auc_pr': model.get('auc_pr'),
                        'f1_score': model.get('f1_score'),
                        'precision': model.get('precision'),
                        'recall': model.get('recall'),
                        'accuracy': model.get('accuracy'),
                        'training_time_seconds': model.get('training_time_seconds'),
                        'model_size_mb': model.get('model_size_mb'),
                        'status': model.get('status')
                    }
            
            benchmarks.append(BenchmarkResponse(
                dataset_id=dataset_name,
                dataset_name=dataset.get('display_name', dataset_name),
                models=models_by_type
            ))
        
        logger.info("Benchmarks retrieved", count=len(benchmarks))
        return benchmarks
        
    except Exception as e:
        logger.error("Failed to get benchmarks", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve benchmarks: {str(e)}"
        )


@router.get("/compare", response_model=Dict[str, Any])
async def compare_models(
    dataset_ids: Optional[str] = None,
    model_types: Optional[str] = None,
    metric: str = "auc_roc",
    current_user = Depends(get_current_researcher)
):
    """
    Compare models across datasets.
    
    Args:
        dataset_ids: Comma-separated dataset IDs (optional, defaults to all)
        model_types: Comma-separated model types (optional, defaults to all)
        metric: Metric to compare (default: auc_roc)
    
    Returns:
        Comparison matrix with best performers
    """
    try:
        # Parse filters
        dataset_filter = dataset_ids.split(',') if dataset_ids else None
        model_filter = model_types.split(',') if model_types else None
        
        # Get all models
        models = supabase_db.list_models()
        
        # Build comparison matrix
        comparison = {}
        best_overall = {'model_type': None, 'dataset': None, 'score': 0}
        
        for model in models:
            dataset_id = model.get('dataset_id')
            model_type = model['model_type']
            
            # Apply filters
            if dataset_filter and dataset_id not in dataset_filter:
                continue
            if model_filter and model_type not in model_filter:
                continue
            
            # Get metrics
            try:
                metrics = supabase_db.get_model_metrics(model['id'])
                if not metrics:
                    continue
                
                score = metrics.get(metric)
                if score is None:
                    continue
                
                # Add to comparison
                if dataset_id not in comparison:
                    comparison[dataset_id] = {}
                
                if model_type not in comparison[dataset_id]:
                    comparison[dataset_id][model_type] = {
                        'score': score,
                        'model_id': model['id'],
                        'training_time': model.get('training_time_seconds')
                    }
                elif score > comparison[dataset_id][model_type]['score']:
                    comparison[dataset_id][model_type] = {
                        'score': score,
                        'model_id': model['id'],
                        'training_time': model.get('training_time_seconds')
                    }
                
                # Track best overall
                if score > best_overall['score']:
                    best_overall = {
                        'model_type': model_type,
                        'dataset': dataset_id,
                        'score': score,
                        'model_id': model['id']
                    }
            except:
                continue
        
        # Calculate averages per model type
        model_averages = {}
        for dataset_id, models_dict in comparison.items():
            for model_type, data in models_dict.items():
                if model_type not in model_averages:
                    model_averages[model_type] = {'scores': [], 'times': []}
                model_averages[model_type]['scores'].append(data['score'])
                if data.get('training_time'):
                    model_averages[model_type]['times'].append(data['training_time'])
        
        # Compute averages
        for model_type in model_averages:
            scores = model_averages[model_type]['scores']
            times = model_averages[model_type]['times']
            model_averages[model_type] = {
                'avg_score': sum(scores) / len(scores) if scores else 0,
                'avg_time': sum(times) / len(times) if times else 0,
                'count': len(scores)
            }
        
        logger.info("Model comparison complete", metric=metric)
        
        return {
            'metric': metric,
            'comparison': comparison,
            'best_overall': best_overall,
            'model_averages': model_averages,
            'datasets_compared': len(comparison),
            'models_compared': sum(len(m) for m in comparison.values())
        }
        
    except Exception as e:
        logger.error("Failed to compare models", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compare models: {str(e)}"
        )


@router.get("/leaderboard", response_model=List[Dict[str, Any]])
async def get_leaderboard(
    metric: str = "auc_roc",
    limit: int = 10,
    current_user = Depends(get_current_researcher)
):
    """
    Get global leaderboard across all datasets.
    
    Args:
        metric: Metric to rank by (default: auc_roc)
        limit: Number of top models to return
    
    Returns:
        Ranked list of best performing models
    """
    try:
        # Get all models
        models = supabase_db.list_models()
        
        # Collect models with metrics
        leaderboard = []
        
        for model in models:
            if model.get('status') != 'completed':
                continue
            
            try:
                metrics = supabase_db.get_model_metrics(model['id'])
                if not metrics:
                    continue
                
                score = metrics.get(metric)
                if score is None:
                    continue
                
                leaderboard.append({
                    'model_id': model['id'],
                    'model_name': model.get('name'),
                    'model_type': model['model_type'],
                    'dataset_id': model.get('dataset_id'),
                    'score': score,
                    'auc_roc': metrics.get('auc_roc'),
                    'f1_score': metrics.get('f1_score'),
                    'training_time_seconds': model.get('training_time_seconds'),
                    'model_size_mb': model.get('model_size_mb')
                })
            except:
                continue
        
        # Sort by score
        leaderboard.sort(key=lambda x: x['score'], reverse=True)
        
        # Add ranks
        for i, entry in enumerate(leaderboard[:limit], 1):
            entry['rank'] = i
        
        logger.info("Leaderboard retrieved", metric=metric, count=len(leaderboard))
        
        return leaderboard[:limit]
        
    except Exception as e:
        logger.error("Failed to get leaderboard", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve leaderboard: {str(e)}"
        )
