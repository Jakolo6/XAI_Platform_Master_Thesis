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
from openai import OpenAI
import numpy as np
from pathlib import Path

from app.core.config import settings
from app.services.sandbox_service import sandbox_service
from app.utils.supabase_client import supabase_db
from app.utils.denormalization import (
    FeatureDenormalizer,
    format_loan_applicant_summary,
    create_feature_list_for_display
)

logger = structlog.get_logger()

# Study configuration
STUDY_MODEL_ID = "german_credit_xgb"
STUDY_DATASET_ID = "german-credit"  # Updated to match database
NUM_CASES_PER_SESSION = 6
EXPLANATION_LAYERS = ["layer_1", "layer_2", "layer_3", "layer_4"]


class StudyService:
    """
    Service for managing user study sessions and data collection.
    
    Handles:
    - Creating study sessions with randomized explanation layer assignments
    - Generating study cases (loan data + SHAP explanations)
    - Formatting explanations for different interpretational layers (with OpenAI for Layers 2 & 4)
    - Saving participant responses and ratings
    - Managing final comparison and ranking data
    """
    
    def __init__(self):
        """Initialize study service with OpenAI client and denormalizer."""
        self._case_cache = {}  # Cache generated cases to ensure consistency
        self.openai_client = None
        if settings.OPENAI_API_KEY:
            self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
            logger.info("OpenAI client initialized for study service")
        else:
            logger.error("OpenAI API key not configured - Layers 2 & 4 will FAIL without it")
            logger.error("Please set OPENAI_API_KEY in your .env file to use Layers 2 and 4")
        
        # Initialize denormalizer for human-readable values
        # Note: Paths will be updated once model is trained and uploaded
        scaler_path = Path("data/models/german_credit_fair/german_credit_scaler.pkl")
        metadata_path = Path("data/models/german_credit_fair/model_metadata.pkl")
        
        self.denormalizer = FeatureDenormalizer(
            scaler_path=str(scaler_path) if scaler_path.exists() else None,
            metadata_path=str(metadata_path) if metadata_path.exists() else None
        )
        
        if scaler_path.exists():
            logger.info("Denormalizer initialized with scaler and metadata")
        else:
            logger.warning("Denormalizer initialized without scaler - will show normalized values")
    
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
        Uses denormalization to show real-world values to participants.
        
        Args:
            features: Raw (normalized) feature dictionary from model
            
        Returns:
            Formatted loan data with denormalized, human-readable values
        """
        try:
            # Denormalize features for human display
            denormalized_data = self.denormalizer.denormalize_instance(features)
            
            # Create human-readable summary
            summary = format_loan_applicant_summary(denormalized_data)
            
            # Organize features into categories
            loan_data = {
                "summary": summary,
                "applicant_info": {},
                "loan_details": {},
                "financial_status": {},
                "other_info": {},
                "raw_features": denormalized_data  # Include full denormalized data
            }
            
            # Categorize features for display
            for feature_name, data in denormalized_data.items():
                try:
                    display_string = data.get('display_string', str(data.get('raw_value', '')))
                    
                    # Skip Unnamed columns
                    if 'Unnamed' in feature_name:
                        continue
                    
                    # Categorize by feature name (handle both cases)
                    feature_lower = feature_name.lower()
                    if feature_name in ['age', 'Age', 'employment', 'job', 'Job', 'housing', 'Housing', 'present_residence', 'Sex']:
                        loan_data["applicant_info"][feature_name] = display_string
                    elif feature_name in ['credit_amount', 'Credit amount', 'duration', 'Duration', 'installment_rate', 'purpose', 'Purpose']:
                        loan_data["loan_details"][feature_name] = display_string
                    elif feature_name in ['checking_status', 'Checking account', 'savings_status', 'Saving accounts', 'credit_history', 'existing_credits']:
                        loan_data["financial_status"][feature_name] = display_string
                    else:
                        loan_data["other_info"][feature_name] = display_string
                except Exception as e:
                    logger.warning(f"Failed to categorize feature {feature_name}", error=str(e))
                    continue
            
            return loan_data
            
        except Exception as e:
            logger.error("Failed to format loan data", error=str(e), exc_info=True)
            # Return minimal fallback
            return {
                "summary": "Loan application",
                "applicant_info": {},
                "loan_details": {},
                "financial_status": {},
                "other_info": {k: str(v) for k, v in features.items()},
                "raw_features": {}
            }
    
    def _format_explanation_for_layer(
        self,
        shap_explanation: Dict[str, Any],
        features: Dict[str, Any],
        prediction: float,
        layer: str
    ) -> Dict[str, Any]:
        """
        Format SHAP explanation according to the assigned interpretational layer.
        
        Implements 4 REFINED explanation styles for UCI German Credit loan decisions:
        - Layer 1: Analytical Transparency (Machine View) - Pure SHAP, no LLM
        - Layer 2: Conversational Summary (LLM-Generated) - OpenAI GPT-4 for friendly tone
        - Layer 3: Story-Driven Causality (Narrative + Counterfactual) - Template-based
        - Layer 4: Visual Dashboard + Metaphor (Cognitive Fusion) - Hybrid with LLM metaphor
        
        Args:
            shap_explanation: Raw SHAP explanation data with features and contributions
            features: Raw feature values for this instance
            prediction: Model prediction probability (0-1, where higher = higher risk)
            layer: Which layer to use (layer_1, layer_2, layer_3, layer_4)
            
        Returns:
            Formatted explanation dict with layer_id, decision, and content
        """
        
        # Extract top features by importance
        top_features = shap_explanation["features"][:5]  # Top 5 most important
        
        # Determine decision label (lower probability = good credit = approved)
        # German Credit: target=1 is "bad credit", so lower prob = approved
        is_approved = prediction < 0.5
        decision_label = "APPROVED" if is_approved else "REJECTED"
        
        # Determine risk level
        if prediction < 0.3:
            risk_level = "Low Risk"
        elif prediction < 0.6:
            risk_level = "Medium Risk"
        else:
            risk_level = "High Risk"
        
        # Base structure
        base_explanation = {
            "layer_id": layer,
            "decision": {
                "label": decision_label,
                "score": round(prediction, 3),
                "risk_level": risk_level
            },
            "top_features": top_features,
            "all_features": shap_explanation["features"]
        }
        
        # ============================================================================
        # LAYER 1: Analytical Transparency (Machine View)
        # ============================================================================
        # Pure SHAP → sorted top 5 features with magnitude and sign
        # No smoothing, no story, no LLM
        
        if layer == "layer_1":
            drivers = []
            for f in top_features:
                direction = "increases" if f["contribution"] > 0 else "decreases"
                drivers.append({
                    "feature_name": f["feature"],
                    "direction": direction,
                    "contribution": round(f["contribution"], 4),
                    "value": features.get(f["feature"], "N/A")
                })
            
            base_explanation["content"] = {
                "type": "analytical",
                "title": "Key Drivers",
                "subtitle": "Machine View - Raw SHAP Values",
                "drivers": drivers
            }
        
        # ============================================================================
        # LAYER 2: Conversational Summary (LLM-Generated)
        # ============================================================================
        # SHAP values → OpenAI API (gpt-4o-mini)
        # Prompt: ≤80 words, conversational, no jargon, no numbers
        
        elif layer == "layer_2":
            narrative = self._generate_conversational_summary(
                top_features, features, is_approved, prediction
            )
            
            base_explanation["content"] = {
                "type": "conversational",
                "title": "Decision Summary",
                "subtitle": "AI Assistant Explanation",
                "text": narrative
            }
        
        # ============================================================================
        # LAYER 3: Story-Driven Causality (Narrative + Counterfactual)
        # ============================================================================
        # Uses both SHAP values and raw feature values
        # Emulates counterfactual mental simulation
        
        elif layer == "layer_3":
            # Get top contributing feature
            top_driver = top_features[0]
            feature_name = top_driver["feature"].replace("_", " ").lower()
            feature_value = features.get(top_driver["feature"], "N/A")
            contribution = top_driver["contribution"]
            
            # Build causal explanation with actual values
            if is_approved:
                causal_text = (
                    f"Because your {feature_name} (value: {feature_value}) is considered favorable "
                    f"compared to typical applicants, the system rated your risk as low. "
                    f"This factor {'strongly' if abs(contribution) > 0.3 else 'moderately'} "
                    f"supported the approval decision."
                )
                counterfactual_text = (
                    f"If your {feature_name} were less favorable, "
                    f"the approval likelihood would decrease significantly."
                )
            else:
                causal_text = (
                    f"Because your {feature_name} (value: {feature_value}) indicates higher risk "
                    f"compared to typical successful applicants, the system rated your application as risky. "
                    f"This factor {'strongly' if abs(contribution) > 0.3 else 'moderately'} "
                    f"influenced the rejection."
                )
                
                # Generate specific counterfactual
                counterfactual_text = self._generate_counterfactual(
                    feature_name, feature_value, contribution
                )
            
            base_explanation["content"] = {
                "type": "causal_counterfactual",
                "title": "Why This Decision?",
                "subtitle": "Causal Story with What-If Scenario",
                "causal_explanation": causal_text,
                "counterfactual": counterfactual_text
            }
        
        # ============================================================================
        # LAYER 4: Visual Dashboard + Metaphor (Cognitive Fusion)
        # ============================================================================
        # Combines numeric + linguistic + visual + metaphorical cues
        # Emoji-enhanced drivers + risk meter + LLM metaphor
        
        elif layer == "layer_4":
            # Build top 3 drivers with emoji + human-readable reasons
            drivers = []
            for f in top_features[:3]:
                feature_name = f["feature"].replace("_", " ").title()
                contribution = f["contribution"]
                magnitude = abs(contribution)
                
                # Assign emoji based on feature type
                emoji = self._get_feature_emoji(f["feature"])
                
                # Determine strength
                if magnitude > 0.3:
                    strength = "strongly"
                elif magnitude > 0.15:
                    strength = "moderately"
                else:
                    strength = "slightly"
                
                # Determine effect
                if contribution > 0:
                    effect = "reduced approval" if not is_approved else "increased risk"
                else:
                    effect = "helped approval" if is_approved else "reduced risk"
                
                reason = f"{emoji} {feature_name} {strength} {effect} ({contribution:+.3f})"
                
                drivers.append({
                    "feature": feature_name,
                    "emoji": emoji,
                    "reason": reason,
                    "contribution": round(contribution, 3)
                })
            
            # Generate risk meter text
            approval_chance = int((1 - prediction) * 100)
            if risk_level == "Low Risk":
                risk_emoji = "🟢"
            elif risk_level == "Medium Risk":
                risk_emoji = "🟡"
            else:
                risk_emoji = "🔴"
            
            risk_meter = f"{risk_emoji} {risk_level} - {approval_chance}% approval likelihood"
            
            # Generate metaphor via LLM
            metaphor = self._generate_metaphor(
                top_features[:3], is_approved, prediction
            )
            
            # Generate actionable guidance
            guidance = self._generate_guidance(top_features, is_approved)
            
            base_explanation["content"] = {
                "type": "visual_dashboard",
                "title": "Decision Dashboard",
                "subtitle": "Visual + Emotional Insight",
                "decision_header": {
                    "label": decision_label,
                    "score": round(prediction, 3),
                    "risk_level": risk_level,
                    "risk_meter": risk_meter
                },
                "top_drivers": drivers,
                "metaphor": metaphor,
                "guidance": guidance
            }
        
        return base_explanation
    
    def _generate_conversational_summary(
        self,
        top_features: List[Dict[str, Any]],
        features: Dict[str, Any],
        is_approved: bool,
        prediction: float
    ) -> str:
        """Generate conversational summary using OpenAI API (Layer 2)."""
        if not self.openai_client:
            logger.error("OpenAI API key not configured - Layer 2 requires OpenAI")
            raise ValueError("Layer 2 requires OpenAI API key. Please configure OPENAI_API_KEY in environment.")
        
        try:
            # Build feature summary for LLM
            feature_list = []
            for f in top_features[:3]:
                feature_name = f["feature"].replace("_", " ")
                contribution = f["contribution"]
                effect = "helped" if contribution < 0 else "raised concerns"
                feature_list.append(f"- {feature_name}: {effect}")
            
            feature_text = "\n".join(feature_list)
            decision_text = "approved" if is_approved else "rejected"
            
            prompt = f"""Summarize this credit decision in ≤80 words. Be conversational and friendly, avoiding jargon and numbers.

Decision: Loan {decision_text}
Key factors:
{feature_text}

Write 2-3 sentences explaining this decision in a friendly, accessible way. Example tone: "It looks like your steady job helped, but your loan amount made the bank cautious."""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a friendly AI assistant explaining loan decisions in simple, conversational language."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI API call failed for Layer 2: {e}")
            raise ValueError(f"Failed to generate Layer 2 explanation via OpenAI: {str(e)}")
    
    def _generate_counterfactual(
        self,
        feature_name: str,
        feature_value: Any,
        contribution: float
    ) -> str:
        """Generate counterfactual explanation (Layer 3)."""
        if "amount" in feature_name or "credit" in feature_name:
            return (
                f"If the requested loan amount were about 20-30% lower, "
                f"approval would be significantly more likely."
            )
        elif "income" in feature_name or "salary" in feature_name:
            return (
                f"If your {feature_name} were about 15-20% higher, "
                f"approval would be significantly more likely."
            )
        elif "duration" in feature_name or "month" in feature_name:
            return (
                f"If the loan duration were shortened by 6-12 months, "
                f"approval would be significantly more likely."
            )
        elif "age" in feature_name:
            return (
                f"While age cannot be changed, building a longer credit history "
                f"would improve future approval chances."
            )
        elif "employment" in feature_name or "job" in feature_name:
            return (
                f"Demonstrating more stable employment history "
                f"would significantly improve approval likelihood."
            )
        else:
            return (
                f"Improving your {feature_name} by addressing the underlying factors "
                f"would increase the likelihood of approval."
            )
    
    def _generate_metaphor(
        self,
        top_features: List[Dict[str, Any]],
        is_approved: bool,
        prediction: float
    ) -> str:
        """Generate one-line metaphor using OpenAI API (Layer 4)."""
        if not self.openai_client:
            logger.error("OpenAI API key not configured - Layer 4 requires OpenAI")
            raise ValueError("Layer 4 requires OpenAI API key. Please configure OPENAI_API_KEY in environment.")
        
        try:
            decision_text = "approved" if is_approved else "rejected"
            risk_text = "low" if prediction < 0.5 else "high"
            
            # Build feature context
            feature_names = [f["feature"].replace("_", " ") for f in top_features]
            
            prompt = f"""Write ONE short metaphor (≤12 words) that explains this credit decision emotionally but responsibly.

Decision: Loan {decision_text}
Risk level: {risk_text}
Key factors: {', '.join(feature_names)}

Example metaphors:
- "Your financial engine was strong, but the loan weight slowed it."
- "The numbers told a cautious story about your credit journey."
- "Your foundation is solid, but the structure needs more support."

Write one metaphor (≤12 words):"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a creative writer crafting short, responsible financial metaphors."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=30
            )
            
            metaphor = response.choices[0].message.content.strip()
            # Remove quotes if present
            metaphor = metaphor.strip('"').strip("'")
            return metaphor
            
        except Exception as e:
            logger.error(f"OpenAI API call failed for Layer 4 metaphor: {e}")
            raise ValueError(f"Failed to generate Layer 4 metaphor via OpenAI: {str(e)}")
    
    def _get_feature_emoji(self, feature_name: str) -> str:
        """Get emoji for feature visualization (Layer 4)."""
        feature_lower = feature_name.lower()
        
        if "amount" in feature_lower or "credit" in feature_lower:
            return "💰"
        elif "income" in feature_lower or "salary" in feature_lower:
            return "💵"
        elif "duration" in feature_lower or "month" in feature_lower:
            return "📅"
        elif "age" in feature_lower:
            return "👤"
        elif "employment" in feature_lower or "job" in feature_lower:
            return "💼"
        elif "saving" in feature_lower or "account" in feature_lower:
            return "🏦"
        elif "property" in feature_lower or "housing" in feature_lower:
            return "🏠"
        elif "purpose" in feature_lower:
            return "🎯"
        else:
            return "📊"
    
    def _generate_guidance(
        self,
        top_features: List[Dict[str, Any]],
        is_approved: bool
    ) -> str:
        """Generate actionable guidance (Layer 4)."""
        if is_approved:
            return (
                "Your application meets the approval criteria. "
                "Maintain your current financial profile for future credit needs."
            )
        
        # Find most impactful negative factor
        top_negative = next((f for f in top_features if f["contribution"] > 0), top_features[0])
        feature_name = top_negative["feature"].replace("_", " ").lower()
        
        if "amount" in feature_name or "credit" in feature_name:
            return "Consider applying for a lower loan amount to increase approval likelihood."
        elif "income" in feature_name or "salary" in feature_name:
            return "Increasing your income or adding a co-applicant would significantly improve approval chances."
        elif "duration" in feature_name:
            return "Choosing a shorter loan duration would reduce risk and increase approval likelihood."
        elif "employment" in feature_name:
            return "Demonstrating stable employment history would strengthen future applications."
        else:
            return f"Improving your {feature_name} would increase your chances of approval in future applications."
    
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
        
        Stores in human_evaluations table:
        - participant_code (from session)
        - session_id
        - explanation layer_id (stored in 'method' column)
        - all 4 rating dimensions (trust, understanding, usefulness, mental_effort)
        - free text comments
        - time spent
        - serialized explanation blob (stored in 'comments' field as JSON)
        
        Args:
            session_id: Study session ID
            case_index: Case number (0-5)
            instance_id: Sample instance ID
            explanation_layer: Which layer was shown (layer_1, layer_2, layer_3, layer_4)
            ratings: Dictionary with trust, understanding, usefulness, mental_effort, comments, 
                    explanation_data (serialized), decision_label, risk_score
            
        Returns:
            Confirmation with evaluation_id
        """
        try:
            import json
            
            evaluation_id = str(uuid.uuid4())
            
            # Get session info for participant_code
            session = None
            if supabase_db.is_available():
                result = supabase_db.client.table('study_sessions').select('*').eq('id', session_id).execute()
                if result.data and len(result.data) > 0:
                    session = result.data[0]
            
            participant_code = session.get('participant_code') if session else f"UNKNOWN_{session_id[:8]}"
            
            # Prepare comments field: combine user comments + serialized explanation
            # This allows us to audit exactly what was shown without changing schema
            user_comments = ratings.get("comments", "")
            explanation_data = ratings.get("explanation_data", {})
            
            # Create combined comments field with explanation audit trail
            combined_comments = {
                "user_comments": user_comments,
                "explanation_shown": explanation_data  # Full explanation structure for audit
            }
            comments_json = json.dumps(combined_comments)
            
            # Create evaluation record
            # NOTE: Using 'method' column to store layer_id (layer_1, layer_2, layer_3, layer_4)
            # This is intentional reuse of existing schema without modifications
            evaluation_data = {
                "id": evaluation_id,
                "session_id": session_id,
                "participant_code": participant_code,
                "model_id": STUDY_MODEL_ID,
                "question_id": str(uuid.uuid4()),  # Generate question_id
                "method": explanation_layer,  # IMPORTANT: Stores layer_id here (layer_1, layer_2, etc.)
                "prediction_outcome": ratings.get("decision_label", "Unknown"),
                "prediction_confidence": ratings.get("risk_score", 0.0),
                "trust_score": ratings["trust"],
                "understanding_score": ratings["understanding"],
                "usefulness_score": ratings["usefulness"],
                "time_spent": ratings.get("time_spent", 0.0),
                "comments": comments_json,  # Stores both user comments AND serialized explanation
                "explanation_shown": True,
                "created_at": datetime.utcnow().isoformat()
            }
            
            # NOTE: mental_effort is passed in ratings but not in current schema
            # If you want to store it separately, add column: mental_effort INTEGER
            # For now, it's included in the explanation_data JSON in comments field
            if "mental_effort" in ratings:
                # Store mental_effort in comments JSON for now
                combined_comments["mental_effort"] = ratings["mental_effort"]
                evaluation_data["comments"] = json.dumps(combined_comments)
            
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
                           layer=explanation_layer,
                           mental_effort=ratings.get("mental_effort"))
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
