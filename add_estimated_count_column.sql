-- Add estimated_count column to searches table for easier frontend access
-- This provides a simple integer field alongside the JSONB result_estimation field

ALTER TABLE searches 
ADD COLUMN IF NOT EXISTS estimated_count INTEGER;

-- Add a comment to document the column
COMMENT ON COLUMN searches.estimated_count IS 'Simple integer field containing the estimated number of people matching the search criteria';

-- Create an index for better query performance
CREATE INDEX IF NOT EXISTS idx_searches_estimated_count ON searches (estimated_count);

-- Verify the column was added successfully
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'searches' 
AND column_name IN ('estimated_count', 'result_estimation')
ORDER BY column_name;