#!/usr/bin/env python3
"""
Debug SHAP generation performance
"""

import requests
import time
import json

BASE_URL = "http://localhost:8000/api/v1"

def login():
    """Login and get token"""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={
            "username": "researcher@xai.com",
            "password": "research123"
        }
    )
    return response.json()["access_token"]

def get_models(token):
    """Get list of models"""
    response = requests.get(
        f"{BASE_URL}/models",
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.json()

def generate_shap(token, model_id):
    """Generate SHAP explanation"""
    print(f"\n🔮 Generating SHAP for model: {model_id}")
    start_time = time.time()
    
    response = requests.post(
        f"{BASE_URL}/explanations/generate",
        params={
            "model_id": model_id,
            "method": "shap"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to start SHAP: {response.status_code}")
        print(response.text)
        return None
    
    data = response.json()
    explanation_id = data["id"]
    print(f"✅ SHAP task started: {explanation_id}")
    print(f"⏱️  Start time: {time.time() - start_time:.2f}s")
    
    return explanation_id

def check_status(token, explanation_id):
    """Check explanation status"""
    response = requests.get(
        f"{BASE_URL}/explanations/{explanation_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.json()

def wait_for_completion(token, explanation_id, timeout=60):
    """Wait for explanation to complete"""
    print(f"\n⏳ Waiting for completion (max {timeout}s)...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        status_data = check_status(token, explanation_id)
        status = status_data.get("status")
        elapsed = time.time() - start_time
        
        print(f"  [{elapsed:.1f}s] Status: {status}")
        
        if status == "completed":
            print(f"\n✅ SHAP completed in {elapsed:.2f}s")
            return status_data
        elif status == "failed":
            print(f"\n❌ SHAP failed: {status_data.get('error')}")
            return status_data
        
        time.sleep(2)
    
    print(f"\n⏰ Timeout after {timeout}s")
    return None

def main():
    print("=" * 60)
    print("SHAP Generation Debug Script")
    print("=" * 60)
    
    # Login
    print("\n🔐 Logging in...")
    token = login()
    print("✅ Logged in successfully")
    
    # Get models
    print("\n📊 Fetching models...")
    models = get_models(token)
    print(f"✅ Found {len(models)} models")
    
    if not models:
        print("❌ No models found!")
        return
    
    # Use first model
    model = models[0]
    model_id = model["id"]
    model_name = model.get("name", "Unknown")
    model_type = model.get("model_type", "Unknown")
    
    print(f"\n🎯 Testing with:")
    print(f"   Name: {model_name}")
    print(f"   Type: {model_type}")
    print(f"   ID: {model_id}")
    
    # Generate SHAP
    explanation_id = generate_shap(token, model_id)
    
    if not explanation_id:
        print("\n❌ Failed to start SHAP generation")
        return
    
    # Wait for completion
    result = wait_for_completion(token, explanation_id, timeout=60)
    
    if result and result.get("status") == "completed":
        print("\n" + "=" * 60)
        print("✅ SUCCESS!")
        print("=" * 60)
        
        # Show some results
        result_data = json.loads(result.get("result", "{}"))
        if "feature_importance" in result_data:
            top_features = result_data["feature_importance"][:5]
            print("\n🏆 Top 5 Features:")
            for i, feat in enumerate(top_features, 1):
                print(f"   {i}. {feat['feature']}: {feat['importance']:.6f}")
    else:
        print("\n" + "=" * 60)
        print("❌ FAILED or TIMEOUT")
        print("=" * 60)
        print("\n💡 Troubleshooting:")
        print("   1. Check Celery worker logs:")
        print("      docker-compose logs celery_worker --tail=100")
        print("   2. Check backend logs:")
        print("      docker-compose logs backend --tail=100")
        print("   3. Restart Celery worker:")
        print("      docker-compose restart celery_worker")

if __name__ == "__main__":
    main()
