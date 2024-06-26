# Generated by Django 5.0.1 on 2024-03-09 18:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='year',
            old_name='year',
            new_name='name',
        ),
        migrations.RemoveField(
            model_name='class',
            name='students',
        ),
        migrations.RemoveField(
            model_name='classtype',
            name='classes',
        ),
        migrations.RemoveField(
            model_name='year',
            name='type',
        ),
        migrations.AddField(
            model_name='class',
            name='type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='main_app.classtype'),
        ),
        migrations.AddField(
            model_name='classtype',
            name='year',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='main_app.year'),
        ),
        migrations.AddField(
            model_name='student',
            name='class_obj',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='main_app.class'),
        ),
    ]
