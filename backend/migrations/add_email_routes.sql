-- Migration: Add email_routes table
-- Run this in your Railway PostgreSQL or local database

CREATE TABLE IF NOT EXISTS email_routes (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id),
    transaction_type VARCHAR(50) NOT NULL,
    email_addresses TEXT[] NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, transaction_type)
);

-- Create index for fast lookups
CREATE INDEX IF NOT EXISTS idx_email_routes_lookup ON email_routes(user_id, transaction_type);
