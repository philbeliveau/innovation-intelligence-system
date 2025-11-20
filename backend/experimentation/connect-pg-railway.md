⏺ Plan: Connect Experimentation System to Railway PostgreSQL

  1. Database Schema Migration

  Create new tables in existing PostgreSQL database:
  -- Few-shot examples
  CREATE TABLE few_shot_examples (
      id SERIAL PRIMARY KEY,
      stage VARCHAR(50),
      input_context JSONB,
      output_example JSONB,
      quality_score FLOAT,
      brand_context JSONB,
      created_at TIMESTAMP DEFAULT NOW()
  );

  -- Prompt templates
  CREATE TABLE prompt_templates (
      id UUID PRIMARY KEY,
      stage VARCHAR(50),
      name VARCHAR(100),
      category VARCHAR(50),
      prompt_template TEXT,
      avg_quality_score FLOAT,
      usage_count INT DEFAULT 0
  );

  -- Pipeline experiments
  CREATE TABLE pipeline_experiments (
      id UUID PRIMARY KEY,
      brand_profile JSONB,
      stage_outputs JSONB,
      quality_scores JSONB,
      configuration JSONB,
      founder_notes TEXT,
      created_at TIMESTAMP DEFAULT NOW()
  );

  -- Trend filter configs
  CREATE TABLE filter_configurations (
      id SERIAL PRIMARY KEY,
      name VARCHAR(100),
      config JSONB,
      success_rate FLOAT
  );

  2. Update Python Modules

  Replace SQLite connections with PostgreSQL using existing DATABASE_URL:
  import psycopg2
  from psycopg2.extras import RealDictCursor
  import os

  class DatabaseConnection:
      def __init__(self):
          self.database_url = os.getenv("DATABASE_URL")

      def get_connection(self):
          return psycopg2.connect(
              self.database_url,
              cursor_factory=RealDictCursor
          )

  3. Migration Path

  - Use same DATABASE_URL from Railway environment
  - All modules share single connection pool
  - JSONB for flexible data storage
  - Indexes on frequently queried fields

  4. Benefits

  - Persistent: Data survives deployments
  - Shareable: Founder accesses same data from anywhere
  - Scalable: No file size limits
  - Queryable: SQL for advanced analytics
  - Integrated: Same DB as production pipeline

  5. Implementation Steps

  1. Add migration script to create tables
  2. Update each module (few_shot_manager.py, etc.) to use PostgreSQL
  3. Add connection pooling for performance
  4. Create backup/restore utilities
  5. Add data export features for analysis

  This connects your experimentation system to your production infrastructure, making it a true learning
  system that improves your pipeline over time.