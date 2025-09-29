-- src/models.sql

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS videos (
    id BIGSERIAL PRIMARY KEY,
    video_id TEXT,
    title TEXT,
    description TEXT,
    channel_id TEXT,
    recorded_at TIMESTAMPTZ NOT NULL,
    published_at TIMESTAMPTZ,
    category_id TEXT
);

CREATE TABLE IF NOT EXISTS video_stats (
    id BIGSERIAL PRIMARY KEY,
    video_id TEXT REFERENCES videos(video_id),
    recorded_at TIMESTAMPTZ NOT NULL,
    view_count BIGINT,
    like_count BIGINT,
    comment_count BIGINT,
    UNIQUE (video_id, recorded_at)
);

CREATE TABLE IF NOT EXISTS trends_queries (
    id BIGSERIAL PRIMARY KEY,
    query TEXT NOT NULL,
    search_volume BIGINT,
    region TEXT,
    category_id TEXT,
    retrieved_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS etl_runs (
    id BIGSERIAL PRIMARY KEY,
    job_name TEXT,
    status TEXT,
    started_at TIMESTAMPTZ,
    finished_at TIMESTAMPTZ,
    details TEXT
);
