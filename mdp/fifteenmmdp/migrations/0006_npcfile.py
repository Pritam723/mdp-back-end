# Generated by Django 3.1.4 on 2021-02-09 10:14

from django.db import migrations, models
import django.db.models.deletion
import fifteenmmdp.models
import fifteenmmdp.validators


class Migration(migrations.Migration):

    dependencies = [
        ('fifteenmmdp', '0005_auto_20210207_2232'),
    ]

    operations = [
        migrations.CreateModel(
            name='NpcFile',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('fileName', models.CharField(max_length=255)),
                ('filePath', models.CharField(max_length=1023)),
                ('npcFile', models.FileField(upload_to=fifteenmmdp.models.upload_path_npc, validators=[fifteenmmdp.validators.validate_file_extension_npc])),
                ('meterFile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fifteenmmdp.allmeterfiles')),
            ],
        ),
    ]