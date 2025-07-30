from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.forms import inlineformset_factory
from django.db.models import Q
from .models import LoadTest, TestResult, UserJourney, JourneyStep, TestTemplate
from .forms import LoadTestForm, UserJourneyForm, JourneyStepForm, PublicTemplateForm
from .utils import LoadTester
import threading
import json


@login_required
def dashboard(request):
    """Dashboard view for the web tester"""
    # Get user's tests (excluding public templates)
    tests = LoadTest.objects.filter(created_by=request.user, is_public_template=False).order_by('-created_at')
    
    # Get running tests
    running_tests = tests.filter(status='running')
    
    # Get recent tests (completed or failed)
    recent_tests = tests.filter(status__in=['completed', 'failed'])[:10]

    # Get tests assigned to the user
    assigned_tests = LoadTest.objects.filter(assignments__assigned_to=request.user).exclude(created_by=request.user).order_by('-assignments__assigned_at')
    
    # Get public templates (separate from user's tests)
    public_templates_count = LoadTest.objects.filter(is_public_template=True).count()
    
    context = {
        'tests': tests,
        'running_tests': running_tests,
        'recent_tests': recent_tests,
        'assigned_tests': assigned_tests,
        'public_templates_count': public_templates_count,
    }
    return render(request, 'webtester/dashboard.html', context)

@login_required
def create_test(request):
    """Create a new load test"""
    # Check if a journey ID was provided
    journey_id = request.GET.get('journey')
    initial_data = {}
    
    if journey_id:
        try:
            journey = UserJourney.objects.get(pk=journey_id)
            initial_data['journey'] = journey
        except UserJourney.DoesNotExist:
            pass
    
    if request.method == 'POST':
        form = LoadTestForm(request.POST)
        if form.is_valid():
            test = form.save(commit=False)
            test.created_by = request.user
            test.save()
            
            messages.success(request, f"Test '{test.name}' created successfully!")
            return redirect('webtester:detail', pk=test.pk)
        else:
            # Add this to debug form errors
            print(f"Form errors: {form.errors}")
            messages.error(request, f"Please correct the errors below.")
    else:
        form = LoadTestForm(initial=initial_data)
    
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
    """View test details"""
    # Get the test if it's created by the user OR assigned to the user
    test = get_object_or_404(
        LoadTest.objects.select_related('created_by', 'journey'),
        Q(pk=pk) & (Q(created_by=request.user) | Q(assignments__assigned_to=request.user))
    )
    
    # Get test results if available
    results = None
    if test.status == 'completed':
        results = test.results.all().order_by('timestamp')[:100]  # Limit to 100 results for performance
    
    context = {
        'test': test,
        'results': results,
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
    """View journey details"""
    # Get the journey if it's created by the user OR part of a test assigned to the user
    journey = get_object_or_404(
        UserJourney.objects.select_related('created_by'),
        Q(pk=pk) & (
            Q(created_by=request.user) | 
            Q(load_tests__assignments__assigned_to=request.user) |
            Q(load_tests_multi__assignments__assigned_to=request.user)
        )
    )
    
    # Get journey steps
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
def add_journey_to_test(request, journey_pk):
    """Add a journey to an existing test"""
    journey = get_object_or_404(
        UserJourney,
        Q(pk=journey_pk) & (
            Q(created_by=request.user) | 
            Q(load_tests__assignments__assigned_to=request.user) |
            Q(load_tests_multi__assignments__assigned_to=request.user)
        )
    )
    
    # Get tests that the user can modify
    tests = LoadTest.objects.filter(created_by=request.user, is_public_template=False)
    
    if request.method == 'POST':
        test_id = request.POST.get('test_id')
        if test_id:
            test = get_object_or_404(LoadTest, pk=test_id, created_by=request.user)
            test.journeys.add(journey)
            messages.success(request, f"Journey '{journey.name}' added to test '{test.name}'.")
            return redirect('webtester:detail', pk=test.pk)
        else:
            messages.error(request, "Please select a test.")
    
    context = {
        'journey': journey,
        'tests': tests,
    }
    return render(request, 'webtester/add_journey_to_test.html', context)

@login_required
def run_test(request, pk):
    """Run a load test"""
    # Get the test if it's created by the user OR assigned to the user
    test = get_object_or_404(
        LoadTest,
        Q(pk=pk) & (Q(created_by=request.user) | Q(assignments__assigned_to=request.user))
    )
    
    # Only the creator or an admin can run the test
    if test.created_by != request.user and not request.user.is_staff:
        messages.error(request, "You don't have permission to run this test.")
        return redirect('webtester:detail', pk=test.pk)
    
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
    # Get the test if it's created by the user OR assigned to the user
    original_test = get_object_or_404(
        LoadTest,
        Q(pk=pk) & (Q(created_by=request.user) | Q(assignments__assigned_to=request.user))
    )
    
    # Create a new test with the same configuration
    new_test = LoadTest.objects.create(
        name=f"Copy of {original_test.name}",
        target_url=original_test.target_url,
        journey=original_test.journey,  # Copy the journey reference
        journey_probability=original_test.journey_probability,
        num_users=original_test.num_users,
        spawn_rate=original_test.spawn_rate,
        duration=original_test.duration,
        http_method=original_test.http_method,
        headers=original_test.headers,
        body=original_test.body,
        created_by=request.user
    )
    
    # Copy the additional journeys
    if original_test.journeys.exists():
        new_test.journeys.set(original_test.journeys.all())
    
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
def public_templates(request):
    """List all public test templates"""
    templates = LoadTest.objects.filter(is_public_template=True).order_by('-created_at')
    
    context = {
        'templates': templates,
    }
    return render(request, 'webtester/public_templates.html', context)

@login_required
def clone_template(request, pk):
    """Clone a public template to the user's tests"""
    template = get_object_or_404(LoadTest, pk=pk, is_public_template=True)
    
    if request.method == 'POST':
        # Create a new test based on the template
        new_test = LoadTest.objects.get(pk=template.pk)
        new_test.pk = None  # This will create a new instance
        new_test.is_public_template = False
        new_test.template_name = None
        new_test.template_description = None
        new_test.created_by = request.user
        new_test.created_at = timezone.now()
        new_test.updated_at = timezone.now()
        new_test.status = 'pending'
        new_test.started_at = None
        new_test.completed_at = None
        new_test.total_requests = 0
        new_test.successful_requests = 0
        new_test.failed_requests = 0
        new_test.avg_response_time = None
        new_test.min_response_time = None
        new_test.max_response_time = None
        new_test.requests_per_second = None
        new_test.users_data = None
        
        # If the template has a journey, clone it too
        if template.journey:
            original_journey = template.journey
            new_journey = UserJourney.objects.get(pk=original_journey.pk)
            new_journey.pk = None
            new_journey.created_by = request.user
            new_journey.created_at = timezone.now()
            new_journey.updated_at = timezone.now()
            new_journey.save()
            
            # Clone all steps
            for step in original_journey.steps.all():
                new_step = JourneyStep.objects.get(pk=step.pk)
                new_step.pk = None
                new_step.journey = new_journey
                new_step.save()
            
            new_test.journey = new_journey
        
        new_test.save()
        
        messages.success(request, f"Template '{template.name}' cloned successfully as '{new_test.name}'!")
        return redirect('webtester:detail', pk=new_test.pk)
    
    context = {
        'template': template,
    }
    return render(request, 'webtester/clone_template.html', context)

@login_required
def make_public_template(request, pk):
    """Make a test a public template"""
    test = get_object_or_404(LoadTest, pk=pk, created_by=request.user)
    
    if request.method == 'POST':
        form = PublicTemplateForm(request.POST, instance=test)
        if form.is_valid():
            form.save()
            messages.success(request, f"Test '{test.name}' is now available as a public template!")
            return redirect('webtester:detail', pk=test.pk)
    else:
        form = PublicTemplateForm(instance=test)
    
    context = {
        'form': form,
        'test': test,
    }
    return render(request, 'webtester/make_public_template.html', context)