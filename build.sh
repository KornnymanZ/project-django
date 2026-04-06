#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

#Fix admin panel css
rm -rf projectdjango/staticfiles
python projectdjango/manage.py collectstatic --no-input
python projectdjango/manage.py migrate

#Hardcode in account because render wipe the thing
python projectdjango/manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
u, created = User.objects.get_or_create(username='65011624', defaults={'email': '65011624@kmitl.ac.th'})
u.is_superuser = True
u.is_staff = True
u.set_password('KmitlAdmin2026!')
u.save()
" || true
