from django.urls import path
from . import views

app_name = 'quiz'

urlpatterns = [
    path('topics/', views.topic_list, name='topics'),
    path('start/<int:topic_id>/', views.start_quiz, name='start_quiz'),
    path('submit/<int:topic_id>/', views.submit_quiz, name='submit_quiz'),
    path('ranking/', views.global_ranking, name='ranking'),
]
