# Generated by Django 3.2.6 on 2021-08-28 12:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administrator', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='is_paid',
        ),
        migrations.AddField(
            model_name='event',
            name='cost',
            field=models.CharField(choices=[('CONFERENCE', 'CONFERENCE'), ('SEMINAR', 'SEMINAR'), ('WORKSHOP', 'WORKSHOP')], max_length=200, null=True),
        ),
    ]