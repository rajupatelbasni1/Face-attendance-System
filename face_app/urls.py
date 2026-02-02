from django.urls import path
from . import views
from . import views_admin
from django.contrib.auth import views as auth_views

urlpatterns = [
    # path('admin-panel/', views_admin.admin_dashboard, name='admin_dashboard'),
    # path('admin-panel/departments/', views_admin.departments, name='admin_departments'),
    # path('admin-panel/subjects/', views_admin.subjects, name='admin_subjects'),
    # path('admin-panel/timetable/', views_admin.timetable, name='admin_timetable'),
    # path('admin-panel/holidays/', views_admin.holidays, name='admin_holidays'),
    # path('admin-panel/attendance/', views_admin.attendance, name='admin_attendance'),
    
    path('login', views.login_view, name='login_view'),
    
    # path('student/student_dashboard2', views.student_dashboard, name='student_dashboard'),


    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/attendance/', views.view_attendance, name='view_attendance'),
    # path('student/monthly-report/', views.monthly_report, name='monthly_report'),
    path('student/monthly-report/', views.student_monthly_report, name='student_monthly_report'),
    path('student/performance/', views.performance, name='performance'),
    path('student/profile/', views.student_profile, name='student_profile'),
    path('login', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('profile/', views.profile, name='profile'),


    # path('faculty/faculty_dashboard', views.faculty_dashboard, name='faculty_dashboard'),

    ## faculty link


    path('faculty/dashboard/', views.faculty_dashboard, name='faculty_dashboard'),
    path('faculty/add-student/', views.add_student, name='add_student'),
    path('faculty/delete-student/<int:id>/', views.delete_student, name='delete_student'),
    path('faculty/student-attendance/<int:id>/', views.student_attendance, name='student_attendance'),
    path('faculty/register-face/<int:id>/', views.register_face, name='register_face'),
    path('faculty/edit-attendance/', views.edit_student_attendance, name='edit_attendance'),





    path('capture/', views.capture_page, name='capture_page'),
    path('capture_face/', views.capture_face, name='capture_face'),
    path('video_feed/', views.video_feed, name='video_feed'),
    path('recognize/', views.recognize_page, name='recognize_page'),
]
