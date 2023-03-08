#!/bin/sh
cd /workspace/src && alembic upgrade head
"$@"
