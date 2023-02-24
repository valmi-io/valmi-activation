#!/bin/sh
python import_storage_to_stdin.py | $VALMI_ENTRYPOINT "$@" 

