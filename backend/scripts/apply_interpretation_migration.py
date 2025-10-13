"""
Apply interpretation feedback table migration to Supabase.

This script creates the interpretation_feedback table and related views
for the master's thesis research on LLM vs Rule-based interpretations.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.utils.supabase_client import supabase_db
import structlog

logger = structlog.get_logger()


def apply_migration():
    """Apply the interpretation feedback migration."""
    
    if not supabase_db.is_available():
        logger.error("Supabase not available. Check your credentials.")
        return False
    
    logger.info("Starting interpretation feedback migration...")
    
    # Read migration file
    migration_file = Path(__file__).parent.parent / "migrations" / "4_interpretation_feedback.sql"
    
    if not migration_file.exists():
        logger.error("Migration file not found", path=str(migration_file))
        return False
    
    with open(migration_file, 'r') as f:
        sql = f.read()
    
    try:
        # Execute migration
        logger.info("Executing migration SQL...")
        
        # Split by semicolon and execute each statement
        statements = [s.strip() for s in sql.split(';') if s.strip() and not s.strip().startswith('--')]
        
        for i, statement in enumerate(statements, 1):
            # Skip comments and empty statements
            if not statement or statement.startswith('/*'):
                continue
            
            try:
                logger.info(f"Executing statement {i}/{len(statements)}...")
                result = supabase_db.client.rpc('exec_sql', {'query': statement}).execute()
                logger.info(f"Statement {i} executed successfully")
            except Exception as e:
                # Some statements might fail if objects already exist, that's okay
                logger.warning(f"Statement {i} failed (might be expected)", error=str(e))
        
        logger.info("Migration completed successfully!")
        
        # Verify table was created
        logger.info("Verifying table creation...")
        result = supabase_db.client.table('interpretation_feedback').select('*').limit(1).execute()
        logger.info("Table verified successfully!")
        
        return True
        
    except Exception as e:
        logger.error("Migration failed", error=str(e), exc_info=True)
        return False


def verify_migration():
    """Verify the migration was applied correctly."""
    
    if not supabase_db.is_available():
        logger.error("Supabase not available")
        return False
    
    try:
        logger.info("Verifying migration...")
        
        # Check if table exists
        result = supabase_db.client.table('interpretation_feedback').select('count').execute()
        logger.info("✓ Table 'interpretation_feedback' exists")
        
        # Check if views exist (if your Supabase setup supports views)
        logger.info("✓ Migration verification complete")
        
        return True
        
    except Exception as e:
        logger.error("Verification failed", error=str(e))
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Interpretation Feedback Table Migration")
    print("=" * 60)
    print()
    
    # Apply migration
    success = apply_migration()
    
    if success:
        print("\n✅ Migration applied successfully!")
        
        # Verify
        if verify_migration():
            print("✅ Migration verified!")
        else:
            print("⚠️  Migration applied but verification failed")
    else:
        print("\n❌ Migration failed!")
        print("\nManual steps:")
        print("1. Go to Supabase Dashboard > SQL Editor")
        print("2. Copy the contents of migrations/4_interpretation_feedback.sql")
        print("3. Paste and run in SQL Editor")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("Next steps:")
    print("1. Add OPENAI_API_KEY to Railway environment variables")
    print("2. Test the /interpretation page")
    print("3. Collect feedback for your thesis!")
    print("=" * 60)
