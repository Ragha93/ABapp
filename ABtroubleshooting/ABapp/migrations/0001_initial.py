# Generated by Django 3.0.3 on 2020-07-05 14:05

from django.conf import settings
import django.contrib.auth.models
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AB_data',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asin1', models.SlugField(max_length=10, validators=[django.core.validators.MinLengthValidator(10)])),
                ('buyability_trace', models.CharField(blank=True, max_length=200, null=True)),
                ('Item', models.CharField(blank=True, max_length=200, null=True)),
                ('Contribution', models.CharField(blank=True, max_length=200, null=True)),
                ('Price_OLSListing', models.CharField(blank=True, max_length=200, null=True)),
                ('Price_BUYListing', models.CharField(blank=True, max_length=200, null=True)),
                ('Xref', models.CharField(blank=True, max_length=200, null=True)),
                ('Shipping_cost', models.CharField(blank=True, max_length=200, null=True)),
                ('AvailabilityGpi', models.CharField(blank=True, max_length=200, null=True)),
                ('Offer_Blacklist', models.CharField(blank=True, max_length=200, null=True)),
                ('Seller_Suppression', models.CharField(blank=True, max_length=200, null=True)),
                ('Explicit_Settlement', models.CharField(blank=True, max_length=200, null=True)),
                ('Backend_buyability', models.CharField(blank=True, max_length=200, null=True)),
                ('blacklist_user', models.CharField(blank=True, max_length=300, null=True)),
                ('sourceability_status', models.CharField(blank=True, max_length=200, null=True)),
                ('sourceability_reason', models.CharField(blank=True, max_length=100, null=True)),
                ('procurability_status', models.CharField(blank=True, max_length=200, null=True)),
                ('procurability_explanation', models.CharField(blank=True, max_length=200, null=True)),
                ('IPCstatus', models.CharField(blank=True, max_length=200, null=True)),
                ('sourcinginstockstatus', models.CharField(blank=True, max_length=200, null=True)),
                ('Vendorcode', models.CharField(blank=True, max_length=200, null=True)),
                ('Reason', models.CharField(blank=True, max_length=200, null=True)),
                ('IPCReason', models.CharField(blank=True, max_length=200, null=True)),
                ('allocatedto', models.CharField(blank=True, max_length=20, null=True)),
                ('runtime', models.TimeField(blank=True, max_length=100, null=True, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='AB_template',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asin', models.SlugField(max_length=10, unique=True, validators=[django.core.validators.MinLengthValidator(10)], verbose_name='ASIN')),
                ('vendorcode', models.CharField(max_length=6)),
                ('allocatedto', models.CharField(max_length=20)),
                ('runby', models.CharField(default=django.contrib.auth.models.User, max_length=20)),
                ('allocationdate', models.DateField(default=django.utils.timezone.now, max_length=100)),
                ('loadtime', models.TimeField(default=django.utils.timezone.now, max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='AB_troubleshooting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asin', models.SlugField(max_length=10, unique=True, validators=[django.core.validators.MinLengthValidator(10)], verbose_name='ASIN')),
                ('vendorcode', models.CharField(max_length=6)),
                ('allocatedto', models.CharField(max_length=20)),
                ('runby', models.CharField(default=django.contrib.auth.models.User, max_length=20)),
                ('allocationdate', models.DateField(default=django.utils.timezone.now, max_length=100)),
                ('loadtime', models.TimeField(default=django.utils.timezone.now, max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Userinfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('team_name', models.CharField(max_length=100)),
                ('register_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]