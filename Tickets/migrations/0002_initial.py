# Generated by Django 4.1.2 on 2023-03-02 08:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Tickets', '0001_initial'),
        ('Users', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='tickets',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='created_by_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='tickets',
            name='userID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='replyticket',
            name='ticketID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='Tickets.tickets'),
        ),
        migrations.AddField(
            model_name='replyticket',
            name='userID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='computerlease',
            name='department',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Users.department'),
        ),
        migrations.AddField(
            model_name='assignticket',
            name='assigned_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='assigned_by_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='assignticket',
            name='ticketID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='Tickets.tickets'),
        ),
        migrations.AddField(
            model_name='assignticket',
            name='userID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to=settings.AUTH_USER_MODEL),
        ),
    ]
