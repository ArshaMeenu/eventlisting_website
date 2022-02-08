# Generated by Django 4.0.1 on 2022-01-25 08:34

from django.db import migrations
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0003_alter_customuser_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='phone',
        ),
        migrations.AddField(
            model_name='customuser',
            name='phone_no',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=10, null=True, region=None, unique=True, verbose_name='Mobile Number'),
        ),
    ]