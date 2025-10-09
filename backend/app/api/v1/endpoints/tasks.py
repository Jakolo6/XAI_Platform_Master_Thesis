"""
Task status tracking endpoints.
"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status
from celery.result import AsyncResult
import structlog

from workers import celery_app

logger = structlog.get_logger()
router = APIRouter()


@router.get("/{task_id}", response_model=Dict[str, Any])
async def get_task_status(task_id: str):
    """
    Get the status of an async task.
    
    Args:
        task_id: Celery task ID
        
    Returns:
        Task status information
    """
    try:
        task_result = AsyncResult(task_id, app=celery_app)
        
        response = {
            "task_id": task_id,
            "status": task_result.state,
            "ready": task_result.ready(),
            "successful": task_result.successful() if task_result.ready() else None,
        }
        
        # Add result if task is complete
        if task_result.ready():
            if task_result.successful():
                response["result"] = task_result.result
            else:
                response["error"] = str(task_result.info)
        
        # Add progress info if available
        if task_result.state == 'PROGRESS':
            response["progress"] = task_result.info
        
        return response
        
    except Exception as e:
        logger.error("Failed to get task status", task_id=task_id, exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve task status: {str(e)}"
        )


@router.post("/{task_id}/cancel")
async def cancel_task(task_id: str):
    """
    Cancel a running task.
    
    Args:
        task_id: Celery task ID
        
    Returns:
        Cancellation confirmation
    """
    try:
        task_result = AsyncResult(task_id, app=celery_app)
        
        if not task_result.ready():
            task_result.revoke(terminate=True)
            logger.info("Task cancelled", task_id=task_id)
            
            return {
                "message": "Task cancelled successfully",
                "task_id": task_id,
                "status": "cancelled"
            }
        else:
            return {
                "message": "Task already completed",
                "task_id": task_id,
                "status": task_result.state
            }
            
    except Exception as e:
        logger.error("Failed to cancel task", task_id=task_id, exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel task: {str(e)}"
        )
