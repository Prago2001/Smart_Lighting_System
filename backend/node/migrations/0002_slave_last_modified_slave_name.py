# Generated by Django 4.1.1 on 2022-09-28 06:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('node', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='slave',
            name='last_modified',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='slave',
            name='name',
            field=models.CharField(default='Street Light ', max_length=255),
        ),
    ]
