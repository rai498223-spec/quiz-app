from django.contrib import admin

from .models import Category, Notification, RecurringTask, ScheduleBlock, Task


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'color')
    search_fields = ('name', 'user__username')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'priority', 'status', 'estimated_duration_minutes', 'deadline')
    list_filter = ('status', 'priority', 'category')
    search_fields = ('title', 'user__username')


@admin.register(ScheduleBlock)
class ScheduleBlockAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'start', 'end', 'status')
    list_filter = ('status', 'is_break')
    search_fields = ('title', 'user__username')


@admin.register(RecurringTask)
class RecurringTaskAdmin(admin.ModelAdmin):
    list_display = ('task', 'pattern', 'next_run')
    search_fields = ('task__title',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'seen', 'created_at')
    list_filter = ('seen',)
    search_fields = ('title', 'user__username')
