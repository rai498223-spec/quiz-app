from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=120, blank=True)
    preferred_language = models.CharField(max_length=30, default='English')
    time_format = models.CharField(max_length=10, choices=[('12h', '12-hour'), ('24h', '24-hour')], default='12h')
    timezone = models.CharField(max_length=80, default='UTC')
    onboarding_complete = models.BooleanField(default=False)

    def __str__(self):
        return self.full_name or self.user.username


class DailyRoutine(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='daily_routine')
    wake_up_time = models.TimeField(default='07:00:00')
    sleep_time = models.TimeField(default='22:30:00')
    work_start_time = models.TimeField(default='09:00:00')
    work_end_time = models.TimeField(default='17:00:00')
    preferred_break_duration = models.PositiveIntegerField(default=15)
    preferred_session_length = models.PositiveIntegerField(default=50)
    productivity_preference = models.CharField(max_length=20, choices=[('morning', 'Morning'), ('afternoon', 'Afternoon'), ('evening', 'Evening')], default='morning')
    work_style = models.CharField(max_length=20, choices=[('short', 'Short'), ('long', 'Long')], default='short')
    breaks_per_day = models.PositiveIntegerField(default=3)
    auto_schedule = models.BooleanField(default=True)
    reminders_enabled = models.BooleanField(default=True)

    def __str__(self):
        return f"Routine for {self.user.username}"


class UserPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    notify_at_start = models.BooleanField(default=True)
    notify_5_minutes_before = models.BooleanField(default=True)
    notify_10_minutes_before = models.BooleanField(default=False)
    notify_15_minutes_before = models.BooleanField(default=False)
    custom_notice_minutes = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Preferences for {self.user.username}"
