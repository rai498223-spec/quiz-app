from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Category, ScheduleBlock, Task
from .services.notification_service import add_notification
from .services.scheduler import build_daily_schedule_for_user, calculate_daily_progress, get_current_task, get_next_task, handle_overdue_tasks


@login_required
def task_list(request):
    tasks = Task.objects.filter(user=request.user)
    query = request.GET.get('q', '')
    status = request.GET.get('status')
    priority = request.GET.get('priority')
    category_id = request.GET.get('category')

    if query:
        tasks = tasks.filter(Q(title__icontains=query) | Q(description__icontains=query))
    if status:
        tasks = tasks.filter(status=status)
    if priority:
        tasks = tasks.filter(priority=priority)
    if category_id:
        tasks = tasks.filter(category_id=category_id)

    sort = request.GET.get('sort', 'deadline')
    if sort == 'priority':
        tasks = tasks.order_by('-priority')
    elif sort == 'duration':
        tasks = tasks.order_by('-estimated_duration_minutes')
    elif sort == 'created':
        tasks = tasks.order_by('-created_at')
    else:
        tasks = tasks.order_by('deadline', 'priority')

    categories = Category.objects.filter(user=request.user)
    return render(request, 'tasks/task_list.html', {'tasks': tasks, 'categories': categories, 'query': query})


@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, user=request.user, pk=pk)
    return render(request, 'tasks/task_detail.html', {'task': task})


@login_required
def task_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        category_id = request.POST.get('category')
        priority = request.POST.get('priority', 'Medium')
        duration = request.POST.get('estimated_duration_minutes')
        deadline = request.POST.get('deadline')
        preferred_start = request.POST.get('preferred_start_time')
        preferred_end = request.POST.get('preferred_end_time')
        notes = request.POST.get('notes', '')
        color = request.POST.get('color', '#1D4533')

        if not title:
            messages.error(request, 'Task title is required.')
            return redirect('task_create')

        try:
            duration_int = int(duration or 60)
        except ValueError:
            messages.error(request, 'Please enter a valid duration in minutes.')
            return redirect('task_create')

        category = Category.objects.filter(user=request.user, pk=category_id).first() if category_id else None
        task = Task.objects.create(
            user=request.user,
            title=title,
            description=description,
            category=category,
            priority=priority,
            estimated_duration_minutes=duration_int,
            deadline=datetime.strptime(deadline, '%Y-%m-%dT%H:%M') if deadline else None,
            preferred_start_time=datetime.strptime(preferred_start, '%H:%M').time() if preferred_start else None,
            preferred_end_time=datetime.strptime(preferred_end, '%H:%M').time() if preferred_end else None,
            notes=notes,
            color=color,
        )
        add_notification(request.user, 'Task scheduled', f'{task.title} has been added to your plan.')
        build_daily_schedule_for_user(request.user)
        messages.success(request, 'Task created and scheduled.')
        return redirect('task_list')

    categories = Category.objects.filter(user=request.user)
    return render(request, 'tasks/task_form.html', {'categories': categories, 'editing': False})


@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, user=request.user, pk=pk)
    if request.method == 'POST':
        task.title = request.POST.get('title', task.title)
        task.description = request.POST.get('description', task.description)
        category_id = request.POST.get('category')
        if category_id:
            task.category = Category.objects.filter(user=request.user, pk=category_id).first()
        task.priority = request.POST.get('priority', task.priority)
        task.estimated_duration_minutes = int(request.POST.get('estimated_duration_minutes', task.estimated_duration_minutes))
        task.status = request.POST.get('status', task.status)
        task.deadline = datetime.strptime(request.POST.get('deadline'), '%Y-%m-%dT%H:%M') if request.POST.get('deadline') else None
        if request.POST.get('preferred_start_time'):
            task.preferred_start_time = datetime.strptime(request.POST.get('preferred_start_time'), '%H:%M').time()
        task.notes = request.POST.get('notes', task.notes)
        task.save()
        build_daily_schedule_for_user(request.user)
        messages.success(request, 'Task updated.')
        return redirect('task_detail', pk=task.pk)

    categories = Category.objects.filter(user=request.user)
    return render(request, 'tasks/task_form.html', {'task': task, 'categories': categories, 'editing': True})


@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, user=request.user, pk=pk)
    if request.method == 'POST':
        task.delete()
        messages.info(request, 'Task removed.')
        return redirect('task_list')
    return redirect('task_detail', pk=task.pk)


@login_required
def calendar_view(request):
    tasks = Task.objects.filter(user=request.user).order_by('deadline')
    return render(request, 'tasks/calendar.html', {'tasks': tasks})


@login_required
def overview_view(request):
    tasks = Task.objects.filter(user=request.user)
    total = tasks.count()
    completed = tasks.filter(status='Completed').count()
    remaining = tasks.filter(status='Not Started').count() + tasks.filter(status='In Progress').count()
    overdue = tasks.filter(status='Overdue').count()
    report = calculate_daily_progress(request.user)
    return render(request, 'tasks/overview.html', {
        'total': total,
        'completed': completed,
        'remaining': remaining,
        'overdue': overdue,
        'report': report,
    })


@login_required
def generate_daily_schedule(request):
    handle_overdue_tasks(request.user)
    build_daily_schedule_for_user(request.user)
    messages.success(request, 'Today’s timetable has been refreshed.')
    return redirect('dashboard_home')


@login_required
def what_should_i_do_now(request):
    current = get_current_task(request.user)
    next_task = get_next_task(request.user)
    if current:
        seconds_left = int((current.end - timezone.now()).total_seconds())
        recommendation = {
            'task': current.title,
            'remaining': max(seconds_left, 0),
            'next': next_task.title if next_task else 'Take a break',
        }
    else:
        recommendation = {
            'task': 'Plan your next task',
            'remaining': 0,
            'next': next_task.title if next_task else 'No upcoming tasks',
        }
    return render(request, 'tasks/what_now.html', {'recommendation': recommendation})
