# Generated by Django 2.0.6 on 2018-06-29 18:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dbus', '0017_delete_forecast_weather'),
    ]

    operations = [
        migrations.CreateModel(
            name='forecast',
            fields=[
                ('datetime', models.DateTimeField(primary_key=True, serialize=False)),
                ('temp', models.FloatField()),
                ('min_temp', models.FloatField()),
                ('max_temp', models.FloatField()),
                ('description', models.TextField()),
                ('mainDescription', models.TextField()),
                ('wind_speed', models.FloatField()),
                ('wind_direction', models.FloatField()),
                ('humidity', models.FloatField()),
            ],
        ),
    ]
