"""
Interpretation Layer Service - Translating SHAP into Human Reasoning

Supports two paradigms:
1. LLM-driven interpretation (OpenAI GPT-4)
2. Rule-based scientific interpretation (deterministic SHAP reasoning)
"""

from typing import Dict, Any, List, Optional
import structlog
from openai import OpenAI

from app.core.config import settings

logger = structlog.get_logger()


class InterpretationService:
    """Service for generating human-readable interpretations from SHAP values."""
    
    def __init__(self):
        """Initialize interpretation service with OpenAI client."""
        self.openai_client = None
        if settings.OPENAI_API_KEY:
            self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
            logger.info("OpenAI client initialized")
        else:
            logger.warning("OpenAI API key not configured")
    
    def generate_interpretation(
        self,
        shap_data: Dict[str, Any],
        mode: str = "rule-based",
        model_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate human-readable interpretation from SHAP data.
        
        Args:
            shap_data: SHAP explanation data with feature contributions
            mode: "llm" or "rule-based"
            model_context: Optional model metadata (type, dataset, etc.)
            
        Returns:
            Dictionary with interpretation text and metadata
        """
        try:
            if mode == "llm":
                return self._generate_llm_interpretation(shap_data, model_context)
            else:
                return self._generate_rule_based_interpretation(shap_data, model_context)
        except Exception as e:
            logger.error("Failed to generate interpretation", mode=mode, error=str(e))
            raise
    
    def _generate_rule_based_interpretation(
        self,
        shap_data: Dict[str, Any],
        model_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate interpretation using deterministic rule-based logic.
        
        Maps SHAP values to human-readable phrases based on:
        - Sign (positive/negative contribution)
        - Magnitude (strong/moderate/weak effect)
        - Feature context (what the feature means)
        """
        features = shap_data.get('features', [])
        prediction = shap_data.get('prediction', 'Unknown')
        prediction_proba = shap_data.get('prediction_proba', 0.5)
        
        # Sort features by absolute importance
        sorted_features = sorted(
            features,
            key=lambda x: abs(x.get('contribution', 0)),
            reverse=True
        )
        
        # Take top 5 most important features
        top_features = sorted_features[:5]
        
        # Build interpretation
        interpretation_parts = []
        
        # Opening statement
        if prediction_proba > 0.5:
            interpretation_parts.append(
                f"The model predicts **HIGH RISK** with {prediction_proba*100:.1f}% confidence."
            )
        else:
            interpretation_parts.append(
                f"The model predicts **LOW RISK** with {(1-prediction_proba)*100:.1f}% confidence."
            )
        
        interpretation_parts.append("\n**Key Factors:**\n")
        
        # Analyze each top feature
        for i, feature in enumerate(top_features, 1):
            feature_name = feature.get('feature', 'Unknown')
            contribution = feature.get('contribution', 0)
            value = feature.get('value', 'N/A')
            
            # Determine effect strength
            abs_contrib = abs(contribution)
            if abs_contrib > 0.3:
                strength = "strongly"
            elif abs_contrib > 0.15:
                strength = "moderately"
            else:
                strength = "slightly"
            
            # Determine direction
            if contribution > 0:
                direction = "increases"
                impact = "risky"
            else:
                direction = "decreases"
                impact = "safe"
            
            # Build feature explanation
            feature_text = (
                f"{i}. **{feature_name}** (value: {value}): "
                f"This {strength} {direction} the risk. "
                f"The current value makes the applicant appear more {impact}."
            )
            
            interpretation_parts.append(feature_text)
        
        # Summary
        interpretation_parts.append("\n**Summary:**")
        
        positive_features = [f for f in top_features if f.get('contribution', 0) > 0]
        negative_features = [f for f in top_features if f.get('contribution', 0) < 0]
        
        if len(positive_features) > len(negative_features):
            interpretation_parts.append(
                f"The decision is primarily driven by {len(positive_features)} risk-increasing factors, "
                f"which outweigh the {len(negative_features)} protective factors."
            )
        elif len(negative_features) > len(positive_features):
            interpretation_parts.append(
                f"The decision is primarily driven by {len(negative_features)} protective factors, "
                f"which outweigh the {len(positive_features)} risk-increasing factors."
            )
        else:
            interpretation_parts.append(
                "The decision reflects a balance between risk-increasing and protective factors."
            )
        
        interpretation_text = "\n".join(interpretation_parts)
        
        return {
            "mode": "rule-based",
            "interpretation": interpretation_text,
            "top_features": [f.get('feature') for f in top_features],
            "confidence": prediction_proba,
            "prediction": prediction,
            "method": "Deterministic SHAP reasoning"
        }
    
    def _generate_llm_interpretation(
        self,
        shap_data: Dict[str, Any],
        model_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate interpretation using OpenAI GPT-4.
        
        Uses structured prompts to translate SHAP values into
        human-understandable loan approval/denial reasoning.
        """
        if not self.openai_client:
            raise ValueError("OpenAI API key not configured")
        
        features = shap_data.get('features', [])
        prediction = shap_data.get('prediction', 'Unknown')
        prediction_proba = shap_data.get('prediction_proba', 0.5)
        
        # Sort features by absolute importance
        sorted_features = sorted(
            features,
            key=lambda x: abs(x.get('contribution', 0)),
            reverse=True
        )[:5]
        
        # Build feature summary for LLM
        feature_summary = []
        for f in sorted_features:
            feature_summary.append({
                "feature": f.get('feature'),
                "value": f.get('value'),
                "contribution": f.get('contribution'),
                "effect": "increases risk" if f.get('contribution', 0) > 0 else "decreases risk"
            })
        
        # System prompt
        system_prompt = """You are a financial AI expert explaining loan approval decisions to loan officers and applicants.

Your task is to translate SHAP (SHapley Additive exPlanations) values into clear, human-understandable reasoning about why a loan application was approved or denied.

Guidelines:
1. Use plain language, avoid technical jargon
2. Focus on the top 3-5 most important factors
3. Explain both risk-increasing and risk-decreasing factors
4. Provide actionable insights when possible
5. Be empathetic but factual
6. Structure your explanation clearly with sections

Context: This is for the Home Credit Default Risk dataset, predicting loan default probability."""

        # User prompt with SHAP data
        user_prompt = f"""Please explain this loan decision:

**Prediction:** {"HIGH RISK (Likely to Default)" if prediction_proba > 0.5 else "LOW RISK (Unlikely to Default)"}
**Confidence:** {prediction_proba*100:.1f}%

**SHAP Feature Contributions:**
{self._format_features_for_llm(feature_summary)}

Generate a clear, empathetic explanation that:
1. States the decision and confidence level
2. Explains the top 3-5 key factors
3. Provides a summary of the overall reasoning
4. Uses markdown formatting for readability"""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            interpretation_text = response.choices[0].message.content
            
            return {
                "mode": "llm",
                "interpretation": interpretation_text,
                "top_features": [f['feature'] for f in feature_summary],
                "confidence": prediction_proba,
                "prediction": prediction,
                "method": "GPT-4 Turbo",
                "tokens_used": response.usage.total_tokens
            }
            
        except Exception as e:
            logger.error("OpenAI API call failed", error=str(e))
            raise
    
    def _format_features_for_llm(self, features: List[Dict[str, Any]]) -> str:
        """Format feature data for LLM prompt."""
        lines = []
        for i, f in enumerate(features, 1):
            lines.append(
                f"{i}. **{f['feature']}** = {f['value']}\n"
                f"   - SHAP contribution: {f['contribution']:.3f}\n"
                f"   - Effect: {f['effect']}"
            )
        return "\n\n".join(lines)


# Global service instance
interpretation_service = InterpretationService()
