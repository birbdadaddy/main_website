# Generated by Django 5.0.1 on 2024-03-08 15:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0009_rename_course_student_class_student_massar_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='massar',
            field=models.CharField(default='P', max_length=20),
        ),
    ]
