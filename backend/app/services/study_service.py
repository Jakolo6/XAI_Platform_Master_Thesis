"""
Study Service - Master Thesis User Study Flow
Handles study session management, case generation, and response logging.

Dataset: UCI German Credit (Statlog) - 1000 rows, 20 features
Model: german_credit_xgb (XGBoost trained on German Credit)
"""

import uuid
import random
from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog

from app.services.sandbox_service import sandbox_service
from app.utils.supabase_client import supabase_db

logger = structlog.get_logger()

# Study configuration
STUDY_MODEL_ID = "german_credit_xgb"
STUDY_DATASET_ID = "uci_german_credit"
NUM_CASES_PER_SESSION = 6
EXPLANATION_LAYERS = ["layer_1", "layer_2", "layer_3", "layer_4"]


class StudyService:
    """Service for managing user study sessions and case generation."""
    
    def __init__(self):
        """Initialize study service."""
        self._case_cache = {}  # Cache generated cases to ensure consistency
    
    def create_study_session(self, participant_code: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new study session.
        
        Args:
            participant_code: Optional participant identifier
            
        Returns:
            Session data with session_id, participant_code, and randomization_seed
        """
        try:
            session_id = str(uuid.uuid4())
            randomization_seed = random.randint(1, 1000000)
            
            if not participant_code:
                participant_code = f"P{uuid.uuid4().hex[:8].upper()}"
            
            # Pre-assign explanation layers for all 6 cases
            # Each participant sees all 4 layers at least once (6 cases, 4 layers)
            # Randomize the order based on seed
            random.seed(randomization_seed)
            layer_assignments = []
            
            # Ensure each layer appears at least once
            layer_assignments.extend(EXPLANATION_LAYERS)
            
            # Fill remaining slots (6 - 4 = 2) with random layers
            for _ in range(NUM_CASES_PER_SESSION - len(EXPLANATION_LAYERS)):
                layer_assignments.append(random.choice(EXPLANATION_LAYERS))
            
            # Shuffle the assignments
            random.shuffle(layer_assignments)
            
            # Create session in database
            session_data = {
                "id": session_id,
                "participant_code": participant_code,
                "started_at": datetime.utcnow().isoformat(),
                "total_questions": NUM_CASES_PER_SESSION,
                "completed_questions": 0,
                "randomization_seed": randomization_seed,
                "status": "in_progress"
            }
            
            if supabase_db.is_available():
                result = supabase_db.client.table('study_sessions').insert(session_data).execute()
                logger.info("Study session created", 
                           session_id=session_id,
                           participant_code=participant_code,
                           seed=randomization_seed)
            else:
                logger.warning("Supabase not available, session not persisted")
            
            return {
                "session_id": session_id,
                "participant_code": participant_code,
                "randomization_seed": randomization_seed,
                "total_cases": NUM_CASES_PER_SESSION,
                "layer_assignments": layer_assignments
            }
            
        except Exception as e:
            logger.error("Failed to create study session", error=str(e), exc_info=e)
            raise
    
    def get_study_case(
        self, 
        session_id: str, 
        case_index: int,
        layer_assignment: str
    ) -> Dict[str, Any]:
        """
        Get a study case with loan data, model decision, and explanation.
        
        Args:
            session_id: Study session ID
            case_index: Case number (0-5)
            layer_assignment: Which explanation layer to use (layer_1, layer_2, layer_3, layer_4)
            
        Returns:
            Case data with loan features, decision, and formatted explanation
        """
        try:
            # Use deterministic sample selection based on session_id and case_index
            # This ensures the same participant always sees the same cases
            cache_key = f"{session_id}_{case_index}"
            
            if cache_key in self._case_cache:
                logger.info("Using cached case", cache_key=cache_key)
                case_data = self._case_cache[cache_key]
            else:
                # Get a sample instance from the German Credit dataset
                sample_instance = sandbox_service.get_sample_instance(STUDY_MODEL_ID)
                
                # Generate SHAP explanation for this instance
                shap_explanation = sandbox_service.generate_shap_explanation(
                    STUDY_MODEL_ID,
                    sample_instance["instance_id"]
                )
                
                case_data = {
                    "instance_id": sample_instance["instance_id"],
                    "features": sample_instance["features"],
                    "prediction": sample_instance["prediction"],
                    "model_output": sample_instance["model_output"],
                    "true_label": sample_instance.get("true_label"),
                    "shap_explanation": shap_explanation
                }
                
                # Cache for consistency
                self._case_cache[cache_key] = case_data
            
            # Format the explanation according to the assigned layer
            formatted_explanation = self._format_explanation_for_layer(
                case_data["shap_explanation"],
                case_data["features"],
                case_data["prediction"],
                layer_assignment
            )
            
            logger.info("Study case generated",
                       session_id=session_id,
                       case_index=case_index,
                       layer=layer_assignment,
                       instance_id=case_data["instance_id"])
            
            return {
                "case_index": case_index,
                "session_id": session_id,
                "instance_id": case_data["instance_id"],
                "loan_data": self._format_loan_data(case_data["features"]),
                "decision": {
                    "approved": case_data["prediction"] < 0.5,  # Lower prob = good credit
                    "risk_score": case_data["prediction"],
                    "confidence": abs(case_data["prediction"] - 0.5) * 2,  # 0-1 scale
                    "label": case_data["model_output"]
                },
                "explanation": formatted_explanation,
                "explanation_layer": layer_assignment
            }
            
        except Exception as e:
            logger.error("Failed to generate study case",
                        session_id=session_id,
                        case_index=case_index,
                        error=str(e),
                        exc_info=e)
            raise
    
    def _format_loan_data(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format raw feature values into human-readable loan application data.
        
        Args:
            features: Raw feature dictionary from model
            
        Returns:
            Formatted loan data with readable labels
        """
        # Map technical feature names to human-readable labels
        # Note: Actual feature names depend on preprocessing
        # This is a template - adjust based on actual German Credit features
        
        loan_data = {
            "applicant_info": {},
            "loan_details": {},
            "financial_status": {},
            "other_info": {}
        }
        
        # Extract and categorize features
        for feature_name, value in features.items():
            # Format the value
            if isinstance(value, float):
                formatted_value = round(value, 2)
            else:
                formatted_value = value
            
            # Categorize by feature name patterns
            # (These mappings should be adjusted based on actual feature names)
            if 'age' in feature_name.lower():
                loan_data["applicant_info"]["Age"] = formatted_value
            elif 'duration' in feature_name.lower():
                loan_data["loan_details"]["Duration (months)"] = formatted_value
            elif 'credit_amount' in feature_name.lower() or 'amount' in feature_name.lower():
                loan_data["loan_details"]["Credit Amount"] = formatted_value
            elif 'employment' in feature_name.lower():
                loan_data["applicant_info"]["Employment Length"] = formatted_value
            elif 'housing' in feature_name.lower():
                loan_data["applicant_info"]["Housing"] = formatted_value
            elif 'checking' in feature_name.lower():
                loan_data["financial_status"]["Checking Account"] = formatted_value
            elif 'savings' in feature_name.lower():
                loan_data["financial_status"]["Savings Account"] = formatted_value
            elif 'installment' in feature_name.lower():
                loan_data["loan_details"]["Installment Rate"] = formatted_value
            elif 'job' in feature_name.lower():
                loan_data["applicant_info"]["Job Type"] = formatted_value
            else:
                loan_data["other_info"][feature_name] = formatted_value
        
        return loan_data
    
    def _format_explanation_for_layer(
        self,
        shap_explanation: Dict[str, Any],
        features: Dict[str, Any],
        prediction: float,
        layer: str
    ) -> Dict[str, Any]:
        """
        Format SHAP explanation according to the assigned interpretational layer.
        
        This is where the 4 different explanation styles will be implemented.
        For now, returns a base structure that each layer renderer will use.
        
        Args:
            shap_explanation: Raw SHAP explanation data
            features: Feature values
            prediction: Model prediction probability
            layer: Which layer to use (layer_1, layer_2, layer_3, layer_4)
            
        Returns:
            Formatted explanation ready for frontend rendering
        """
        
        # Extract top features by importance
        top_features = shap_explanation["features"][:5]  # Top 5 most important
        
        base_explanation = {
            "layer_type": layer,
            "prediction_proba": shap_explanation["prediction_proba"],
            "base_value": shap_explanation.get("base_value", 0.0),
            "top_features": top_features,
            "all_features": shap_explanation["features"]
        }
        
        # ============================================================================
        # TODO: Implement 4 different explanation layer renderers
        # ============================================================================
        # 
        # Layer 1: [DEFINE YOUR FIRST INTERPRETATION STYLE]
        # - Example: Simple feature list with +/- indicators
        # - Format: List of "Feature X increases/decreases risk by Y"
        #
        # Layer 2: [DEFINE YOUR SECOND INTERPRETATION STYLE]
        # - Example: Natural language narrative
        # - Format: Paragraph explaining the decision
        #
        # Layer 3: [DEFINE YOUR THIRD INTERPRETATION STYLE]
        # - Example: Visual bar chart data
        # - Format: Structured data for bar chart rendering
        #
        # Layer 4: [DEFINE YOUR FOURTH INTERPRETATION STYLE]
        # - Example: Counterfactual explanations
        # - Format: "If feature X was Y, decision would change"
        #
        # ============================================================================
        
        if layer == "layer_1":
            # Placeholder for Layer 1 rendering
            base_explanation["rendered_content"] = {
                "type": "feature_list",
                "title": "Key Factors (Layer 1 - Placeholder)",
                "items": [
                    {
                        "feature": f["feature"],
                        "contribution": f["contribution"],
                        "direction": "increases risk" if f["contribution"] > 0 else "decreases risk"
                    }
                    for f in top_features
                ]
            }
        
        elif layer == "layer_2":
            # Placeholder for Layer 2 rendering
            base_explanation["rendered_content"] = {
                "type": "narrative",
                "title": "Decision Explanation (Layer 2 - Placeholder)",
                "text": f"The model predicts a risk score of {prediction:.2%}. This is based on multiple factors..."
            }
        
        elif layer == "layer_3":
            # Placeholder for Layer 3 rendering
            base_explanation["rendered_content"] = {
                "type": "visual_chart",
                "title": "Feature Contributions (Layer 3 - Placeholder)",
                "chart_data": [
                    {
                        "feature": f["feature"],
                        "value": f["contribution"]
                    }
                    for f in top_features
                ]
            }
        
        elif layer == "layer_4":
            # Placeholder for Layer 4 rendering
            base_explanation["rendered_content"] = {
                "type": "counterfactual",
                "title": "What-If Scenarios (Layer 4 - Placeholder)",
                "scenarios": [
                    {
                        "feature": f["feature"],
                        "current_value": features.get(f["feature"], "N/A"),
                        "suggestion": "Placeholder counterfactual"
                    }
                    for f in top_features[:3]
                ]
            }
        
        return base_explanation
    
    def save_case_response(
        self,
        session_id: str,
        case_index: int,
        instance_id: str,
        explanation_layer: str,
        ratings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Save participant's response for a case.
        
        Args:
            session_id: Study session ID
            case_index: Case number (0-5)
            instance_id: Sample instance ID
            explanation_layer: Which layer was shown
            ratings: Dictionary with trust, understanding, usefulness, mental_effort, comments
            
        Returns:
            Confirmation with evaluation_id
        """
        try:
            evaluation_id = str(uuid.uuid4())
            
            # Get session info for participant_code
            session = None
            if supabase_db.is_available():
                result = supabase_db.client.table('study_sessions').select('*').eq('id', session_id).execute()
                if result.data and len(result.data) > 0:
                    session = result.data[0]
            
            participant_code = session.get('participant_code') if session else f"UNKNOWN_{session_id[:8]}"
            
            # Create evaluation record
            evaluation_data = {
                "id": evaluation_id,
                "session_id": session_id,
                "participant_code": participant_code,
                "model_id": STUDY_MODEL_ID,
                "question_id": str(uuid.uuid4()),  # Generate question_id
                "method": explanation_layer,  # Store layer type in method field
                "prediction_outcome": ratings.get("decision_label", "Unknown"),
                "prediction_confidence": ratings.get("risk_score", 0.0),
                "trust_score": ratings["trust"],
                "understanding_score": ratings["understanding"],
                "usefulness_score": ratings["usefulness"],
                "time_spent": ratings.get("time_spent", 0.0),
                "comments": ratings.get("comments", ""),
                "explanation_shown": True,
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Save to database
            if supabase_db.is_available():
                result = supabase_db.client.table('human_evaluations').insert(evaluation_data).execute()
                
                # Update session progress
                completed = (session.get('completed_questions', 0) + 1) if session else case_index + 1
                supabase_db.client.table('study_sessions').update({
                    'completed_questions': completed
                }).eq('id', session_id).execute()
                
                logger.info("Case response saved",
                           session_id=session_id,
                           case_index=case_index,
                           evaluation_id=evaluation_id,
                           layer=explanation_layer)
            else:
                logger.warning("Supabase not available, response not persisted")
            
            return {
                "status": "success",
                "evaluation_id": evaluation_id,
                "case_index": case_index,
                "completed": case_index + 1,
                "total": NUM_CASES_PER_SESSION
            }
            
        except Exception as e:
            logger.error("Failed to save case response",
                        session_id=session_id,
                        case_index=case_index,
                        error=str(e),
                        exc_info=e)
            raise
    
    def get_final_comparison_data(self, session_id: str) -> Dict[str, Any]:
        """
        Get aggregated data for final comparison screen.
        
        Shows participant which layers they saw and prepares ranking interface.
        
        Args:
            session_id: Study session ID
            
        Returns:
            Summary of all cases and layers for comparison
        """
        try:
            # Get all evaluations for this session
            evaluations = []
            if supabase_db.is_available():
                result = supabase_db.client.table('human_evaluations').select('*').eq('session_id', session_id).execute()
                evaluations = result.data if result.data else []
            
            # Group by explanation layer
            layer_summary = {}
            for layer in EXPLANATION_LAYERS:
                layer_evals = [e for e in evaluations if e.get('method') == layer]
                if layer_evals:
                    layer_summary[layer] = {
                        "layer_type": layer,
                        "num_cases": len(layer_evals),
                        "avg_trust": sum(e['trust_score'] for e in layer_evals) / len(layer_evals),
                        "avg_understanding": sum(e['understanding_score'] for e in layer_evals) / len(layer_evals),
                        "avg_usefulness": sum(e['usefulness_score'] for e in layer_evals) / len(layer_evals),
                        "cases": [
                            {
                                "case_index": i,
                                "trust": e['trust_score'],
                                "understanding": e['understanding_score'],
                                "usefulness": e['usefulness_score']
                            }
                            for i, e in enumerate(layer_evals)
                        ]
                    }
            
            logger.info("Final comparison data generated",
                       session_id=session_id,
                       num_layers=len(layer_summary))
            
            return {
                "session_id": session_id,
                "total_cases": len(evaluations),
                "layer_summary": layer_summary,
                "layers_shown": list(layer_summary.keys())
            }
            
        except Exception as e:
            logger.error("Failed to get final comparison data",
                        session_id=session_id,
                        error=str(e),
                        exc_info=e)
            raise
    
    def save_final_ranking(
        self,
        session_id: str,
        rankings: Dict[str, int]
    ) -> Dict[str, Any]:
        """
        Save participant's final ranking of explanation layers.
        
        Args:
            session_id: Study session ID
            rankings: Dictionary mapping layer_type to rank (1-4)
            
        Returns:
            Confirmation
        """
        try:
            # For now, store in study_sessions as JSONB
            # Could create separate table later if needed
            if supabase_db.is_available():
                # Store rankings and mark session as completed
                supabase_db.client.table('study_sessions').update({
                    'status': 'completed',
                    'completed_at': datetime.utcnow().isoformat()
                }).eq('id', session_id).execute()
                
                # Store rankings in a separate field (would need to add column)
                # For now, log it
                logger.info("Final ranking saved",
                           session_id=session_id,
                           rankings=rankings)
            
            return {
                "status": "success",
                "session_id": session_id,
                "rankings": rankings
            }
            
        except Exception as e:
            logger.error("Failed to save final ranking",
                        session_id=session_id,
                        error=str(e),
                        exc_info=e)
            raise


# Global service instance
study_service = StudyService()
