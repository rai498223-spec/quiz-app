from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import DailyRoutine, UserPreference, UserProfile


class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['full_name', 'preferred_language', 'time_format', 'timezone']


class DailyRoutineForm(forms.ModelForm):
    class Meta:
        model = DailyRoutine
        fields = [
            'wake_up_time', 'sleep_time', 'work_start_time', 'work_end_time',
            'preferred_break_duration', 'preferred_session_length',
            'productivity_preference', 'work_style', 'breaks_per_day',
            'auto_schedule', 'reminders_enabled'
        ]


class UserPreferenceForm(forms.ModelForm):
    class Meta:
        model = UserPreference
        fields = [
            'notify_at_start', 'notify_5_minutes_before', 'notify_10_minutes_before',
            'notify_15_minutes_before', 'custom_notice_minutes'
        ]
