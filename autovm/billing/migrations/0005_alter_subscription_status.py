# Generated by Django 5.0.9 on 2024-09-12 14:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0004_alter_billingaccount_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=10),
        ),
    ]
