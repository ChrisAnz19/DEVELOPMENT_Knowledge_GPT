#!/usr/bin/env python3
"""
Database Migration Script
Adds the behavioral_data column to the people table if it doesn't exist
"""

import logging
from supabase_client import supabase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migration():
    """Run the database migration to add behavioral_data column"""
    try:
        # SQL to add behavioral_data column if it doesn't exist
        migration_sql = """
        DO $$ 
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'people' AND column_name = 'behavioral_data'
            ) THEN
                ALTER TABLE people ADD COLUMN behavioral_data JSONB;
                RAISE NOTICE 'Added behavioral_data column to people table';
            ELSE
                RAISE NOTICE 'behavioral_data column already exists in people table';
            END IF;
        END $$;
        """
        
        # Execute the migration
        logger.info("Running database migration to add behavioral_data column...")
        result = supabase.rpc('exec_sql', {'sql': migration_sql}).execute()
        
        logger.info("Migration completed successfully!")
        logger.info("The behavioral_data column has been added to the people table.")
        
        return True
        
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        logger.info("Please run this SQL manually in your Supabase SQL Editor:")
        logger.info(migration_sql)
        return False

if __name__ == "__main__":
    print("🔧 Running Database Migration...")
    print("=" * 50)
    
    success = run_migration()
    
    if success:
        print("✅ Migration completed successfully!")
    else:
        print("❌ Migration failed. Please run the SQL manually in Supabase.")
        print("\nSQL to run manually:")
        print("""
        ALTER TABLE people ADD COLUMN IF NOT EXISTS behavioral_data JSONB;
        """)