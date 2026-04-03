#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python projectdjango/manage.py collectstatic --no-input
python projectdjango/manage.py migrate

# Automatically spawn a Master Admin account securely bypassing the missing Shell access!
python projectdjango/manage.py createsuperuser --noinput --username admin --email admin@collaborative.com || true
