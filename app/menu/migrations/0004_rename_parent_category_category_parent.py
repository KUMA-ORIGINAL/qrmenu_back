# Generated by Django 5.1 on 2025-01-06 22:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0003_alter_category_options_remove_category_description_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='category',
            old_name='parent_category',
            new_name='parent',
        ),
    ]
