from datetime import datetime, timedelta

from django.utils import timezone

from accounts.models import DailyRoutine
from tasks.models import ScheduleBlock, Task


def _as_aware_datetime(date_value, time_value):
    combined = datetime.combine(date_value, time_value)
    if timezone.is_naive(combined):
        return timezone.make_aware(combined, timezone.get_current_timezone())
    return combined


def build_daily_schedule_for_user(user, target_date=None):
    if target_date is None:
        target_date = timezone.localdate()

    routine, _ = DailyRoutine.objects.get_or_create(user=user)
    ScheduleBlock.objects.filter(user=user, start__date=target_date).delete()

    tasks = Task.objects.filter(user=user).exclude(status='Completed').order_by('deadline', '-priority')
    work_start = _as_aware_datetime(target_date, routine.work_start_time)
    work_end = _as_aware_datetime(target_date, routine.work_end_time)

    current = work_start
    for task in tasks:
        preferred_start = task.preferred_start_time or (task.start_time.time() if task.start_time else None)
        if preferred_start:
            start_dt = _as_aware_datetime(target_date, preferred_start)
        else:
            start_dt = current

        if start_dt < work_start:
            start_dt = work_start
        if start_dt + timedelta(minutes=task.estimated_duration_minutes) > work_end:
            start_dt = max(work_start, work_end - timedelta(minutes=max(task.estimated_duration_minutes, 30)))

        end_dt = start_dt + timedelta(minutes=task.estimated_duration_minutes)
        ScheduleBlock.objects.create(
            user=user,
            task=task,
            title=task.title,
            start=start_dt,
            end=end_dt,
            category=task.category,
            description=task.description,
            status=task.status,
        )
        current = end_dt

    if tasks.exists():
        break_minutes = routine.preferred_break_duration or 15
        if len(tasks) > 1:
            longest = max((task.estimated_duration_minutes for task in tasks), default=60)
            break_slot = min(break_minutes, max(10, longest // 5))
            break_start = current if current < work_end else work_start
            break_end = break_start + timedelta(minutes=break_slot)
            ScheduleBlock.objects.create(
                user=user,
                title='Break',
                start=break_start,
                end=break_end,
                is_break=True,
                description='Scheduled break',
                status='Not Started',
            )

    return ScheduleBlock.objects.filter(user=user, start__date=target_date).order_by('start')


def get_current_task(user, now=None):
    if now is None:
        now = timezone.now()
    return ScheduleBlock.objects.filter(user=user, start__lte=now, end__gt=now).order_by('start').first()


def get_next_task(user, now=None):
    if now is None:
        now = timezone.now()
    return ScheduleBlock.objects.filter(user=user, start__gt=now).order_by('start').first()


def calculate_daily_progress(user, target_date=None):
    if target_date is None:
        target_date = timezone.localdate()
    tasks = Task.objects.filter(user=user, created_at__date=target_date)
    completed = tasks.filter(status='Completed').count()
    total = tasks.count() or 1
    percent = int((completed / total) * 100) if total else 0
    return {'total': total, 'done': completed, 'remaining': max(total - completed, 0), 'percent': percent}


def handle_overdue_tasks(user):
    overdue = Task.objects.filter(user=user).exclude(status='Completed').filter(deadline__lt=timezone.now())
    for task in overdue:
        task.status = 'Overdue'
        task.save(update_fields=['status'])
    return overdue.count()


def find_available_slot(user, start_dt, duration_minutes):
    occupied = ScheduleBlock.objects.filter(user=user, start__lt=start_dt + timedelta(minutes=duration_minutes), end__gt=start_dt)
    if not occupied.exists():
        return start_dt
    return None


def get_today_summary(user):
    today = timezone.localdate()
    tasks = Task.objects.filter(user=user)
    todays = tasks.filter(created_at__date=today)
    return {
        'total_tasks': todays.count(),
        'completed': todays.filter(status='Completed').count(),
        'remaining': todays.exclude(status='Completed').count(),
        'overdue': tasks.filter(status='Overdue').count(),
    }
