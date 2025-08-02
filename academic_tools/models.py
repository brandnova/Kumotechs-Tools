# academic_tools/models.py
from django.db import models
from django.contrib.auth.models import User

class AcademicLevel(models.Model):
    name = models.CharField(max_length=50)  # e.g., "100 Level", "200 Level"
    
    def __str__(self):
        return self.name

class Semester(models.Model):
    name = models.CharField(max_length=50)  # e.g., "First Semester", "Second Semester"
    
    def __str__(self):
        return self.name

class Course(models.Model):
    code = models.CharField(max_length=20)  # e.g., "CSC101"
    title = models.CharField(max_length=255)
    credit_units = models.IntegerField()
    level = models.ForeignKey(AcademicLevel, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.code} - {self.title}"

class StudentGrade(models.Model):
    GRADE_CHOICES = [
        ('A', 'A (70-100%)'),
        ('B', 'B (60-69%)'),
        ('C', 'C (50-59%)'),
        ('D', 'D (45-49%)'),
        ('E', 'E (40-44%)'),
        ('F', 'F (0-39%)'),
    ]
    
    GRADE_POINTS = {
        'A': 5.00,
        'B': 4.00,
        'C': 3.00,
        'D': 2.00,
        'E': 1.00,
        'F': 0.00,
    }
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=100, null=True, blank=True)  # For anonymous users
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    grade = models.CharField(max_length=1, choices=GRADE_CHOICES)
    
    @property
    def grade_point(self):
        return self.GRADE_POINTS.get(self.grade, 0)
    
    @property
    def credit_points(self):
        return self.grade_point * self.course.credit_units
    
    def __str__(self):
        user_info = self.user.username if self.user else f"Anonymous ({self.session_id})"
        return f"{user_info} - {self.course.code} - {self.grade}"

class GPACalculation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=100, null=True, blank=True)  # For anonymous users
    level = models.ForeignKey(AcademicLevel, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    gpa = models.DecimalField(max_digits=4, decimal_places=2)
    total_credit_units = models.IntegerField()
    total_credit_points = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        user_info = self.user.username if self.user else f"Anonymous ({self.session_id})"
        return f"{user_info} - {self.level} {self.semester} - GPA: {self.gpa}"

class CGPACalculation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=100, null=True, blank=True)  # For anonymous users
    cgpa = models.DecimalField(max_digits=4, decimal_places=2)
    total_credit_units = models.IntegerField()
    total_credit_points = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        user_info = self.user.username if self.user else f"Anonymous ({self.session_id})"
        return f"{user_info} - CGPA: {self.cgpa}"