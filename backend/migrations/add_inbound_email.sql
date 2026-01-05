-- Migration: Add inbound_email column to users table
-- Run this in your Railway PostgreSQL or local database

-- Add inbound_email column to users table
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS inbound_email VARCHAR(255) UNIQUE;

-- Create index for fast lookups by inbound email
CREATE INDEX IF NOT EXISTS idx_users_inbound_email ON users(inbound_email);

-- Add source column to documents table (to track email vs web upload)
ALTER TABLE documents 
ADD COLUMN IF NOT EXISTS source VARCHAR(50) DEFAULT 'web';

-- Create inbound_email_errors table for tracking failed email processing
CREATE TABLE IF NOT EXISTS inbound_email_errors (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    sender_email VARCHAR(255) NOT NULL,
    filename VARCHAR(255),
    error_message TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for fetching errors by user
CREATE INDEX IF NOT EXISTS idx_inbound_email_errors_user_id ON inbound_email_errors(user_id);

-- Backfill inbound_email for existing users
-- This generates a unique email based on their user ID hash
UPDATE users 
SET inbound_email = 'user_' || SUBSTRING(encode(sha256(id::bytea), 'hex'), 1, 8) || '@readableedi.com'
WHERE inbound_email IS NULL;
