# Generated by Django 5.1 on 2025-05-21 08:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('venues', '0027_remove_spot_slug'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkingHours',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_of_week', models.IntegerField(choices=[(0, 'Понедельник'), (1, 'Вторник'), (2, 'Среда'), (3, 'Четверг'), (4, 'Пятница'), (5, 'Суббота'), (6, 'Воскресенье')], verbose_name='День недели')),
                ('open_time', models.TimeField(verbose_name='Время открытия')),
                ('close_time', models.TimeField(verbose_name='Время закрытия')),
                ('is_closed', models.BooleanField(default=False, verbose_name='Закрыто')),
                ('venue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='working_hours', to='venues.venue', verbose_name='Заведение')),
            ],
            options={
                'verbose_name': 'График работы',
                'verbose_name_plural': 'Графики работы',
                'ordering': ['day_of_week'],
                'unique_together': {('venue', 'day_of_week')},
            },
        ),
    ]
