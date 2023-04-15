# Generated by Django 3.1.3 on 2021-07-01 03:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ahj_app', '0011_auto_20210623_2231'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicaluser',
            name='AcceptedEdits',
        ),
        migrations.RemoveField(
            model_name='historicaluser',
            name='CommunityScore',
        ),
        migrations.RemoveField(
            model_name='historicaluser',
            name='SubmittedEdits',
        ),
        migrations.RemoveField(
            model_name='user',
            name='AcceptedEdits',
        ),
        migrations.RemoveField(
            model_name='user',
            name='CommunityScore',
        ),
        migrations.RemoveField(
            model_name='user',
            name='SubmittedEdits',
        ),
        migrations.AddField(
            model_name='historicaluser',
            name='NumAPICalls',
            field=models.IntegerField(db_column='NumAPICalls', default=0),
        ),
        migrations.AddField(
            model_name='user',
            name='NumAPICalls',
            field=models.IntegerField(db_column='NumAPICalls', default=0),
        ),
    ]