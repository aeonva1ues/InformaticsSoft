# Generated by Django 3.2 on 2022-08-21 13:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('performancetech', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='WebPresentation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('creation_date', models.DateField()),
                ('is_active', models.BooleanField(default=True)),
                ('files', models.TextField()),
            ],
        ),
    ]
