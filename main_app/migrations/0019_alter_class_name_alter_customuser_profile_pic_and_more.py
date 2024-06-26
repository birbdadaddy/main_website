# Generated by Django 5.0.1 on 2024-04-14 22:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0018_remove_notification_user_notification_users'),
    ]

    operations = [
        migrations.AlterField(
            model_name='class',
            name='name',
            field=models.IntegerField(verbose_name='Number:'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='profile_pic',
            field=models.ImageField(blank=True, default=None, null=True, upload_to='', verbose_name='Profile picture: '),
        ),
        migrations.AlterField(
            model_name='student',
            name='class_obj',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='main_app.class', verbose_name='Class:'),
        ),
        migrations.AlterField(
            model_name='student',
            name='massar',
            field=models.CharField(default='P', max_length=20, verbose_name='Massar Number:'),
        ),
    ]
