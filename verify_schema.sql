-- SQL script to verify the result_estimation column exists and check its structure

-- Check if the result_estimation column exists
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'searches' 
AND column_name = 'result_estimation';

-- Check the table structure for the searches table
SELECT 
    column_name, 
    data_type, 
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'searches' 
ORDER BY ordinal_position;

-- Check if there are any existing result_estimation values
SELECT 
    COUNT(*) as total_searches,
    COUNT(result_estimation) as searches_with_estimation,
    COUNT(*) - COUNT(result_estimation) as searches_without_estimation
FROM searches;

-- Show a sample of existing result_estimation data (if any)
SELECT 
    request_id,
    prompt,
    result_estimation
FROM searches 
WHERE result_estimation IS NOT NULL 
LIMIT 5; 