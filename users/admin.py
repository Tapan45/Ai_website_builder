from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser  # use your actual user model name

admin.site.register(CustomUser, UserAdmin)
