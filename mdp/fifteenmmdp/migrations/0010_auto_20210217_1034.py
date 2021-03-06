# Generated by Django 3.1.4 on 2021-02-17 05:04

from django.db import migrations, models
import django.db.models.deletion
import fifteenmmdp.models
import fifteenmmdp.validators


class Migration(migrations.Migration):

    dependencies = [
        ('fifteenmmdp', '0009_allmeterfiles_mergedfile'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='allmeterfiles',
            name='mergedFile',
        ),
        migrations.CreateModel(
            name='MergedFile',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('fileName', models.CharField(max_length=255)),
                ('filePath', models.CharField(max_length=1023)),
                ('mergedFile', models.FileField(max_length=1023, null=True, storage=fifteenmmdp.models.OverwriteStorage(), upload_to=fifteenmmdp.models.upload_path_mergedFile, validators=[fifteenmmdp.validators.validate_file_extension_npc])),
                ('meterFile', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='fifteenmmdp.allmeterfiles')),
            ],
        ),
    ]
