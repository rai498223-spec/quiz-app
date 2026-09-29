from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone

from accounts.models import DailyRoutine, UserProfile
from tasks.models import Task
from tasks.services.scheduler import build_daily_schedule_for_user, calculate_daily_progress, get_current_task, get_next_task, handle_overdue_tasks


@login_required
def dashboard_home(request):
    handle_overdue_tasks(request.user)
    user_profile = UserProfile.objects.get_or_create(user=request.user)[0]
    DailyRoutine.objects.get_or_create(user=request.user)
    tasks = Task.objects.filter(user=request.user)
    today = timezone.localdate()
    todays_tasks = tasks.filter(created_at__date=today)
    current = get_current_task(request.user)
    next_task = get_next_task(request.user)
    progress = calculate_daily_progress(request.user)
    build_daily_schedule_for_user(request.user, today)

    greeting = 'Good morning'
    hour = timezone.now().hour
    if 12 <= hour < 18:
        greeting = 'Good afternoon'
    elif hour >= 18:
        greeting = 'Good evening'

    context = {
        'greeting': greeting,
        'profile': user_profile,
        'current_task': current,
        'next_task': next_task,
        'progress': progress,
        'tasks': todays_tasks,
        'today_date': today.strftime('%A, %B %d'),
    }
    return render(request, 'dashboard/home.html', context)
