# Generated by Django 4.1.1 on 2022-09-28 06:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('node', '0002_slave_last_modified_slave_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='slave',
            name='dim_val',
            field=models.IntegerField(choices=[(0, '0'), (25, '25'), (50, '50'), (75, '75'), (100, '100')], default=25),
        ),
    ]
