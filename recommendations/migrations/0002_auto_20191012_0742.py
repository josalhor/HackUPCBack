# Generated by Django 2.2.6 on 2019-10-12 07:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recommendations', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RealEstate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField()),
            ],
        ),
        migrations.AddField(
            model_name='preference',
            name='is_mandatory',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='session',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending to be processed'), ('in progress', 'The session is being processed'), ('completed', 'The session has been processed')], default='pending', max_length=20),
        ),
        migrations.AddField(
            model_name='session',
            name='recommendations',
            field=models.ManyToManyField(to='recommendations.RealEstate'),
        ),
    ]
