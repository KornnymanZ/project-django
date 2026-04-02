#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python projectdjango/manage.py collectstatic --no-input
python projectdjango/manage.py migrate
