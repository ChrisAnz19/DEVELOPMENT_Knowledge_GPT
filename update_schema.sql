-- SQL script to add result_estimation column to searches table
-- This column will store JSON data for the search result estimation feature

-- Add the result_estimation column to the searches table
ALTER TABLE searches 
ADD COLUMN result_estimation JSONB;

-- Add a comment to document the column
COMMENT ON COLUMN searches.result_estimation IS 'JSON data containing search result estimation including estimated_count, confidence, reasoning, and limiting_factors';

-- Create an index on the result_estimation column for better query performance
CREATE INDEX idx_searches_result_estimation ON searches USING GIN (result_estimation);

-- Optional: Add a check constraint to ensure the JSON structure is valid
-- This ensures the JSON contains the expected fields
ALTER TABLE searches 
ADD CONSTRAINT check_result_estimation_structure 
CHECK (
    result_estimation IS NULL OR (
        jsonb_typeof(result_estimation) = 'object' AND
        result_estimation ? 'estimated_count' AND
        result_estimation ? 'confidence' AND
        result_estimation ? 'reasoning'
    )
);

-- Verify the column was added successfully
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'searches' 
AND column_name = 'result_estimation'; 