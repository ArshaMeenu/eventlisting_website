# Generated by Django 4.0.1 on 2022-01-25 18:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0004_remove_customuser_phone_customuser_phone_no'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='phone_no',
        ),
    ]