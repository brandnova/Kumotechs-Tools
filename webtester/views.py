from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
import threading
import json

from .models import LoadTest, TestResult
from .forms import LoadTestForm
from .utils import LoadTester

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
    
    context = {
        'test': test,
        'results': results,
    }
    return render(request, 'webtester/test_detail.html', context)

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

