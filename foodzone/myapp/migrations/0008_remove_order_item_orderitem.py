# Generated by Django 5.2 on 2025-05-11 11:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0007_cart_cartitem'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='item',
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('price', models.FloatField()),
                ('dish', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.dish')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='myapp.order')),
            ],
            options={
                'verbose_name_plural': 'Order Item Table',
            },
        ),
    ]
