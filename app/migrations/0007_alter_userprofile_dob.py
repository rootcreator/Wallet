# Generated by Django 5.0.3 on 2024-09-18 23:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_rename_bio_userprofile_dob'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='dob',
            field=models.DateField(blank=True, max_length=500, null=True),
        ),
    ]
