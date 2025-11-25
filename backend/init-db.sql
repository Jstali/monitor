-- This file is automatically executed when PostgreSQL container starts for the first time
-- It ensures the database and user are properly configured

-- The database 'monitor' is already created by POSTGRES_DB environment variable
-- This file can be used for additional initialization if needed

-- Grant all privileges to postgres user (already done by default)
GRANT ALL PRIVILEGES ON DATABASE monitor TO postgres;

-- You can add additional initialization SQL here if needed
-- For example: creating extensions, setting up schemas, etc.

-- Example: Enable UUID extension (uncomment if needed)
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
