# Generated by Django 3.0.3 on 2020-07-11 18:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ABapp', '0007_auto_20200711_2226'),
    ]

    operations = [
        migrations.CreateModel(
            name='Hcsavings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('toolname', models.CharField(max_length=20)),
                ('toolcompletiondate', models.DateField(max_length=10)),
                ('hcsavings', models.IntegerField()),
            ],
        ),
    ]
