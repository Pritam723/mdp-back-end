# Generated by Django 3.1.4 on 2021-03-07 14:51

from django.db import migrations, models
import fifteenmmdp.models


class Migration(migrations.Migration):

    dependencies = [
        ('fifteenmmdp', '0023_finaloutputfile'),
    ]

    operations = [
        migrations.CreateModel(
            name='NecessaryFile',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('fileName', models.CharField(max_length=1023, null=True)),
                ('filePath', models.CharField(max_length=1023, null=True)),
                ('subTitle', models.TextField(null=True)),
                ('description', models.TextField(null=True)),
                ('necessaryFile', models.FileField(max_length=1023, upload_to=fifteenmmdp.models.upload_path_necessaryFile)),
            ],
        ),
    ]