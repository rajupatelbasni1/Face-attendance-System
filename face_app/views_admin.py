from django.shortcuts import render, redirect
from .models import *

def admin_dashboard(request):
    return render(request, 'admin_panel/dashboard.html', {
        'students': Student.objects.count(),
        'subjects': Subject.objects.count(),
        'faculty': Faculty.objects.count(),
        'attendance': Attendance.objects.filter(date=date.today()).count()
    })
