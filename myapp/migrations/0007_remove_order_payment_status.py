# Generated by Django 5.1.1 on 2024-09-22 12:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0006_order_payment_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='payment_status',
        ),
    ]
