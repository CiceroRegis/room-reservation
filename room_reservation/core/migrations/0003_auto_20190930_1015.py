# Generated by Django 2.2.2 on 2019-09-30 13:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20190929_0006'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reservation',
            name='calendarOwnerTID',
            field=models.IntegerField(default=179021546, editable=False),
        ),
    ]