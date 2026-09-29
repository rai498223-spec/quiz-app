from django.contrib import admin

from .models import DailyRoutine, UserPreference, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'preferred_language', 'timezone', 'onboarding_complete')
    search_fields = ('user__username', 'full_name')
    list_filter = ('onboarding_complete', 'timezone')


@admin.register(DailyRoutine)
class DailyRoutineAdmin(admin.ModelAdmin):
    list_display = ('user', 'wake_up_time', 'work_start_time', 'work_end_time', 'preferred_break_duration')
    search_fields = ('user__username',)


@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'notify_at_start', 'notify_5_minutes_before', 'custom_notice_minutes')
    search_fields = ('user__username',)
