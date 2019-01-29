#!/bin/sh
python manage.py migrate && gunicorn contty.wsgi --bind 0.0.0.0
