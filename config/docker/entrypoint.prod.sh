#!/bin/sh

python3 manage.py collectstatic --no-input

exec "$@"