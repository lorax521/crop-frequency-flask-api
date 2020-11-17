#!/bin/bash
exec gunicorn --timeout 150 --workers 2 --threads 4 --bind 0.0.0.0:5000 wsgi:app