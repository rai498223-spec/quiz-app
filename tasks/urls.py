from django.urls import path

from . import views

urlpatterns = [
    path('', views.task_list, name='task_list'),
    path('add/', views.task_create, name='task_create'),
    path('generate-schedule/', views.generate_daily_schedule, name='generate_schedule'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('overview/', views.overview_view, name='overview'),
    path('what-now/', views.what_should_i_do_now, name='what_now'),
    path('<int:pk>/', views.task_detail, name='task_detail'),
    path('<int:pk>/edit/', views.task_update, name='task_update'),
    path('<int:pk>/delete/', views.task_delete, name='task_delete'),
]