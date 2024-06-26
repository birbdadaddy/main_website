# Generated by Django 5.0.1 on 2024-03-09 18:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0002_rename_year_year_name_remove_class_students_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classtype',
            name='name',
            field=models.CharField(choices=[('APIC', 'APIC'), ('AGSE', 'AGSE')], max_length=50),
        ),
        migrations.AlterField(
            model_name='year',
            name='name',
            field=models.CharField(choices=[('year1', 'Year 1'), ('year2', 'Year 2'), ('year3', 'Year 3')], max_length=10, unique=True, verbose_name='Year:'),
        ),
    ]
