-- Add behavioral_data column to people table
-- Run this in your Supabase SQL Editor

ALTER TABLE people ADD COLUMN IF NOT EXISTS behavioral_data JSONB;

-- Verify the column was added
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'people' 
ORDER BY ordinal_position;