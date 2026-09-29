from django.contrib.auth.models import User

from tasks.models import Notification


def add_notification(user: User, title: str, message: str):
    return Notification.objects.create(user=user, title=title, message=message)


def unread_notifications(user):
    return Notification.objects.filter(user=user, seen=False).order_by('-created_at')
