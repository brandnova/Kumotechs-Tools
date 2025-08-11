from django.shortcuts import render

# Create your views here.

def notes_view(request):
    """
    View for the Task Manager SPA page
    """
    context = {
        'page_title': 'Task Manager',
        'page_description': 'Manage your tasks with a simple workflow'
    }
    return render(request, 'notes/notes.html', context)

def uuid_view(request):
    """
    View for the UUID Generator page
    """
    context = {
        'page_title': 'UUID Generator',
        'page_description': 'Generate unique identifiers for your projects'
    }
    return render(request, 'uuid/uuid.html', context)

def json_formatter(request):
    """
    View for the JSON Formatter page
    """
    context = {
        'page_title': 'JSON Formatter',
        'page_description': 'Format and validate your JSON data easily'
    }
    return render(request, 'json/json.html', context)