# Generated by Django 5.0 on 2024-11-30 17:13

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0027_sales_receipt_customer_alter_account_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='sales_receipt',
            name='is_cash',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='account',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2024, 11, 30, 22, 13, 3, 574985)),
        ),
    ]
