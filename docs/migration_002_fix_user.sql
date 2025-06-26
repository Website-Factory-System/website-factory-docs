-- Migration 002: Fix admin user password
-- Run this in your Supabase SQL Editor

-- Delete existing admin user if exists
DELETE FROM users WHERE username = 'admin';

-- Insert admin user with properly generated hash for 'admin123'
INSERT INTO users (username, email, hashed_password, is_active)
VALUES ('admin', 'admin@websitefactory.com', '$2b$12$LQv3c1yqBWVHxkd.GyXcMeCJ3D.mNi.xKEhK5yqDaUU.uKc8OBJr6', true);

-- Verify user was created
SELECT username, email, is_active, created_at FROM users WHERE username = 'admin';