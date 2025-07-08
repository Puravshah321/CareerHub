from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

class Topic(models.Model):
    DIFFICULTY_LEVELS = [
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
    ]

    CATEGORY_CHOICES = [
        ('Technical', 'Technical'),
        ('Business', 'Business'),
        ('Management', 'Management'),
        ('Law', 'Law'),
        ('Aptitude', 'Aptitude'),
        ('Logical', 'Logical'),
        ('Web Development', 'Web Development'),
        ('Communication', 'Communication'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, help_text="Short description about the topic.")
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_LEVELS, default='Medium')
    time_limit = models.PositiveIntegerField(help_text="Time duration in minutes", default=10)
    total_questions = models.PositiveIntegerField(default=10)
    image = models.ImageField(upload_to='topics/', null=True, blank=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return self.name


class Category(models.Model):
    
    CATEGORY_CHOICES = [
        ('Programming', 'Programming'),
        ('Business & Management', 'Business & Management'),
        ('Web Development', 'Web Development'),
        ('Database Management', 'Database Management'),
        ('Technical', 'Technical'),
        ('Law', 'Law'),
        ('General Test', 'General Test'),
        ('Other Specialized Area', 'Other Specialized Area'),
    ]
    
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='')

    def __str__(self):
        return self.category


class Question(models.Model):
    DIFFICULTY_LEVELS = [
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
    ]

    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    question_text = models.TextField()
    option1 = models.CharField(max_length=200)
    option2 = models.CharField(max_length=200)
    option3 = models.CharField(max_length=200)
    option4 = models.CharField(max_length=200)
    correct_option = models.IntegerField()  # 1 to 4
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_LEVELS, default='Medium')

    def save(self, *args, **kwargs):
        # Automatically inherit difficulty from topic
        if self.topic and self.difficulty != self.topic.difficulty:
            self.difficulty = self.topic.difficulty
        super().save(*args, **kwargs)

    def __str__(self):
        return self.question_text


from django.utils import timezone
from datetime import timedelta

class QuizAttempt(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    score = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)

    def get_duration(self):
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            # Return duration in "X min Y sec" format
            minutes, seconds = divmod(duration.total_seconds(), 60)
            return f"{int(minutes)} min {int(seconds)} sec"
        return "N/a"

    def __str__(self):
        return f"{self.user.username} - {self.topic.name} - {self.score} pts"



class GlobalRanking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_score = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.user.username} - {self.total_score}'
