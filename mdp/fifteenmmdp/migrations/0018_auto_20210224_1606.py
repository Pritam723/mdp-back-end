# Generated by Django 3.1.4 on 2021-02-24 10:36

from django.db import migrations, models
import django.db.models.deletion
import fifteenmmdp.models
import fifteenmmdp.validators


class Migration(migrations.Migration):

    dependencies = [
        ('fifteenmmdp', '0017_auto_20210224_1445'),
    ]

    operations = [
        migrations.AlterField(
            model_name='realmetermwhfile',
            name='meterFile',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='fifteenmmdp.allmeterfiles'),
        ),
        migrations.AlterField(
            model_name='realmetermwhfile',
            name='realMeterMWHFile',
            field=models.FileField(max_length=1023, storage=fifteenmmdp.models.OverwriteStorage(), upload_to=fifteenmmdp.models.upload_path_realMeterMWH, validators=[fifteenmmdp.validators.validate_file_extension]),
        ),
    ]
