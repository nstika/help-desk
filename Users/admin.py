from django.contrib import admin
from . import models
from .models import Users

# Register your models here.
# admin.register(models.Users)



@admin.register(Users)
class AuthorAdmin(admin.ModelAdmin):
    pass