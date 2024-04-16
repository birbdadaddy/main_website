from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0010_alter_student_massar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='class_obj',  # Update to the actual name of the field in your 'Student' model
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='main_app.Class'),
        ),
    ]
