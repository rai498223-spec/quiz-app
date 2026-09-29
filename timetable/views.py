from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone

from tasks.models import ScheduleBlock


@login_required
def timetable_view(request):
    today = timezone.localdate()
    blocks = ScheduleBlock.objects.filter(user=request.user, start__date=today).order_by('start')
    return render(request, 'timetable/day.html', {'blocks': blocks, 'today': today})
