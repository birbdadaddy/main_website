# Generated by Django 5.0.1 on 2024-03-09 00:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0014_rename_class_student_class_obj'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='class',
            name='members',
        ),
        migrations.RemoveField(
            model_name='student',
            name='class_obj',
        ),
        migrations.RemoveField(
            model_name='year',
            name='type',
        ),
        migrations.AddField(
            model_name='class',
            name='students',
            field=models.ManyToManyField(to='main_app.student'),
        ),
        migrations.AddField(
            model_name='year',
            name='class_types',
            field=models.ManyToManyField(to='main_app.classtype'),
        ),
        migrations.AlterField(
            model_name='classtype',
            name='name',
            field=models.CharField(choices=[('apic', 'APIC'), ('agse', 'AGSE')], max_length=50),
        ),
        migrations.AlterField(
            model_name='year',
            name='year',
            field=models.CharField(choices=[('year1', 'Year 1'), ('year2', 'Year 2'), ('year3', 'Year 3')], max_length=10, verbose_name='Year:'),
        ),
    ]