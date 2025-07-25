# Generated by Django 5.2 on 2025-04-11 09:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='topic',
            name='description',
            field=models.TextField(blank=True, help_text='Short description about the topic.'),
        ),
        migrations.AddField(
            model_name='topic',
            name='difficulty',
            field=models.CharField(choices=[('Easy', 'Easy'), ('Medium', 'Medium'), ('Hard', 'Hard')], default='Medium', max_length=10),
        ),
        migrations.AddField(
            model_name='topic',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='topic_images/'),
        ),
        migrations.AddField(
            model_name='topic',
            name='time_limit',
            field=models.PositiveIntegerField(default=10, help_text='Time duration in minutes'),
        ),
        migrations.AddField(
            model_name='topic',
            name='total_questions',
            field=models.PositiveIntegerField(default=10),
        ),
    ]
