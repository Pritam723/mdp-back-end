# Generated by Django 3.1.4 on 2021-02-10 09:20

from django.db import migrations, models
import fifteenmmdp.models
import fifteenmmdp.validators


class Migration(migrations.Migration):

    dependencies = [
        ('fifteenmmdp', '0006_npcfile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='allmeterfiles',
            name='zippedMeterFile',
            field=models.FileField(max_length=1023, upload_to=fifteenmmdp.models.upload_path, validators=[fifteenmmdp.validators.validate_file_extension]),
        ),
        migrations.AlterField(
            model_name='npcfile',
            name='npcFile',
            field=models.FileField(max_length=1023, storage=fifteenmmdp.models.OverwriteStorage(), upload_to=fifteenmmdp.models.upload_path_npc, validators=[fifteenmmdp.validators.validate_file_extension_npc]),
        ),
    ]