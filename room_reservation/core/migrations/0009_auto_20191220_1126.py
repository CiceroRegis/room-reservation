# Generated by Django 2.2.2 on 2019-12-20 14:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20191220_1124'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reservation',
            name='calendarOwnerTID',
            field=models.IntegerField(default=998085633, editable=False),
        ),
    ]
