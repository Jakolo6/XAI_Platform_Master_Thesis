"""
Local test for explanation generation to diagnose issues.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.explanation_service import explanation_service
import structlog

structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(),
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
)

logger = structlog.get_logger()

def test_explanation():
    """Test explanation generation locally."""
    
    model_id = "ieee-cis-fraud_xgboost_413d3682"
    
    logger.info("Testing explanation generation", model_id=model_id)
    
    try:
        result = explanation_service.generate_explanation(
            model_id=model_id,
            method="shap",
            sample_size=10  # Small sample for testing
        )
        
        logger.info("Explanation generated successfully", result=result)
        return result
        
    except Exception as e:
        logger.error("Explanation generation failed", error=str(e), exc_info=e)
        raise

if __name__ == "__main__":
    test_explanation()
