# Generated by Django 5.0.1 on 2024-03-08 11:08

import main_app.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0004_alter_year_classes'),
    ]

    operations = [
        migrations.CreateModel(
            name='Class',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10, verbose_name=main_app.models.Year)),
                ('members', models.CharField(max_length=50)),
            ],
        ),
        migrations.AlterField(
            model_name='year',
            name='classes',
            field=models.CharField(max_length=50, verbose_name='Class:'),
        ),
        migrations.AlterField(
            model_name='year',
            name='name',
            field=models.CharField(choices=[('year1', 'Year 1'), ('year2', 'Year 2'), ('year3', 'Year 3')], max_length=10, verbose_name='Year:'),
        ),
    ]
