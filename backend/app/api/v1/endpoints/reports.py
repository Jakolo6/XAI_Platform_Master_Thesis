"""
Report generation and export endpoints.

Provides CSV and JSON exports for thesis documentation:
- Model performance reports
- Explanation quality reports
- Research leaderboard exports
- Comparison reports (SHAP vs LIME)
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from typing import Optional
import structlog
import io
import csv
import json
from datetime import datetime

from app.api.dependencies import get_current_researcher
from app.utils.supabase_client import supabase_db

router = APIRouter()
logger = structlog.get_logger()


@router.get("/model/{model_id}/csv")
async def export_model_csv(
    model_id: str,
    current_user: str = Depends(get_current_researcher)
):
    """
    Export model performance and metrics as CSV.
    
    Includes:
    - Model metadata
    - Performance metrics (AUC-ROC, F1, Precision, Recall)
    - Training information
    - Feature importance (top 20)
    
    Args:
        model_id: ID of the model to export
        current_user: Authenticated user
        
    Returns:
        CSV file download
    """
    try:
        logger.info("Exporting model CSV", model_id=model_id)
        
        # Get model and metrics
        model = supabase_db.get_model(model_id)
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        
        metrics = supabase_db.get_model_metrics(model_id)
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Metric', 'Value'])
        
        # Model info
        writer.writerow(['Model ID', model['id']])
        writer.writerow(['Model Name', model['name']])
        writer.writerow(['Model Type', model['model_type']])
        writer.writerow(['Dataset', model['dataset_id']])
        writer.writerow(['Status', model['status']])
        writer.writerow(['Training Time (seconds)', model.get('training_time_seconds', 'N/A')])
        writer.writerow([''])
        
        # Performance metrics
        if metrics:
            writer.writerow(['Performance Metrics', ''])
            writer.writerow(['AUC-ROC', metrics.get('auc_roc', 'N/A')])
            writer.writerow(['F1 Score', metrics.get('f1_score', 'N/A')])
            writer.writerow(['Precision', metrics.get('precision', 'N/A')])
            writer.writerow(['Recall', metrics.get('recall', 'N/A')])
            writer.writerow(['Accuracy', metrics.get('accuracy', 'N/A')])
            writer.writerow([''])
        
        # Feature importance
        if model.get('feature_importance'):
            writer.writerow(['Feature Importance', ''])
            writer.writerow(['Feature', 'Importance'])
            for feature, importance in list(model['feature_importance'].items())[:20]:
                writer.writerow([feature, importance])
        
        # Prepare response
        output.seek(0)
        filename = f"model_{model_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to export model CSV", model_id=model_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/explanation/{explanation_id}/csv")
async def export_explanation_csv(
    explanation_id: str,
    current_user: str = Depends(get_current_researcher)
):
    """
    Export explanation data as CSV.
    
    Includes:
    - Explanation metadata
    - Feature importance rankings
    - Method details
    
    Args:
        explanation_id: ID of the explanation to export
        current_user: Authenticated user
        
    Returns:
        CSV file download
    """
    try:
        logger.info("Exporting explanation CSV", explanation_id=explanation_id)
        
        # Get explanation
        explanation = supabase_db.get_explanation(explanation_id)
        if not explanation:
            raise HTTPException(status_code=404, detail="Explanation not found")
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(['Metric', 'Value'])
        writer.writerow(['Explanation ID', explanation['id']])
        writer.writerow(['Model ID', explanation['model_id']])
        writer.writerow(['Method', explanation['method']])
        writer.writerow(['Status', explanation['status']])
        writer.writerow(['Sample Size', explanation.get('sample_size', 'N/A')])
        writer.writerow([''])
        
        # Feature importance
        if explanation.get('feature_importance'):
            writer.writerow(['Feature Importance', ''])
            writer.writerow(['Rank', 'Feature', 'Importance'])
            for rank, (feature, importance) in enumerate(explanation['feature_importance'].items(), 1):
                writer.writerow([rank, feature, importance])
        
        output.seek(0)
        filename = f"explanation_{explanation_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to export explanation CSV", explanation_id=explanation_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/leaderboard/csv")
async def export_leaderboard_csv(
    dataset_id: Optional[str] = None,
    current_user: str = Depends(get_current_researcher)
):
    """
    Export research leaderboard as CSV.
    
    Includes all models with performance and quality metrics.
    
    Args:
        dataset_id: Optional filter by dataset
        current_user: Authenticated user
        
    Returns:
        CSV file download
    """
    try:
        logger.info("Exporting leaderboard CSV", dataset_id=dataset_id)
        
        # Get all models
        models = supabase_db.list_models(dataset_id=dataset_id)
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            'Model ID', 'Model Name', 'Model Type', 'Dataset',
            'AUC-ROC', 'F1 Score', 'Precision', 'Recall', 'Accuracy',
            'Training Time (s)', 'Status'
        ])
        
        # Data rows
        for model in models:
            metrics = supabase_db.get_model_metrics(model['id'])
            writer.writerow([
                model['id'],
                model['name'],
                model['model_type'],
                model['dataset_id'],
                metrics.get('auc_roc', 'N/A') if metrics else 'N/A',
                metrics.get('f1_score', 'N/A') if metrics else 'N/A',
                metrics.get('precision', 'N/A') if metrics else 'N/A',
                metrics.get('recall', 'N/A') if metrics else 'N/A',
                metrics.get('accuracy', 'N/A') if metrics else 'N/A',
                model.get('training_time_seconds', 'N/A'),
                model['status']
            ])
        
        output.seek(0)
        filename = f"leaderboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    except Exception as e:
        logger.error("Failed to export leaderboard CSV", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/comparison/{model_id}/json")
async def export_comparison_json(
    model_id: str,
    current_user: str = Depends(get_current_researcher)
):
    """
    Export SHAP vs LIME comparison as JSON.
    
    Includes both explanations side-by-side for analysis.
    
    Args:
        model_id: ID of the model
        current_user: Authenticated user
        
    Returns:
        JSON file download
    """
    try:
        logger.info("Exporting comparison JSON", model_id=model_id)
        
        # Get model
        model = supabase_db.get_model(model_id)
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        
        # Get explanations
        explanations = supabase_db.list_explanations(model_id=model_id)
        
        shap_exp = None
        lime_exp = None
        for exp in explanations:
            if exp.get('method') == 'shap' and exp.get('status') == 'completed':
                shap_exp = exp
            elif exp.get('method') == 'lime' and exp.get('status') == 'completed':
                lime_exp = exp
        
        # Create comparison report
        report = {
            'model': {
                'id': model['id'],
                'name': model['name'],
                'type': model['model_type'],
                'dataset': model['dataset_id']
            },
            'shap': shap_exp if shap_exp else {'status': 'not_available'},
            'lime': lime_exp if lime_exp else {'status': 'not_available'},
            'generated_at': datetime.now().isoformat()
        }
        
        # Convert to JSON
        json_str = json.dumps(report, indent=2)
        filename = f"comparison_{model_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        return StreamingResponse(
            iter([json_str]),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to export comparison JSON", model_id=model_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
