# Generated by Django 3.2.4 on 2021-06-18 20:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='id_campus',
            field=models.PositiveSmallIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='group',
            name='name',
            field=models.CharField(max_length=500, null=True),
        ),
    ]
