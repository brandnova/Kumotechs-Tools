from django.core.management.base import BaseCommand
from academic_tools.models import AcademicLevel, Semester, Course

class Command(BaseCommand):
    help = 'Populates the database with academic levels, semesters, and courses'

    def handle(self, *args, **options):
        # Create academic levels (100 to 700)
        self.stdout.write('Creating academic levels...')
        levels = []
        for level in range(100, 701, 100):
            level_obj, created = AcademicLevel.objects.get_or_create(name=f"{level} Level")
            levels.append(level_obj)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created {level} Level"))
            else:
                self.stdout.write(f"{level} Level already exists")

        # Create semesters
        self.stdout.write('Creating semesters...')
        first_semester, created = Semester.objects.get_or_create(name="First Semester")
        if created:
            self.stdout.write(self.style.SUCCESS("Created First Semester"))
        else:
            self.stdout.write("First Semester already exists")
            
        second_semester, created = Semester.objects.get_or_create(name="Second Semester")
        if created:
            self.stdout.write(self.style.SUCCESS("Created Second Semester"))
        else:
            self.stdout.write("Second Semester already exists")

        # Find 500 level
        level_500 = AcademicLevel.objects.get(name="500 Level")

        # Create 500 Level First Semester courses
        self.stdout.write('Creating 500 Level First Semester courses...')
        
        courses_500_first = [
            {"code": "ENG 501", "title": "Management and Economics", "credit_units": 3},
            {"code": "EEE 501", "title": "Reliability & Maintainability of Electrical & Electronic Components & Systems", "credit_units": 2},
            {"code": "EEE 502", "title": "Advance Computer Programming & Statistics", "credit_units": 3},
            {"code": "EEE 503", "title": "Electrical Services Design", "credit_units": 2},
            {"code": "EEE 504", "title": "Electrical Power System I", "credit_units": 2},
            {"code": "EEE 505", "title": "Industrial Electronic Design", "credit_units": 2},
            {"code": "EEE 508", "title": "Project & Thesis", "credit_units": 3},
            {"code": "EEE 506", "title": "Telecommunication Engineering", "credit_units": 2},
            {"code": "EEE 507", "title": "Power Systems Communications and Control", "credit_units": 2},
            {"code": "EEE 509", "title": "Switch Gear and High Voltage Engineering", "credit_units": 2},
            {"code": "EEE 520", "title": "Communication Systems", "credit_units": 3},
            {"code": "EEE 521", "title": "Micro Computer Hardware and Software Techniques", "credit_units": 2},
            {"code": "EEE 522", "title": "Solid State Electronics", "credit_units": 2},
        ]
        
        for course_data in courses_500_first:
            course, created = Course.objects.get_or_create(
                code=course_data["code"],
                defaults={
                    "title": course_data["title"],
                    "credit_units": course_data["credit_units"],
                    "level": level_500,
                    "semester": first_semester
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created course: {course.code} - {course.title}"))
            else:
                self.stdout.write(f"Course {course.code} already exists")

        # Create 500 Level Second Semester courses
        self.stdout.write('Creating 500 Level Second Semester courses...')
        
        courses_500_second = [
            {"code": "EEE 518", "title": "Project & Thesis", "credit_units": 3},
            {"code": "EEE 512", "title": "Control Engineering", "credit_units": 3},
            {"code": "EEE 513", "title": "Advanced Circuits Techniques", "credit_units": 2},
            {"code": "EEE 514", "title": "Electrical Power Systems II", "credit_units": 3},
            {"code": "EEE 515", "title": "Power Electronics & Drives", "credit_units": 3},
            {"code": "EEE 516", "title": "Analogue & Digital Computer", "credit_units": 2},
            {"code": "EEE 517", "title": "Digital Signal Processing", "credit_units": 2},
            {"code": "EEE 538", "title": "Digital Communications Systems", "credit_units": 2},
            {"code": "EEE 519", "title": "Telecommunication Service Design", "credit_units": 2},
            {"code": "EEE 510", "title": "Electromechanical Devices Design", "credit_units": 2},
            {"code": "EEE 511", "title": "Special Topics", "credit_units": 2},
        ]
        
        for course_data in courses_500_second:
            course, created = Course.objects.get_or_create(
                code=course_data["code"],
                defaults={
                    "title": course_data["title"],
                    "credit_units": course_data["credit_units"],
                    "level": level_500,
                    "semester": second_semester
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created course: {course.code} - {course.title}"))
            else:
                self.stdout.write(f"Course {course.code} already exists")

        self.stdout.write(self.style.SUCCESS('Database population completed successfully!'))

# exec(open("populate_academic_data.py").read())