# Generated by Django 5.0.3 on 2024-09-10 23:40

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_alter_wallet_balance'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='wallet',
            name='stellar_private_key',
            field=models.CharField(blank=True, max_length=56, null=True),
        ),
        migrations.AddField(
            model_name='wallet',
            name='stellar_public_key',
            field=models.CharField(blank=True, max_length=56, null=True),
        ),
        migrations.CreateModel(
            name='CryptoWalletConnectConnection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wallet_address', models.CharField(max_length=255)),
                ('connection_date', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(max_length=50)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CryptoWalletConnectSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_id', models.CharField(max_length=255, unique=True)),
                ('uri', models.URLField(max_length=500)),
                ('connected', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CryptoWalletConnectTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_id', models.CharField(max_length=255, unique=True)),
                ('amount', models.DecimalField(decimal_places=8, max_digits=20)),
                ('currency', models.CharField(max_length=10)),
                ('date', models.DateTimeField()),
                ('status', models.CharField(max_length=50)),
                ('description', models.TextField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='LinkedAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_id', models.CharField(max_length=255)),
                ('provider', models.CharField(choices=[('mono', 'Mono'), ('plaid', 'Plaid')], max_length=50)),
                ('access_token', models.TextField()),
                ('refresh_token', models.TextField(blank=True, null=True)),
                ('linked_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mono_user_id', models.CharField(blank=True, max_length=255, null=True)),
                ('plaid_user_id', models.CharField(blank=True, max_length=255, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('wallet', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='app.wallet')),
            ],
        ),
    ]
