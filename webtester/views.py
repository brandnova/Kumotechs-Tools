from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.forms import inlineformset_factory
from .models import LoadTest, TestResult, UserJourney, JourneyStep, TestTemplate
from .forms import LoadTestForm, UserJourneyForm, JourneyStepForm
from .utils import LoadTester
import threading
import json


@login_required
def dashboard(request):
    """Dashboard view for the web tester"""
    tests = LoadTest.objects.filter(created_by=request.user).order_by('-created_at')
    
    # Get running tests
    running_tests = tests.filter(status='running')
    
    # Get recent tests (completed or failed)
    recent_tests = tests.filter(status__in=['completed', 'failed'])[:10]
    
    context = {
        'tests': tests,
        'running_tests': running_tests,
        'recent_tests': recent_tests,
    }
    return render(request, 'webtester/dashboard.html', context)

@login_required
def create_test(request):
    """Create a new load test"""
    if request.method == 'POST':
        form = LoadTestForm(request.POST)
        if form.is_valid():
            test = form.save(commit=False)
            test.created_by = request.user
            test.save()
            
            messages.success(request, f"Test '{test.name}' created successfully!")
            return redirect('webtester:detail', pk=test.pk)
    else:
        form = LoadTestForm()
    
    context = {
        'form': form,
        'title': 'Create Load Test'
    }
    return render(request, 'webtester/test_form.html', context)

@login_required
def edit_test(request, pk):
    """Edit an existing load test"""
    test = get_object_or_404(LoadTest, pk=pk, created_by=request.user)
    
    if test.status == 'running':
        messages.error(request, "Cannot edit a running test!")
        return redirect('webtester:detail', pk=test.pk)
    
    if request.method == 'POST':
        form = LoadTestForm(request.POST, instance=test)
        if form.is_valid():
            form.save()
            messages.success(request, f"Test '{test.name}' updated successfully!")
            return redirect('webtester:detail', pk=test.pk)
    else:
        form = LoadTestForm(instance=test)
    
    context = {
        'form': form,
        'test': test,
        'title': 'Edit Load Test'
    }
    return render(request, 'webtester/test_form.html', context)

@login_required
def test_detail(request, pk):
    """View details of a load test"""
    test = get_object_or_404(LoadTest, pk=pk, created_by=request.user)
    
    # Get test results
    results = test.results.all()
    
    # Get users data
    users_data = test.get_users_data_dict()
    
    context = {
        'test': test,
        'results': results,
        'users_data': users_data,
    }
    return render(request, 'webtester/test_detail.html', context)

@login_required
def journey_list(request):
    """List all user journeys"""
    journeys = UserJourney.objects.filter(created_by=request.user).order_by('-created_at')
    
    context = {
        'journeys': journeys,
    }
    return render(request, 'webtester/journey_list.html', context)

@login_required
def journey_detail(request, pk):
    """View details of a user journey"""
    journey = get_object_or_404(UserJourney, pk=pk, created_by=request.user)
    steps = journey.steps.all().order_by('order')
    
    context = {
        'journey': journey,
        'steps': steps,
    }
    return render(request, 'webtester/journey_detail.html', context)

@login_required
def create_journey(request):
    """Create a new user journey"""
    if request.method == 'POST':
        form = UserJourneyForm(request.POST)
        if form.is_valid():
            journey = form.save(commit=False)
            journey.created_by = request.user
            journey.save()
            
            messages.success(request, f"Journey '{journey.name}' created successfully!")
            return redirect('webtester:journey_detail', pk=journey.pk)
    else:
        form = UserJourneyForm()
    
    context = {
        'form': form,
        'title': 'Create User Journey'
    }
    return render(request, 'webtester/journey_form.html', context)

@login_required
def edit_journey(request, pk):
    """Edit an existing user journey"""
    journey = get_object_or_404(UserJourney, pk=pk, created_by=request.user)
    
    if request.method == 'POST':
        form = UserJourneyForm(request.POST, instance=journey)
        if form.is_valid():
            form.save()
            messages.success(request, f"Journey '{journey.name}' updated successfully!")
            return redirect('webtester:journey_detail', pk=journey.pk)
    else:
        form = UserJourneyForm(instance=journey)
    
    context = {
        'form': form,
        'journey': journey,
        'title': 'Edit User Journey'
    }
    return render(request, 'webtester/journey_form.html', context)

@login_required
def delete_journey(request, pk):
    """Delete a user journey"""
    journey = get_object_or_404(UserJourney, pk=pk, created_by=request.user)
    
    if request.method == 'POST':
        journey_name = journey.name
        journey.delete()
        messages.success(request, f"Journey '{journey_name}' deleted successfully!")
        return redirect('webtester:journey_list')
    
    return redirect('webtester:journey_detail', pk=pk)

@login_required
def add_journey_step(request, journey_pk):
    """Add a step to a user journey"""
    journey = get_object_or_404(UserJourney, pk=journey_pk, created_by=request.user)
    
    # Get the next order number
    next_order = 1
    if journey.steps.exists():
        next_order = journey.steps.order_by('-order').first().order + 1
    
    if request.method == 'POST':
        form = JourneyStepForm(request.POST)
        if form.is_valid():
            step = form.save(commit=False)
            step.journey = journey
            step.save()
            
            messages.success(request, f"Step added to journey '{journey.name}' successfully!")
            return redirect('webtester:journey_detail', pk=journey.pk)
    else:
        form = JourneyStepForm(initial={'order': next_order})
    
    context = {
        'form': form,
        'journey': journey,
        'title': f'Add Step to {journey.name}'
    }
    return render(request, 'webtester/journey_step_form.html', context)

@login_required
def edit_journey_step(request, journey_pk, step_pk):
    """Edit a journey step"""
    journey = get_object_or_404(UserJourney, pk=journey_pk, created_by=request.user)
    step = get_object_or_404(JourneyStep, pk=step_pk, journey=journey)
    
    if request.method == 'POST':
        form = JourneyStepForm(request.POST, instance=step)
        if form.is_valid():
            form.save()
            messages.success(request, f"Step updated successfully!")
            return redirect('webtester:journey_detail', pk=journey.pk)
    else:
        form = JourneyStepForm(instance=step)
    
    context = {
        'form': form,
        'journey': journey,
        'step': step,
        'title': f'Edit Step {step.order}'
    }
    return render(request, 'webtester/journey_step_form.html', context)

@login_required
def delete_journey_step(request, journey_pk, step_pk):
    """Delete a journey step"""
    journey = get_object_or_404(UserJourney, pk=journey_pk, created_by=request.user)
    step = get_object_or_404(JourneyStep, pk=step_pk, journey=journey)
    
    if request.method == 'POST':
        step.delete()
        
        # Reorder remaining steps
        for i, s in enumerate(journey.steps.all().order_by('order')):
            s.order = i + 1
            s.save()
        
        messages.success(request, f"Step deleted successfully!")
        return redirect('webtester:journey_detail', pk=journey.pk)
    
    return redirect('webtester:journey_detail', pk=journey.pk)


@login_required
def run_test(request, pk):
    """Run a load test"""
    test = get_object_or_404(LoadTest, pk=pk, created_by=request.user)
    
    if test.status == 'running':
        messages.error(request, "Test is already running!")
        return redirect('webtester:detail', pk=test.pk)
    
    # Run the test in a background thread
    def run_test_thread():
        tester = LoadTester(test)
        tester.run_test()
    
    thread = threading.Thread(target=run_test_thread)
    thread.daemon = True
    thread.start()
    
    messages.success(request, f"Test '{test.name}' started!")
    return redirect('webtester:detail', pk=test.pk)

@login_required
def delete_test(request, pk):
    """Delete a load test"""
    test = get_object_or_404(LoadTest, pk=pk, created_by=request.user)
    
    if request.method == 'POST':
        test_name = test.name
        test.delete()
        messages.success(request, f"Test '{test_name}' deleted successfully!")
        return redirect('webtester:dashboard')
    
    return redirect('webtester:detail', pk=pk)

@login_required
def test_status(request, pk):
    """Get the current status of a test (for AJAX polling)"""
    test = get_object_or_404(LoadTest, pk=pk, created_by=request.user)
    
    data = {
        'status': test.status,
        'total_requests': test.total_requests,
        'successful_requests': test.successful_requests,
        'failed_requests': test.failed_requests,
        'avg_response_time': test.avg_response_time,
        'requests_per_second': test.requests_per_second,
    }
    
    return JsonResponse(data)

@login_required
def clone_test(request, pk):
    """Clone an existing test"""
    original_test = get_object_or_404(LoadTest, pk=pk, created_by=request.user)
    
    # Create a new test with the same configuration
    new_test = LoadTest.objects.create(
        name=f"Copy of {original_test.name}",
        target_url=original_test.target_url,
        num_users=original_test.num_users,
        spawn_rate=original_test.spawn_rate,
        duration=original_test.duration,
        http_method=original_test.http_method,
        headers=original_test.headers,
        body=original_test.body,
        created_by=request.user
    )
    
    messages.success(request, f"Test '{original_test.name}' cloned successfully!")
    return redirect('webtester:detail', pk=new_test.pk)


@login_required
def template_list(request):
    """List all test templates"""
    templates = TestTemplate.objects.all().order_by('name')
    
    context = {
        'templates': templates,
    }
    return render(request, 'webtester/template_list.html', context)

@login_required
def clone_template(request, pk):
    """Clone a template to create a new test"""
    template = get_object_or_404(TestTemplate, pk=pk)
    
    # Clone the template for the current user
    test = template.clone_for_user(request.user)
    
    messages.success(request, f"Test '{test.name}' created from template successfully!")
    
    # Redirect to edit the new test
    return redirect('webtester:edit', pk=test.pk)