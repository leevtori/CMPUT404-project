# Generated by Django 2.1.7 on 2019-03-17 21:54

from django.db import migrations, models
import posts.utils


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_auto_20190308_2055'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='visibility',
            field=models.CharField(choices=[('PUBL', 'Public'), ('FOAF', 'Friend of a Friend'), ('PRIV', 'Private'), ('SERV', 'Home Server Only'), ('FRND', 'Friends Only')], default=posts.utils.Visibility('PUBL'), max_length=4),
        ),
    ]
