#!/bin/sh
set -e
if [ $# -eq 0 ]; then
    exec mimicker serve --port "${MIMICKER_PORT:-8080}"
else
    exec mimicker "$@"
fi
