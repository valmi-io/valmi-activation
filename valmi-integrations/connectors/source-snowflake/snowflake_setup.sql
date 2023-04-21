-- Create a role for the valmi user
CREATE ROLE VALMI_ROLE;

-- Ensure the sysadmin role inherits any privileges the valmi role is granted. Note that this does not grant sysadmin privileges to the valmi role
GRANT ROLE VALMI_ROLE TO ROLE SYSADMIN;

-- Create a warehouse for the valmi user, optimizing for cost over performance
CREATE WAREHOUSE VALMI_WAREHOUSE WITH WAREHOUSE_SIZE = XSMALL AUTO_SUSPEND = 60 AUTO_RESUME = TRUE INITIALLY_SUSPENDED = FALSE;

-- Allow the valmi user to run queries in the warehouse
GRANT USAGE ON WAREHOUSE VALMI_WAREHOUSE TO ROLE VALMI_ROLE;

-- Allow the valmi user to start and stop the warehouse and abort running queries in the warehouse
GRANT OPERATE ON WAREHOUSE VALMI_WAREHOUSE TO ROLE VALMI_ROLE;

-- Allow the valmi user to see historical query statistics on queries in its warehouse
GRANT MONITOR ON WAREHOUSE VALMI_WAREHOUSE TO ROLE VALMI_ROLE;

-- Create the valmi user
-- Do not set DEFAULT_WORKSPACE, this will impact which tables are visible to Census
CREATE USER VALMI WITH DEFAULT_ROLE = VALMI_ROLE DEFAULT_WAREHOUSE = VALMI_WAREHOUSE PASSWORD = '<strong, unique password>';

-- Grant the valmi role to the valmi user
GRANT ROLE VALMI_ROLE TO USER VALMI;

-- Create a private bookkeeping database where Census can store sync state
-- Skip this step if working in read-only mode
CREATE DATABASE "VALMI";

-- Give the valmi user full access to the bookkeeping database
-- Skip this step if working in read-only mode
GRANT ALL PRIVILEGES ON DATABASE "VALMI" TO ROLE VALMI_ROLE;

-- Create a private bookkeeping schema where Census can store sync state
-- Skip this step if working in read-only mode
CREATE SCHEMA "VALMI"."VALMI";

-- Give the valmi user full access to the bookkeeping schema
-- Skip this step if working in read-only mode
GRANT ALL PRIVILEGES ON SCHEMA "VALMI"."VALMI" TO ROLE VALMI_ROLE;

-- Give the valmi user the ability to create stages for unloading data
-- Skip this step if working in read-only mode
GRANT CREATE STAGE ON SCHEMA "VALMI"."VALMI" TO ROLE VALMI_ROLE;

-- Let the valmi user see this database
GRANT USAGE ON DATABASE "<your database>" TO ROLE VALMI_ROLE;

-- Let the valmi user see this schema
GRANT USAGE ON SCHEMA "<your database>"."<your schema>" TO ROLE VALMI_ROLE;

-- Let the valmi user read all existing tables in this schema
GRANT SELECT ON ALL TABLES IN SCHEMA "<your database>"."<your schema>" TO ROLE VALMI_ROLE;

-- Let the valmi user read any new tables added to this schema
GRANT SELECT ON FUTURE TABLES IN SCHEMA "<your database>"."<your schema>" TO ROLE VALMI_ROLE;

-- Let the valmi user read all existing views in this schema
GRANT SELECT ON ALL VIEWS IN SCHEMA "<your database>"."<your schema>" TO ROLE VALMI_ROLE;

-- Let the valmi user read any new views added to this schema
GRANT SELECT ON FUTURE VIEWS IN SCHEMA "<your database>"."<your schema>" TO ROLE VALMI_ROLE;

-- Let the valmi user execute any existing functions in this schema
GRANT USAGE ON ALL FUNCTIONS IN SCHEMA "<your database>"."<your schema>" TO ROLE VALMI_ROLE;

-- Let the valmi user execute any new functions added to this schema
GRANT USAGE ON FUTURE FUNCTIONS IN SCHEMA "<your database>"."<your schema>" TO ROLE VALMI_ROLE;
