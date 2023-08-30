from django.contrib import admin
from . import models

# Register your models here.


# admin.register(models.Category)
from .models import Tickets


@admin.register(Tickets)
class AthorAdmin(admin.ModelAdmin):
    pass

admin.site.register(models.Category)
admin.site.register(models.ReplyTicket)

