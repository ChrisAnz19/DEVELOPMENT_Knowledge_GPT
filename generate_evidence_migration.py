#!/usr/bin/env python3
"""
Generate SQL migration for evidence columns.
This script creates the SQL needed to add evidence columns to the people table.
"""

def generate_migration_sql():
    """Generate the SQL migration for evidence columns."""
    
    sql = """
-- Migration: Add Evidence Columns to People Table
-- Run this SQL in your Supabase SQL Editor

-- Add evidence columns to people table
ALTER TABLE people 
ADD COLUMN IF NOT EXISTS evidence_urls TEXT,
ADD COLUMN IF NOT EXISTS evidence_summary TEXT,
ADD COLUMN IF NOT EXISTS evidence_confidence DECIMAL(3,2);

-- Add comments to document the new columns
COMMENT ON COLUMN people.evidence_urls IS 'JSON array of evidence URLs supporting the candidate match';
COMMENT ON COLUMN people.evidence_summary IS 'Human-readable summary of evidence found';
COMMENT ON COLUMN people.evidence_confidence IS 'Confidence score (0-1) based on evidence quality and quantity';

-- Verify the columns were added
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'people' 
AND column_name IN ('evidence_urls', 'evidence_summary', 'evidence_confidence')
ORDER BY column_name;
"""
    
    return sql.strip()

def create_migration_file():
    """Create the migration SQL file."""
    sql = generate_migration_sql()
    
    with open('evidence_migration.sql', 'w') as f:
        f.write(sql)
    
    print("✅ Created evidence_migration.sql")
    print("\n🔧 To apply this migration:")
    print("1. Go to your Supabase dashboard")
    print("2. Open the SQL Editor")
    print("3. Copy and paste the contents of evidence_migration.sql")
    print("4. Run the SQL")
    print("\n📄 Migration SQL:")
    print("=" * 60)
    print(sql)
    print("=" * 60)

if __name__ == '__main__':
    create_migration_file()