-- Production-ready NeonDB schema for Bridgit AI
-- All table definitions match live DB audit, use with care.

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- USERS TABLE
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- SESSIONS TABLE
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    auth_code VARCHAR(8) UNIQUE NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    host_user UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT now(),
    ended_at TIMESTAMPTZ
);

-- MESSAGES TABLE
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES sessions(id),
    user_id UUID REFERENCES users(id),
    text TEXT,
    audio_url TEXT,
    original_text TEXT,
    source_language VARCHAR(16),
    target_language VARCHAR(16),
    message_duration NUMERIC,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- VOICES TABLE
CREATE TABLE IF NOT EXISTS voices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    voice_id VARCHAR(128) NOT NULL,
    name VARCHAR(128) NOT NULL,
    description TEXT,
    voice_type VARCHAR(64) DEFAULT 'default',
    is_public BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- AUDIO TABLE (for detached media or solo uploads, if present)
CREATE TABLE IF NOT EXISTS audio (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID REFERENCES messages(id),
    url TEXT NOT NULL,
    duration NUMERIC,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- INDEX AND OPTIMIZATION EXAMPLES
CREATE INDEX IF NOT EXISTS idx_sessions_auth_code ON sessions(auth_code);
CREATE INDEX IF NOT EXISTS idx_messages_session_id ON messages(session_id);

-- Add more tables here as your workflow evolves