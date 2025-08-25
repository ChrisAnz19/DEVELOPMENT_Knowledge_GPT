-- Add evidence columns to people table
-- This migration adds the evidence URL fields that were missing from the schema

ALTER TABLE people 
ADD COLUMN IF NOT EXISTS evidence_urls TEXT,
ADD COLUMN IF NOT EXISTS evidence_summary TEXT,
ADD COLUMN IF NOT EXISTS evidence_confidence DECIMAL(3,2);

-- Add comments to document the new columns
COMMENT ON COLUMN people.evidence_urls IS 'JSON array of evidence URLs supporting the candidate match';
COMMENT ON COLUMN people.evidence_summary IS 'Human-readable summary of evidence found';
COMMENT ON COLUMN people.evidence_confidence IS 'Confidence score (0-1) based on evidence quality and quantity';