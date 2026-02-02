from django.db import models
from django.contrib.auth.models import User


class UserData(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)

    def __str__(self):
        return self.user.username

# ===============================
# 1. Department
# ===============================
class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


# ===============================
# 2. Faculty Profile
# (Login via email + password using Django User)
# ===============================
class Faculty(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    name = models.CharField(max_length=120)
    email = models.EmailField(unique=True)
    contact_no = models.CharField(max_length=15)
    erp_id = models.CharField(max_length=30, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# ===============================
# 3. Student Profile
# (Registered by Faculty)
# ===============================
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE
    )

    name = models.CharField(max_length=120)
    email = models.EmailField(unique=True)
    contact_no = models.CharField(max_length=15)
    roll_no = models.CharField(max_length=30, unique=True)

    profile_picture = models.ImageField(
        upload_to='students/profile/',
        blank=True,
        null=True
    )

    # 🔥 FACE RECOGNITION
    face_embedding = models.TextField(blank=True, null=True)
    face_registered = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.roll_no})"


# ===============================
# 4. Face Registration Log
# ===============================
class FaceRegistrationLog(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    registered_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=30, default='SUCCESS')

    def __str__(self):
        return f"{self.student.name} - {self.status}"


# ===============================
# 5. Subject
# ===============================
class Subject(models.Model):
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


# ===============================
# 6. Time Table
# ===============================
class TimeTable(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    day = models.CharField(max_length=10)  # Monday, Tuesday
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.subject.name} - {self.day}"


# ===============================
# 7. Attendance
# (Face + Manual)
# ===============================
class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    date = models.DateField()

    status = models.CharField(
        max_length=10,
        choices=[('Present', 'Present'), ('Absent', 'Absent')],
        default='Absent'
    )

    marked_by_face = models.BooleanField(default=False)
    auto_marked = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'date')

    def __str__(self):
        return f"{self.student.name} - {self.date} - {self.status}"

# ===============================
# 8. Holiday
# ===============================
class Holiday(models.Model):
    date = models.DateField(unique=True)
    reason = models.CharField(max_length=200)

    def __str__(self):
        return str(self.date)


class FacultyTimeSetting(models.Model):
    faculty = models.OneToOneField(Faculty, on_delete=models.CASCADE)

    start_time = models.TimeField(default="09:00")
    grace_minutes = models.IntegerField(default=15)
    end_time = models.TimeField(default="17:00")

    def __str__(self):
        return f"{self.faculty.user.username} Timing"