-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create database if it doesn't exist (this will be run by docker-entrypoint)
-- The database is already created by the POSTGRES_DB environment variable