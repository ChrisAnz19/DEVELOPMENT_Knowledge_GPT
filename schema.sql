-- Knowledge_GPT Database Schema
-- Run this in your Supabase SQL Editor

-- Table to store each search request and its metadata
CREATE TABLE IF NOT EXISTS searches (
    id SERIAL PRIMARY KEY,
    request_id VARCHAR(255) UNIQUE NOT NULL,
    prompt TEXT NOT NULL,
    filters JSONB,
    behavioral_data JSONB,
    status VARCHAR(50) DEFAULT 'processing',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    error TEXT
);

-- Table to store each candidate returned for a search
CREATE TABLE IF NOT EXISTS candidates (
    id SERIAL PRIMARY KEY,
    search_id INTEGER REFERENCES searches(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    title VARCHAR(255),
    company VARCHAR(255),
    email VARCHAR(255),
    linkedin_url TEXT,
    profile_photo_url TEXT,
    location VARCHAR(255),
    accuracy INTEGER,
    reasons JSONB,
    linkedin_profile JSONB,
    linkedin_posts JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for 30-day candidate exclusion system
CREATE TABLE IF NOT EXISTS candidate_exclusions (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    company VARCHAR(255),
    excluded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL '30 days'),
    reason VARCHAR(255) DEFAULT 'Previously processed'
);

-- Indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_searches_request_id ON searches(request_id);
CREATE INDEX IF NOT EXISTS idx_candidates_search_id ON candidates(search_id);
CREATE INDEX IF NOT EXISTS idx_candidate_exclusions_email ON candidate_exclusions(email);
CREATE INDEX IF NOT EXISTS idx_candidate_exclusions_expires ON candidate_exclusions(expires_at);

-- Optional: Add some sample data for testing
-- INSERT INTO searches (request_id, prompt, status, created_at, completed_at) 
-- VALUES ('test-123', 'Find marketing directors in San Francisco', 'completed', NOW(), NOW());

-- INSERT INTO candidates (search_id, name, title, company, email, accuracy) 
-- VALUES (1, 'John Doe', 'Marketing Director', 'Tech Corp', 'john@techcorp.com', 85); 