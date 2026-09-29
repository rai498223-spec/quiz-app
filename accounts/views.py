from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render

from tasks.models import Category

from .forms import DailyRoutineForm, SignupForm, UserPreferenceForm, UserProfileForm
from .models import DailyRoutine, UserPreference, UserProfile


def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.get_or_create(user=user, defaults={'full_name': user.username})
            DailyRoutine.objects.get_or_create(user=user)
            UserPreference.objects.get_or_create(user=user)
            for name in ['Study', 'Work', 'Personal', 'Exercise', 'Health', 'Family', 'Projects', 'Chores', 'Break', 'Other']:
                Category.objects.get_or_create(user=user, name=name)
            login(request, user)
            messages.success(request, 'Your account is ready. Let’s set up your smart routine.')
            return redirect('onboarding')
    else:
        form = SignupForm()
    return render(request, 'auth/signup.html', {'form': form})


@login_required
@transaction.atomic
def onboarding_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    routine, _ = DailyRoutine.objects.get_or_create(user=request.user)
    preferences, _ = UserPreference.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, instance=profile)
        routine_form = DailyRoutineForm(request.POST, instance=routine)
        preferences_form = UserPreferenceForm(request.POST, instance=preferences)
        if profile_form.is_valid() and routine_form.is_valid() and preferences_form.is_valid():
            profile_form.save()
            routine_form.save()
            preferences_form.save()
            profile.onboarding_complete = True
            profile.save()
            messages.success(request, 'Your onboarding is complete. Your personal plan is ready.')
            return redirect('dashboard_home')
    else:
        profile_form = UserProfileForm(instance=profile)
        routine_form = DailyRoutineForm(instance=routine)
        preferences_form = UserPreferenceForm(instance=preferences)

    return render(
        request,
        'auth/onboarding.html',
        {'profile_form': profile_form, 'routine_form': routine_form, 'preferences_form': preferences_form}
    )


@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'auth/profile.html', {'profile': profile})


@login_required
def settings_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    routine, _ = DailyRoutine.objects.get_or_create(user=request.user)
    preferences, _ = UserPreference.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, instance=profile)
        routine_form = DailyRoutineForm(request.POST, instance=routine)
        preferences_form = UserPreferenceForm(request.POST, instance=preferences)
        if profile_form.is_valid() and routine_form.is_valid() and preferences_form.is_valid():
            profile_form.save()
            routine_form.save()
            preferences_form.save()
            messages.success(request, 'Your settings were updated.')
            return redirect('settings')
    else:
        profile_form = UserProfileForm(instance=profile)
        routine_form = DailyRoutineForm(instance=routine)
        preferences_form = UserPreferenceForm(instance=preferences)

    return render(request, 'auth/settings.html', {
        'profile_form': profile_form,
        'routine_form': routine_form,
        'preferences_form': preferences_form,
    })
