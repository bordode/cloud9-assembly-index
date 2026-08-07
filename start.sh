#!/bin/sh
# start.sh - start the Cloud-9 Assembly Index app using gunicorn
set -e
PORT=${PORT:-8080}
exec gunicorn main:app --bind 0.0.0.0:${PORT}
