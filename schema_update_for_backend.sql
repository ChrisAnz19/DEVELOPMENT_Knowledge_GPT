-- SQL script to update schema for backend compatibility
-- This script brings your current schema in line with the backend requirements

-- =======================
-- MISSING SEQUENCES
-- =======================

-- Create sequences for auto-increment columns if they don't exist
CREATE SEQUENCE IF NOT EXISTS people_id_seq;
CREATE SEQUENCE IF NOT EXISTS searches_id_seq;

-- Set ownership of sequences to their respective columns
ALTER SEQUENCE people_id_seq OWNED BY public.people.id;
ALTER SEQUENCE searches_id_seq OWNED BY public.searches.id;

-- =======================
-- MISSING TABLES
-- =======================

-- Create exclusions table (used by backend to track previously returned candidates)
CREATE TABLE IF NOT EXISTS public.exclusions (
    id SERIAL PRIMARY KEY,
    linkedin_url TEXT NOT NULL,
    name TEXT,
    reason TEXT DEFAULT 'Previously returned in search results',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create unique index on linkedin_url for exclusions
CREATE UNIQUE INDEX IF NOT EXISTS idx_exclusions_linkedin_url ON public.exclusions (linkedin_url);

-- =======================
-- MISSING COLUMNS
-- =======================

-- Add estimated_count column to searches table if it doesn't exist
ALTER TABLE public.searches 
ADD COLUMN IF NOT EXISTS estimated_count INTEGER;

-- Add result_estimation column if it doesn't exist (with proper constraint)
DO $$ 
BEGIN
    -- Check if column exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'searches' AND column_name = 'result_estimation'
    ) THEN
        -- Add the column
        ALTER TABLE public.searches ADD COLUMN result_estimation JSONB;
        
        -- Add the constraint
        ALTER TABLE public.searches 
        ADD CONSTRAINT check_result_estimation_structure 
        CHECK (
            result_estimation IS NULL OR (
                jsonb_typeof(result_estimation) = 'object' AND
                result_estimation ? 'estimated_count' AND
                result_estimation ? 'confidence' AND
                result_estimation ? 'reasoning'
            )
        );
    END IF;
END $$;

-- =======================
-- COLUMN UPDATES
-- =======================

-- Ensure linkedin_posts column exists in people table (used by backend)
ALTER TABLE public.people 
ADD COLUMN IF NOT EXISTS linkedin_posts JSONB;

-- =======================
-- INDEXES FOR PERFORMANCE
-- =======================

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_searches_request_id ON public.searches (request_id);
CREATE INDEX IF NOT EXISTS idx_searches_status ON public.searches (status);
CREATE INDEX IF NOT EXISTS idx_searches_created_at ON public.searches (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_searches_estimated_count ON public.searches (estimated_count);
CREATE INDEX IF NOT EXISTS idx_searches_result_estimation ON public.searches USING GIN (result_estimation);

CREATE INDEX IF NOT EXISTS idx_people_search_id ON public.people (search_id);
CREATE INDEX IF NOT EXISTS idx_people_linkedin_url ON public.people (linkedin_url);
CREATE INDEX IF NOT EXISTS idx_people_email ON public.people (email);
CREATE INDEX IF NOT EXISTS idx_people_created_at ON public.people (created_at DESC);

-- =======================
-- COLUMN COMMENTS
-- =======================

-- Add helpful comments for documentation
COMMENT ON TABLE public.exclusions IS 'Tracks people who have been previously returned in search results to avoid duplicates';
COMMENT ON COLUMN public.searches.estimated_count IS 'Simple integer field containing the estimated number of people matching the search criteria';
COMMENT ON COLUMN public.searches.result_estimation IS 'JSON data containing search result estimation including estimated_count, confidence, reasoning, and limiting_factors';
COMMENT ON COLUMN public.people.linkedin_posts IS 'JSON array of LinkedIn posts data for the person';
COMMENT ON COLUMN public.people.behavioral_data IS 'AI-generated behavioral analysis and scores for the candidate';

-- =======================
-- VERIFICATION QUERIES
-- =======================

-- Verify all tables exist
SELECT 
    schemaname,
    tablename
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('searches', 'people', 'users', 'exclusions')
ORDER BY tablename;

-- Verify searches table structure
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'searches' 
ORDER BY ordinal_position;

-- Verify people table structure
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'people' 
ORDER BY ordinal_position;

-- Verify exclusions table structure
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'exclusions' 
ORDER BY ordinal_position;

-- Check indexes
SELECT 
    indexname,
    tablename,
    indexdef
FROM pg_indexes 
WHERE schemaname = 'public' 
AND tablename IN ('searches', 'people', 'exclusions')
ORDER BY tablename, indexname;

-- =======================
-- DATA VALIDATION
-- =======================

-- Show sample data to verify structure
SELECT 'searches' as table_name, COUNT(*) as row_count FROM public.searches
UNION ALL
SELECT 'people' as table_name, COUNT(*) as row_count FROM public.people
UNION ALL  
SELECT 'users' as table_name, COUNT(*) as row_count FROM public.users
UNION ALL
SELECT 'exclusions' as table_name, COUNT(*) as row_count FROM public.exclusions;

-- Show any constraint violations that might exist
SELECT conname, contype, pg_get_constraintdef(oid) as definition
FROM pg_constraint 
WHERE conrelid IN (
    SELECT oid FROM pg_class WHERE relname IN ('searches', 'people', 'users', 'exclusions')
)
ORDER BY conrelid, conname;