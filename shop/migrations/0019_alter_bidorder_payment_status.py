# Generated by Django 5.1.4 on 2025-04-09 05:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0018_bidorder_payment_status_alter_bidorder_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bidorder',
            name='payment_status',
            field=models.CharField(choices=[('Khalti', 'Khalti'), ('Cash on Delevery', 'Cash on Delevery')], default='Cash on Delevery', max_length=255),
        ),
    ]
