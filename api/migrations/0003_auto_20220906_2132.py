# Generated by Django 3.0.8 on 2022-09-06 21:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_comment_post'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='color',
            field=models.CharField(default='#000000', max_length=7),
        ),
    ]
