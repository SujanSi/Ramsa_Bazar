# Generated by Django 5.1.4 on 2025-03-05 06:06

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0009_chatmessage'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Auction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('starting_bid', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('highest_bid', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('highest_bidder', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='winning_bids', to=settings.AUTH_USER_MODEL)),
                ('product', models.OneToOneField(limit_choices_to={'product_type': 'auction'}, on_delete=django.db.models.deletion.CASCADE, related_name='auction', to='shop.product')),
            ],
            options={
                'verbose_name': 'Auction',
            },
        ),
        migrations.CreateModel(
            name='Bid',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('auction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bids', to='shop.auction')),
                ('bidder', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bids', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Bid',
            },
        ),
        migrations.AddIndex(
            model_name='auction',
            index=models.Index(fields=['start_time', 'end_time', 'is_active'], name='shop_auctio_start_t_244811_idx'),
        ),
        migrations.AddIndex(
            model_name='bid',
            index=models.Index(fields=['auction', 'created_at'], name='shop_bid_auction_39f856_idx'),
        ),
    ]
