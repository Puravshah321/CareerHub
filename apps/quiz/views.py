from django.shortcuts import render, redirect, get_object_or_404
from .models import Topic, Question, QuizAttempt, GlobalRanking, Category
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.contrib import messages

@login_required
def topic_list(request):
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    difficulty_filter = request.GET.get('difficulty', '')

    topics = Topic.objects.all()

    if search_query:
        topics = topics.filter(name__icontains=search_query)

    if category_filter:
        topics = topics.filter(category__category__iexact=category_filter)

    if difficulty_filter:
        topics = topics.filter(difficulty__iexact=difficulty_filter)

    categories = Category.objects.all()

    return render(request, 'quiz/topics_list.html', {
        'topics': topics,
        'categories': categories,
        'selected_category': category_filter,
        'selected_difficulty': difficulty_filter,
        'search_query': search_query,
    })

from django.utils.timezone import now

@login_required
def start_quiz(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)

    if QuizAttempt.objects.filter(user=request.user, topic=topic).exists():
        messages.warning(request, f"You have already given this {topic.name} test.")
        return redirect('quiz:topics')

    questions = Question.objects.filter(topic=topic)

    # Save start time in session
    request.session['quiz_start_time'] = now().isoformat()

    return render(request, 'quiz/start_quiz.html', {'topic': topic, 'questions': questions})


from datetime import datetime
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware
from django.utils import timezone

@login_required
def submit_quiz(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)

    if QuizAttempt.objects.filter(user=request.user, topic=topic).exists():
        messages.info(request, "You have already taken this quiz.")
        return redirect('quiz:topics')

    questions = Question.objects.filter(topic=topic)
    score = 0
    bonus = 0

    for q in questions:
        selected = request.POST.get(str(q.id))
        if selected and int(selected) == q.correct_option:
            score += 1
            if q.difficulty == 'Medium':
                bonus += 1
            elif q.difficulty == 'Hard':
                bonus += 2

    total_score_with_bonus = score + bonus

    # Get time values
    start_time_str = request.session.pop('quiz_start_time', None)
    start_time = parse_datetime(start_time_str) if start_time_str else None
    if start_time and start_time.tzinfo is None:
        start_time = make_aware(start_time)
    end_time = timezone.now()

    QuizAttempt.objects.create(
        user=request.user,
        topic=topic,
        score=total_score_with_bonus,
        start_time=start_time,
        end_time=end_time
    )

    total_score = QuizAttempt.objects.filter(user=request.user).aggregate(Sum('score'))['score__sum'] or 0
    rank_obj, _ = GlobalRanking.objects.get_or_create(user=request.user)
    rank_obj.total_score = total_score
    rank_obj.save()

    return redirect('quiz:ranking')


from collections import defaultdict
from django.utils.timezone import localtime

@login_required
def global_ranking(request):
    rankings = GlobalRanking.objects.order_by('-total_score')
    
    # Group user's quiz attempts by topic
    user_attempts = QuizAttempt.objects.filter(user=request.user).select_related('topic')
    
    user_scores_by_subject = defaultdict(list)
    for attempt in user_attempts:
        user_scores_by_subject[attempt.topic.name].append({
            'test_name': attempt.topic.name,
            'score': attempt.score,
            'date_taken': localtime(attempt.timestamp),
           'duration': attempt.get_duration() or "N/a"
        })

    return render(request, 'quiz/ranking.html', {
        'rankings': rankings,
        'user_scores_by_subject': dict(user_scores_by_subject),
        'user': request.user
    })


@login_required
def recommend_quizzes(request):
    # Get the job seeker user
    job_seeker = request.user.jobseeker

    # Get the user's interests (categories they are interested in)
    interested_categories = job_seeker.interests.all()

    # Filter topics that match the user's interests
    recommended_topics = Topic.objects.filter(category__in=interested_categories)

    # Render the recommendations in a template
    return render(request, 'quiz/recommended_quizzes.html', {
        'recommended_topics': recommended_topics
    })
