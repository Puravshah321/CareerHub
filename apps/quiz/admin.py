from django.contrib import admin
from .models import Topic, Question, QuizAttempt, GlobalRanking , Category

admin.site.register(Topic)
admin.site.register(Question)
admin.site.register(QuizAttempt)
admin.site.register(GlobalRanking)
admin.site.register(Category)
