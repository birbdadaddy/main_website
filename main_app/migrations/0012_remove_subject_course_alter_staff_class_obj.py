# Generated by Django 5.0.1 on 2024-03-20 22:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0011_remove_staff_course_staff_class_obj_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subject',
            name='course',
        ),
        migrations.AlterField(
            model_name='staff',
            name='class_obj',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='main_app.class', verbose_name='Class:'),
        ),
    ]