# Generated by Django 4.2.16 on 2024-10-04 15:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_class_days_of_week'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='topics',
            options={'ordering': ['-name']},
        ),
    ]
