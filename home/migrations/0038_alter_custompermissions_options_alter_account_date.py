# Generated by Django 5.0 on 2024-12-12 10:43

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0037_alter_account_date_alter_store_purchase_note_project'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='custompermissions',
            options={'permissions': [('view_dashboard', 'Can view dashboard'), ('view_balance_sheet', 'Can view balance sheet'), ('view_store', 'Can view store'), ('view_inventory', 'Can view inventory')]},
        ),
        migrations.AlterField(
            model_name='account',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2024, 12, 12, 15, 43, 6, 617150)),
        ),
    ]
