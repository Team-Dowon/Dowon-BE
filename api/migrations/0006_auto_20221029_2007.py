# Generated by Django 3.0.8 on 2022-10-29 20:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_test'),
    ]

    operations = [
        migrations.AlterField(
            model_name='test',
            name='photo',
            field=models.ImageField(upload_to=''),
        ),
    ]
