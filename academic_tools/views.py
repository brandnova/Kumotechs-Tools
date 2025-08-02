# academic_tools/views.py
import json
import uuid
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum
from .models import AcademicLevel, Semester, Course, StudentGrade, GPACalculation, CGPACalculation

def gpa_calculator(request):
    levels = AcademicLevel.objects.all()
    semesters = Semester.objects.all()
    return render(request, 'academic_tools/gpa_calculator.html', {
        'levels': levels,
        'semesters': semesters,
    })

def get_courses(request):
    level_id = request.GET.get('level')
    semester_id = request.GET.get('semester')
    
    if not level_id or not semester_id:
        return JsonResponse({'error': 'Both level and semester are required'}, status=400)
    
    courses = Course.objects.filter(level_id=level_id, semester_id=semester_id)
    
    course_list = [
        {
            'id': course.id,
            'code': course.code,
            'title': course.title,
            'credit_units': course.credit_units,
        }
        for course in courses
    ]
    
    return JsonResponse({'courses': course_list})

@csrf_exempt
def calculate_gpa(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    data = json.loads(request.body)
    level_id = data.get('level')
    semester_id = data.get('semester')
    courses_data = data.get('courses', [])
    
    if not courses_data:
        return JsonResponse({'error': 'No courses provided'}, status=400)
    
    total_cu = sum(course.get('credit_units', 0) for course in courses_data)
    total_cp = sum(course.get('credit_points', 0) for course in courses_data)
    
    if total_cu > 0:
        gpa = round(total_cp / total_cu, 2)
    else:
        gpa = 0
        
    # Store calculation result
    user = request.user if request.user.is_authenticated else None
    session_id = request.session.get('anonymous_id')
    if not session_id and not user:
        session_id = str(uuid.uuid4())
        request.session['anonymous_id'] = session_id
    
    GPACalculation.objects.create(
        user=user,
        session_id=session_id if not user else None,
        level_id=level_id,
        semester_id=semester_id,
        gpa=gpa,
        total_credit_units=total_cu,
        total_credit_points=total_cp
    )
    
    return JsonResponse({
        'gpa': gpa,
        'total_credit_units': total_cu,
        'total_credit_points': total_cp
    })

@csrf_exempt
def calculate_cgpa(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    data = json.loads(request.body)
    semesters_data = data.get('semesters', [])
    
    if not semesters_data:
        return JsonResponse({'error': 'No semester data provided'}, status=400)
    
    total_cu = sum(semester.get('total_credit_units', 0) for semester in semesters_data)
    total_cp = sum(semester.get('total_credit_points', 0) for semester in semesters_data)
    
    if total_cu > 0:
        cgpa = round(total_cp / total_cu, 2)
    else:
        cgpa = 0
    
    # Store calculation result
    user = request.user if request.user.is_authenticated else None
    session_id = request.session.get('anonymous_id')
    if not session_id and not user:
        session_id = str(uuid.uuid4())
        request.session['anonymous_id'] = session_id
    
    CGPACalculation.objects.create(
        user=user,
        session_id=session_id if not user else None,
        cgpa=cgpa,
        total_credit_units=total_cu,
        total_credit_points=total_cp
    )
    
    return JsonResponse({
        'cgpa': cgpa,
        'total_credit_units': total_cu,
        'total_credit_points': total_cp
    })