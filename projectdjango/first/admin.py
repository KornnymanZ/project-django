from django.contrib import admin
from django.contrib.auth.models import Group
from .models import AppUser
from .models import Team

# Register your models here.
admin.site.register(AppUser)
admin.site.register(Team)