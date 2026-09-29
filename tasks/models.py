from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=20, default='#1D4533')

    class Meta:
        unique_together = ('user', 'name')

    def __str__(self):
        return self.name


class Task(models.Model):
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('Urgent', 'Urgent'),
    ]
    STATUS_CHOICES = [
        ('Not Started', 'Not Started'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Skipped', 'Skipped'),
        ('Overdue', 'Overdue'),
    ]
    RECURRING_CHOICES = [
        ('None', 'None'),
        ('Daily', 'Daily'),
        ('Weekly', 'Weekly'),
        ('Weekdays', 'Weekdays'),
        ('Weekends', 'Weekends'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Not Started')
    estimated_duration_minutes = models.PositiveIntegerField(default=60)
    deadline = models.DateTimeField(null=True, blank=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    preferred_start_time = models.TimeField(null=True, blank=True)
    preferred_end_time = models.TimeField(null=True, blank=True)
    recurring = models.CharField(max_length=20, choices=RECURRING_CHOICES, default='None')
    notes = models.TextField(blank=True)
    color = models.CharField(max_length=20, default='#1D4533')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['deadline', 'priority', 'created_at']

    def __str__(self):
        return self.title

    @property
    def duration_display(self):
        total = self.estimated_duration_minutes
        hours, minutes = divmod(total, 60)
        if hours and minutes:
            return f'{hours}h {minutes}m'
        if hours:
            return f'{hours}h'
        return f'{minutes}m'

    @property
    def is_overdue(self):
        return self.status != 'Completed' and self.deadline and self.deadline < timezone.now()


class ScheduleBlock(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='schedule_blocks')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='schedule_blocks', null=True, blank=True)
    title = models.CharField(max_length=200)
    start = models.DateTimeField()
    end = models.DateTimeField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    is_break = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Task.STATUS_CHOICES, default='Not Started')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['start']

    def __str__(self):
        return f'{self.title} ({self.start.strftime("%H:%M")})'


class RecurringTask(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recurring_tasks')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='recurrence_rules')
    pattern = models.CharField(max_length=30, default='Weekly')
    custom_days = models.CharField(max_length=100, blank=True, default='')
    next_run = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.task.title} ({self.pattern})'


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    seen = models.BooleanField(default=False)

    def __str__(self):
        return self.title

