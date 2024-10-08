# Generated by Django 4.2.16 on 2024-10-03 14:16

from django.db import migrations
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_alter_clubs_name_class'),
    ]

    operations = [
        migrations.AddField(
            model_name='class',
            name='days_of_week',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('sun', 'Sunday'), ('mon', 'Monday'), ('tue', 'Tuesday'), ('wed', 'Wednesday'), ('thu', 'Thursday'), ('fri', 'Friday'), ('sat', 'Saturday')], max_length=27, null=True),
        ),
    ]
