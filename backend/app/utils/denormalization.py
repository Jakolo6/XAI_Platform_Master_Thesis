"""
Denormalization utilities for displaying human-readable values to study participants.

This module handles inverse transformation of normalized model inputs back to
real-world values for human interpretation.
"""

import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional
import structlog

logger = structlog.get_logger()


class FeatureDenormalizer:
    """Handles denormalization of features for human-readable display."""
    
    def __init__(self, scaler_path: Optional[str] = None, metadata_path: Optional[str] = None):
        """
        Initialize denormalizer with scaler and metadata.
        
        Args:
            scaler_path: Path to saved StandardScaler
            metadata_path: Path to model metadata (feature names, mappings, etc.)
        """
        self.scaler = None
        self.metadata = None
        
        if scaler_path and Path(scaler_path).exists():
            self.scaler = joblib.load(scaler_path)
            logger.info("Scaler loaded", path=scaler_path)
        
        if metadata_path and Path(metadata_path).exists():
            self.metadata = joblib.load(metadata_path)
            logger.info("Metadata loaded", path=metadata_path)
    
    def denormalize_numerical(self, values: np.ndarray, feature_names: List[str]) -> Dict[str, float]:
        """
        Denormalize numerical features using the scaler.
        
        Args:
            values: Normalized feature values
            feature_names: Names of features
            
        Returns:
            Dictionary of feature_name -> denormalized_value
        """
        if self.scaler is None:
            logger.warning("No scaler available, returning normalized values")
            return {name: float(val) for name, val in zip(feature_names, values)}
        
        # Get numerical columns from metadata
        numerical_cols = self.metadata.get('numerical_cols', []) if self.metadata else feature_names
        
        # Create DataFrame for inverse transform
        df = pd.DataFrame([values], columns=feature_names)
        
        # Inverse transform only numerical columns
        if numerical_cols:
            df[numerical_cols] = self.scaler.inverse_transform(df[numerical_cols])
        
        return df.iloc[0].to_dict()
    
    def format_for_display(self, feature_name: str, value: Any) -> str:
        """
        Format a feature value for human-readable display.
        
        Args:
            feature_name: Name of the feature
            value: Denormalized value
            
        Returns:
            Formatted string for display
        """
        # Get display name
        display_name = self.metadata.get('feature_display_names', {}).get(feature_name, feature_name) if self.metadata else feature_name
        
        # Check if categorical
        categorical_mappings = self.metadata.get('categorical_mappings', {}) if self.metadata else {}
        
        if feature_name in categorical_mappings:
            # Map categorical value - handle both int and string values
            try:
                int_value = int(float(value)) if isinstance(value, (int, float, str)) else value
                mapped_value = categorical_mappings[feature_name].get(int_value, f"Unknown ({value})")
            except (ValueError, TypeError):
                mapped_value = str(value)
            return f"{display_name}: {mapped_value}"
        
        # Format numerical values - handle conversion errors gracefully
        try:
            if feature_name == 'age':
                return f"{display_name}: {int(float(value))} years"
            elif feature_name == 'credit_amount':
                return f"{display_name}: €{int(float(value)):,}"
            elif feature_name == 'duration':
                return f"{display_name}: {int(float(value))} months"
            elif feature_name == 'installment_rate':
                return f"{display_name}: {int(float(value))}%"
            elif feature_name == 'present_residence':
                return f"{display_name}: {int(float(value))} years"
            elif feature_name == 'existing_credits':
                return f"{display_name}: {int(float(value))}"
            else:
                # Default formatting
                if isinstance(value, (int, float)):
                    return f"{display_name}: {value:.2f}" if isinstance(value, float) else f"{display_name}: {value}"
                else:
                    return f"{display_name}: {value}"
        except (ValueError, TypeError):
            # If conversion fails, just return as string
            return f"{display_name}: {value}"
    
    def denormalize_instance(self, instance: Dict[str, Any]) -> Dict[str, Any]:
        """
        Denormalize a complete instance for display.
        
        Args:
            instance: Dictionary of normalized feature values
            
        Returns:
            Dictionary with denormalized values and formatted display strings
        """
        feature_names = list(instance.keys())
        values = np.array([instance[f] for f in feature_names])
        
        # Denormalize numerical features
        denormalized = self.denormalize_numerical(values, feature_names)
        
        # Create display-friendly version
        display_values = {}
        for feature_name, value in denormalized.items():
            display_values[feature_name] = {
                'raw_value': value,
                'display_string': self.format_for_display(feature_name, value)
            }
        
        return display_values


# Default categorical mappings (fallback if metadata not available)
DEFAULT_CATEGORICAL_MAPPINGS = {
    'checking_status': {
        0: '< 0 DM',
        1: '0 - 200 DM',
        2: '> 200 DM',
        3: 'No checking account'
    },
    'credit_history': {
        0: 'No credits / all paid',
        1: 'All paid this bank',
        2: 'Existing paid',
        3: 'Delayed payment',
        4: 'Critical account'
    },
    'purpose': {
        0: 'New car',
        1: 'Used car',
        2: 'Furniture/equipment',
        3: 'Radio/TV',
        4: 'Domestic appliances',
        5: 'Repairs',
        6: 'Education',
        7: 'Vacation',
        8: 'Retraining',
        9: 'Business',
        10: 'Other'
    },
    'savings_status': {
        0: '< 100 DM',
        1: '100 - 500 DM',
        2: '500 - 1000 DM',
        3: '> 1000 DM',
        4: 'Unknown / no savings'
    },
    'employment': {
        0: 'Unemployed',
        1: '< 1 year',
        2: '1 - 4 years',
        3: '4 - 7 years',
        4: '> 7 years'
    },
    'housing': {
        0: 'Rent',
        1: 'Own',
        2: 'For free'
    },
    'job': {
        0: 'Unemployed/unskilled',
        1: 'Unskilled resident',
        2: 'Skilled',
        3: 'Highly skilled'
    }
}

DEFAULT_FEATURE_DISPLAY_NAMES = {
    'age': 'Age',
    'credit_amount': 'Credit Amount',
    'duration': 'Duration',
    'installment_rate': 'Installment Rate',
    'present_residence': 'Years at Residence',
    'existing_credits': 'Existing Credits',
    'checking_status': 'Checking Account',
    'credit_history': 'Credit History',
    'purpose': 'Loan Purpose',
    'savings_status': 'Savings Account',
    'employment': 'Employment Length',
    'property_magnitude': 'Property',
    'other_payment_plans': 'Other Payment Plans',
    'housing': 'Housing',
    'job': 'Job Type',
    'own_telephone': 'Has Telephone',
}


def format_loan_applicant_summary(denormalized_data: Dict[str, Any]) -> str:
    """
    Create a human-readable summary of a loan applicant.
    
    Args:
        denormalized_data: Denormalized feature values
        
    Returns:
        Formatted summary string
    """
    try:
        age = denormalized_data.get('age', {}).get('raw_value', 'Unknown')
        credit_amount = denormalized_data.get('credit_amount', {}).get('raw_value', 0)
        duration = denormalized_data.get('duration', {}).get('raw_value', 0)
        employment = denormalized_data.get('employment', {}).get('display_string', 'Unknown employment')
        
        # Safe conversion with fallbacks
        age_str = f"{int(float(age))}" if isinstance(age, (int, float)) else str(age)
        credit_str = f"€{int(float(credit_amount)):,}" if isinstance(credit_amount, (int, float)) else str(credit_amount)
        duration_str = f"{int(float(duration))}" if isinstance(duration, (int, float)) else str(duration)
        employment_str = employment.split(': ')[1] if ': ' in employment else employment
        
        summary = f"Applicant: {age_str} years old, {employment_str}, requesting {credit_str} for {duration_str} months"
        
        return summary
    except Exception as e:
        logger.warning("Failed to format loan applicant summary", error=str(e))
        return "Loan applicant information"


def create_feature_list_for_display(denormalized_data: Dict[str, Any], top_n: int = 5) -> List[Dict[str, str]]:
    """
    Create a list of top features for display in the UI.
    
    Args:
        denormalized_data: Denormalized feature values
        top_n: Number of top features to return
        
    Returns:
        List of feature dictionaries with name and display_value
    """
    features = []
    
    for feature_name, data in denormalized_data.items():
        features.append({
            'name': feature_name,
            'display_name': DEFAULT_FEATURE_DISPLAY_NAMES.get(feature_name, feature_name),
            'display_value': data.get('display_string', str(data.get('raw_value', ''))),
            'raw_value': data.get('raw_value')
        })
    
    return features[:top_n]
