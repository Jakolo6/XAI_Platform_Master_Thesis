"""Test Supabase connection."""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.supabase.client import get_supabase_client

def test_connection():
    """Test Supabase connection."""
    print("=" * 60)
    print("SUPABASE CONNECTION TEST")
    print("=" * 60)
    
    try:
        # Initialize client
        print("\n1. Initializing Supabase client...")
        client = get_supabase_client()
        print("   ✅ Client initialized")
        
        # Test connection
        print("\n2. Testing connection...")
        is_healthy = client.health_check()
        
        if is_healthy:
            print("   ✅ Connection successful!")
            print("\n" + "=" * 60)
            print("SUCCESS: Supabase is connected and ready!")
            print("=" * 60)
            return True
        else:
            print("   ❌ Connection failed (health check returned False)")
            return False
            
    except ValueError as e:
        print(f"   ❌ Configuration error: {e}")
        print("\n💡 Make sure your .env file has:")
        print("   - SUPABASE_URL")
        print("   - SUPABASE_ANON_KEY")
        print("   - SUPABASE_SERVICE_KEY")
        return False
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
        print(f"\n💡 Error details: {type(e).__name__}")
        return False

if __name__ == '__main__':
    success = test_connection()
    sys.exit(0 if success else 1)
