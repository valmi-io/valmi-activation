# Launches jobs on dagster according to the schedule
# Handles failures and retries
# Be on top of job runs and their status. Store state in the db.
# Provide API for the frontend to query the status of the runs
# Provide API for the frontend to save source and destination checkpoints
# Provide Pull API for Synchronising the source and destination. And even sources and destinations ask whether to fail or continue.
# Listen to Sources and Destinations for Control Messsages Like Oauth refreshes| Destination unreachable | Source unreachable
# OAUTH refreshes should be done by the api Server (its responsibility is crendential management & configuration). This server is responsible for (job run & meta data management).
