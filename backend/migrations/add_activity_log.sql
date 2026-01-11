-- Activity Log Migration
-- Tracks user actions for admin analytics

CREATE TABLE IF NOT EXISTS activity_log (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL,
    user_email VARCHAR(255),  -- Denormalized for faster queries
    action VARCHAR(50) NOT NULL,  -- 'conversion', 'login', 'layout_edit', 'download', etc.
    details JSONB DEFAULT '{}',  -- Action-specific metadata
    ip_address VARCHAR(45),  -- IPv4 or IPv6
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_activity_log_user_id ON activity_log(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_log_action ON activity_log(action);
CREATE INDEX IF NOT EXISTS idx_activity_log_created_at ON activity_log(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_activity_log_user_action ON activity_log(user_id, action);

-- Add last_active_at column to users table for quick "active users" queries
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_active_at TIMESTAMP WITH TIME ZONE;

-- Create index for last_active_at
CREATE INDEX IF NOT EXISTS idx_users_last_active ON users(last_active_at DESC);

-- Comments for documentation
COMMENT ON TABLE activity_log IS 'Tracks user actions for admin analytics and traffic monitoring';
COMMENT ON COLUMN activity_log.action IS 'Action types: conversion, login, download, layout_edit, layout_reset';
COMMENT ON COLUMN activity_log.details IS 'JSON with action-specific data: transaction_type, filename, layout_type, etc.';
