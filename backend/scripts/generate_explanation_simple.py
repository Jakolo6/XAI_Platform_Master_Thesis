"""Simple explanation generation script (without Celery)."""

import sys
import uuid
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.datasets.registry import get_dataset_registry
from app.datasets.loaders import get_loader
from app.utils.explainers import ShapExplainer
from app.supabase.client import get_supabase_client
import pickle
import structlog

logger = structlog.get_logger()


def generate_explanation_simple(model_id: str, dataset_id: str, method: str = 'shap'):
    """Generate explanation for a model (simplified, no Celery).
    
    Args:
        model_id: Model ID (UUID)
        dataset_id: Dataset identifier
        method: Explanation method (shap or lime)
    """
    print("=" * 60)
    print(f"GENERATING EXPLANATION: {method.upper()}")
    print("=" * 60)
    
    try:
        # Get dataset configuration
        print("\n1. Loading dataset...")
        registry = get_dataset_registry()
        dataset_config = registry.get_dataset_config(dataset_id)
        
        if not dataset_config:
            print(f"   ❌ Dataset not found: {dataset_id}")
            return False
        
        print(f"   ✅ Dataset: {dataset_config['display_name']}")
        
        # Load dataset
        loader = get_loader(dataset_id, dataset_config)
        
        if not loader.splits_exist():
            print(f"   ❌ Dataset not processed. Run: python scripts/process_dataset.py {dataset_id}")
            return False
        
        train_df, val_df, test_df = loader.load_splits()
        print(f"   ✅ Loaded: val={len(val_df)}, test={len(test_df)}")
        
        # Prepare data
        print("\n2. Preparing data...")
        target_col = loader.get_target_column()
        
        X_val = val_df.drop(columns=[target_col])
        X_test = test_df.drop(columns=[target_col])
        
        # Sample background data
        background_data = X_val.sample(min(100, len(X_val)), random_state=42)
        sample_data = X_test.sample(min(1000, len(X_test)), random_state=42)
        
        print(f"   ✅ Background: {len(background_data)} samples")
        print(f"   ✅ Explain: {len(sample_data)} samples")
        
        # Load model
        print("\n3. Loading model...")
        model_path = Path(f"data/models/{model_id}/model.pkl")
        
        if not model_path.exists():
            print(f"   ❌ Model not found: {model_path}")
            return False
        
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        
        print(f"   ✅ Model loaded from {model_path}")
        
        # Generate explanation
        print(f"\n4. Generating {method.upper()} explanation...")
        
        if method == 'shap':
            # Get model type from Supabase
            supabase = get_supabase_client()
            models = supabase.get_models()
            model_info = next((m for m in models if m['id'] == model_id), None)
            model_type = model_info['model_type'] if model_info else 'random_forest'
            
            explainer = ShapExplainer(str(model_path), model_type)
            explainer.initialize_explainer(background_data)
            
            print(f"   ℹ️  Computing SHAP values for {len(sample_data)} samples...")
            explanation_result = explainer.get_global_feature_importance(sample_data)
            
        elif method == 'lime':
            from app.utils.explainers.lime_explainer import LimeExplainer
            
            explainer = LimeExplainer(
                model=model,
                feature_names=X_val.columns.tolist(),
                training_data=background_data
            )
            
            print(f"   ℹ️  Computing LIME explanations for {len(sample_data)} samples...")
            explanation_result = explainer.get_global_feature_importance(sample_data)
            
        else:
            print(f"   ❌ Unsupported method: {method}")
            return False
        
        print(f"   ✅ Explanation generated")
        
        # Display top features
        print("\n5. Top 10 Features:")
        feature_importance = explanation_result.get('feature_importance', [])
        for i, feat in enumerate(feature_importance[:10], 1):
            print(f"   {i:2d}. {feat['feature']:30s} {feat['importance']:8.4f}")
        
        # Save to Supabase
        print("\n6. Saving to Supabase...")
        supabase = get_supabase_client()
        
        # Get dataset UUID
        datasets = supabase.get_datasets(is_active=False)
        supabase_dataset = next((d for d in datasets if d['name'] == dataset_id), None)
        dataset_uuid = supabase_dataset['id'] if supabase_dataset else None
        
        # Generate explanation ID
        explanation_id = str(uuid.uuid4())
        
        # Save explanation
        supabase.insert_explanation({
            'id': explanation_id,
            'model_id': model_id,
            'dataset_id': dataset_uuid,
            'method': method,
            'type': 'global',
            'summary_json': explanation_result,
            'top_features': feature_importance[:10],
            'feature_importance': {f['feature']: f['importance'] for f in feature_importance},
            'num_samples': len(sample_data),
            'num_features': len(X_val.columns)
        })
        
        print(f"   ✅ Saved to Supabase")
        print(f"   ✅ Explanation ID: {explanation_id}")
        
        print("\n" + "=" * 60)
        print("SUCCESS: Explanation generated and saved!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate explanation for a model')
    parser.add_argument('model_id', help='Model ID (UUID)')
    parser.add_argument('dataset_id', help='Dataset ID')
    parser.add_argument('method', nargs='?', default='shap', help='Explanation method (shap or lime)')
    
    args = parser.parse_args()
    
    success = generate_explanation_simple(args.model_id, args.dataset_id, args.method)
    sys.exit(0 if success else 1)
