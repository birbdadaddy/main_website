# Generated by Django 5.0.1 on 2024-03-08 12:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0007_alter_year_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='year',
            name='classes',
            field=models.TextField(max_length=50, verbose_name='Class:'),
        ),
    ]
