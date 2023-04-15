# Generated by Django 4.1.4 on 2023-04-13 12:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('node', '0008_alter_notification_operation_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='Energy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField(null=True)),
                ('consumption', models.FloatField(null=True)),
                ('saved', models.FloatField(null=True)),
                ('intensity', models.IntegerField(choices=[(0, '0'), (25, '25'), (50, '50'), (75, '75'), (100, '100')], default=25)),
                ('mains', models.BooleanField()),
            ],
        ),
    ]
