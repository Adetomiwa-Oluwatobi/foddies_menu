# Generated by Django 5.1.1 on 2024-09-21 07:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_alter_order_status'),
    ]

    operations = [
        migrations.RenameField(
            model_name='payment',
            old_name='price',
            new_name='amount',
        ),
        migrations.RenameField(
            model_name='payment',
            old_name='created_at',
            new_name='payment_date',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='item',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='status',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='table_number',
        ),
        migrations.AddField(
            model_name='payment',
            name='order',
            field=models.OneToOneField(default=21, on_delete=django.db.models.deletion.CASCADE, related_name='payment', to='myapp.order'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='payment',
            name='payment_reference',
            field=models.CharField(default=23, max_length=255, unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='payment',
            name='payment_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending', max_length=20),
        ),
    ]
