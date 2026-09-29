from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import DailyRoutine, UserPreference, UserProfile
from tasks.models import Category, Task
from tasks.services.scheduler import build_daily_schedule_for_user

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed the admin user with realistic demo tasks and a smart daily timetable.'

    def handle(self, *args, **options):
        user, _ = User.objects.get_or_create(username='admin', defaults={'email': 'admin@example.com'})
        if not user.check_password('admin123'):
            user.set_password('admin123')
            user.save()

        UserProfile.objects.get_or_create(user=user, defaults={'full_name': 'Admin User'})
        DailyRoutine.objects.get_or_create(user=user)
        UserPreference.objects.get_or_create(user=user)

        default_categories = ['Study', 'Work', 'Personal', 'Exercise', 'Health', 'Family', 'Projects', 'Chores', 'Break', 'Other']
        for name in default_categories:
            Category.objects.get_or_create(user=user, name=name)

        today = timezone.localdate()
        now = timezone.now()

        task_defs = [
            {
                'title': 'Morning Exercise',
                'description': 'Light cardio and mobility routine.',
                'category': 'Exercise',
                'priority': 'High',
                'estimated_duration_minutes': 30,
                'deadline': datetime.combine(today, datetime.min.time()).replace(hour=8, minute=30),
                'preferred_start_time': '07:30',
                'status': 'Not Started',
            },
            {
                'title': 'Breakfast and Planning',
                'description': 'Quick breakfast and set up the day.',
                'category': 'Personal',
                'priority': 'Medium',
                'estimated_duration_minutes': 45,
                'deadline': datetime.combine(today, datetime.min.time()).replace(hour=9, minute=15),
                'preferred_start_time': '08:15',
                'status': 'Not Started',
            },
            {
                'title': 'Deep Work Session',
                'description': 'Focus on the most important project work.',
                'category': 'Study',
                'priority': 'Urgent',
                'estimated_duration_minutes': 90,
                'deadline': datetime.combine(today, datetime.min.time()).replace(hour=11, minute=0),
                'preferred_start_time': '09:30',
                'status': 'In Progress',
            },
            {
                'title': 'Project Review',
                'description': 'Check deliverables and plan next steps.',
                'category': 'Projects',
                'priority': 'High',
                'estimated_duration_minutes': 60,
                'deadline': datetime.combine(today, datetime.min.time()).replace(hour=14, minute=0),
                'preferred_start_time': '14:00',
                'status': 'Not Started',
            },
            {
                'title': 'Reading and Reflection',
                'description': 'Read for 30 minutes and summarize key lessons.',
                'category': 'Work',
                'priority': 'Medium',
                'estimated_duration_minutes': 45,
                'deadline': datetime.combine(today, datetime.min.time()).replace(hour=20, minute=30),
                'preferred_start_time': '20:00',
                'status': 'Not Started',
            },
        ]

        for item in task_defs:
            category = Category.objects.filter(user=user, name=item['category']).first()
            task, created = Task.objects.get_or_create(
                user=user,
                title=item['title'],
                defaults={
                    'description': item['description'],
                    'category': category,
                    'priority': item['priority'],
                    'estimated_duration_minutes': item['estimated_duration_minutes'],
                    'deadline': timezone.make_aware(item['deadline'], timezone.get_current_timezone()) if item['deadline'] else None,
                    'preferred_start_time': datetime.strptime(item['preferred_start_time'], '%H:%M').time() if item['preferred_start_time'] else None,
                    'status': item['status'],
                    'color': '#1D4533',
                    'start_time': timezone.make_aware(item['deadline'] - timedelta(minutes=item['estimated_duration_minutes']), timezone.get_current_timezone()) if item['deadline'] else now,
                },
            )
            if not created:
                task.description = item['description']
                task.category = category
                task.priority = item['priority']
                task.estimated_duration_minutes = item['estimated_duration_minutes']
                task.deadline = timezone.make_aware(item['deadline'], timezone.get_current_timezone()) if item['deadline'] else None
                task.preferred_start_time = datetime.strptime(item['preferred_start_time'], '%H:%M').time() if item['preferred_start_time'] else None
                task.status = item['status']
                task.save()

        build_daily_schedule_for_user(user, today)
        self.stdout.write(self.style.SUCCESS('Demo data has been added for the admin user.'))
