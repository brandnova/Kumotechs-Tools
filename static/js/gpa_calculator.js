// static/js/gpa_calculator.js
function gpaCalculator() {
    return {
      courses: [],
      selectedLevel: '',
      selectedSemester: '',
      searchQuery: '',
      selectedCourses: [],
      savedSemesters: [],
      gradePoints: {
        'A': 5.00,
        'B': 4.00,
        'C': 3.00,
        'D': 2.00,
        'E': 1.00,
        'F': 0.00
      },
      levelNames: {},
      semesterNames: {},
      
      init() {
        // Store level and semester names for display
        document.querySelectorAll('#id_selectedLevel option').forEach(option => {
          if (option.value) {
            this.levelNames[option.value] = option.textContent;
          }
        });
        
        document.querySelectorAll('#id_selectedSemester option').forEach(option => {
          if (option.value) {
            this.semesterNames[option.value] = option.textContent;
          }
        });
        
        // Load saved data from localStorage
        this.loadFromLocalStorage();
      },
      
      loadFromLocalStorage() {
        // Load selected courses
        const savedCourses = localStorage.getItem('selectedCourses');
        if (savedCourses) {
          this.selectedCourses = JSON.parse(savedCourses);
        }
        
        // Load saved semesters for CGPA calculation
        const savedSemesters = localStorage.getItem('savedSemesters');
        if (savedSemesters) {
          this.savedSemesters = JSON.parse(savedSemesters);
        }
      },
      
      saveToLocalStorage() {
        localStorage.setItem('selectedCourses', JSON.stringify(this.selectedCourses));
        localStorage.setItem('savedSemesters', JSON.stringify(this.savedSemesters));
      },
      
      loadCourses() {
        if (!this.selectedLevel || !this.selectedSemester) {
          this.courses = [];
          return;
        }
        
        // Fetch courses from API
        fetch(`/academic_tools/api/courses/?level=${this.selectedLevel}&semester=${this.selectedSemester}`)
          .then(response => response.json())
          .then(data => {
            this.courses = data.courses || [];
          })
          .catch(error => {
            console.error('Error fetching courses:', error);
            this.courses = [];
          });
      },
      
      get filteredCourses() {
        if (!this.searchQuery.trim()) {
          return this.courses;
        }
        
        const query = this.searchQuery.toLowerCase().trim();
        return this.courses.filter(course => 
          course.code.toLowerCase().includes(query) || 
          course.title.toLowerCase().includes(query)
        );
      },
      
      isSelected(courseId) {
        return this.selectedCourses.some(course => course.id === courseId);
      },
      
      addCourse(course) {
        if (!this.isSelected(course.id)) {
          this.selectedCourses.push({
            ...course,
            grade: null,
          });
          this.saveToLocalStorage();
        }
      },
      
      removeCourse(index) {
        this.selectedCourses.splice(index, 1);
        this.saveToLocalStorage();
      },
      
      selectGrade(index, grade) {
        this.selectedCourses[index].grade = grade;
        this.saveToLocalStorage();
      },
      
      calculateCreditPoints(course) {
        if (!course.grade) {
          return '—';
        }
        const gradePoint = this.gradePoints[course.grade] || 0;
        return (gradePoint * course.credit_units).toFixed(2);
      },
      
      get totalCreditUnits() {
        return this.selectedCourses.reduce((total, course) => total + course.credit_units, 0);
      },
      
      get totalCreditPoints() {
        return this.selectedCourses.reduce((total, course) => {
          if (!course.grade) return total;
          const gradePoint = this.gradePoints[course.grade] || 0;
          return total + (gradePoint * course.credit_units);
        }, 0).toFixed(2);
      },
      
      calculateGPA() {
        const totalCU = this.totalCreditUnits;
        const totalCP = parseFloat(this.totalCreditPoints);
        
        if (totalCU === 0) return '0.00';
        
        return (totalCP / totalCU).toFixed(2);
      },
      
      saveGPA() {
        const levelName = this.levelNames[this.selectedLevel] || this.selectedLevel;
        const semesterName = this.semesterNames[this.selectedSemester] || this.selectedSemester;
        const label = `${levelName} - ${semesterName}`;
        
        // Check if all courses have grades
        const allGraded = this.selectedCourses.every(course => course.grade);
        if (!allGraded) {
          alert('Please assign grades to all courses before saving.');
          return;
        }
        
        const semesterResult = {
          level_id: this.selectedLevel,
          semester_id: this.selectedSemester,
          label: label,
          gpa: this.calculateGPA(),
          total_credit_units: this.totalCreditUnits,
          total_credit_points: parseFloat(this.totalCreditPoints)
        };
        
        // Save to server (you can implement this)
        fetch('/academic_tools/api/calculate-gpa/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            level: this.selectedLevel,
            semester: this.selectedSemester,
            courses: this.selectedCourses.map(course => ({
              id: course.id,
              code: course.code,
              credit_units: course.credit_units,
              grade: course.grade,
              credit_points: parseFloat(this.calculateCreditPoints(course))
            }))
          })
        })
        .then(response => response.json())
        .then(data => {
          console.log('GPA saved:', data);
          
          // Add to saved semesters for CGPA calculation
          this.savedSemesters.push(semesterResult);
          this.saveToLocalStorage();
          
          // Optional: Clear selected courses for next calculation
          // this.selectedCourses = [];
        })
        .catch(error => {
          console.error('Error saving GPA:', error);
          
          // Even if server save fails, save to local storage
          this.savedSemesters.push(semesterResult);
          this.saveToLocalStorage();
        });
      },
      
      removeSavedSemester(index) {
        this.savedSemesters.splice(index, 1);
        this.saveToLocalStorage();
      },
      
      get cgpaTotalCreditUnits() {
        return this.savedSemesters.reduce((total, semester) => 
          total + semester.total_credit_units, 0);
      },
      
      get cgpaTotalCreditPoints() {
        return this.savedSemesters.reduce((total, semester) => 
          total + semester.total_credit_points, 0).toFixed(2);
      },
      
      calculateCGPA() {
        const totalCU = this.cgpaTotalCreditUnits;
        const totalCP = parseFloat(this.cgpaTotalCreditPoints);
        
        if (totalCU === 0) return '0.00';
        
        return (totalCP / totalCU).toFixed(2);
      },
      
      saveCGPA() {
        if (this.savedSemesters.length === 0) {
          alert('Please save at least one semester GPA first.');
          return;
        }
        
        fetch('/academic_tools/api/calculate-cgpa/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            semesters: this.savedSemesters
          })
        })
        .then(response => response.json())
        .then(data => {
          console.log('CGPA saved:', data);
          alert(`CGPA of ${data.cgpa} has been saved successfully!`);
        })
        .catch(error => {
          console.error('Error saving CGPA:', error);
          alert(`CGPA calculation complete: ${this.calculateCGPA()} (Offline mode)`);
        });
      },
      
      resetCalculator() {
        if (confirm('Are you sure you want to reset all calculations? This action cannot be undone.')) {
          this.selectedCourses = [];
          this.savedSemesters = [];
          this.saveToLocalStorage();
        }
      }
    };
  }