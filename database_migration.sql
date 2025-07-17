-- Database Migration: Add behavioral_data column to people table
-- Run this in your Supabase SQL Editor to update existing tables

-- Add behavioral_data column to people table if it doesn't exist
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