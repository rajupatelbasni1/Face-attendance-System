from django.contrib import admin
from .models import Student, Faculty, Department, Subject, TimeTable, Holiday, Attendance


admin.site.register(Student)


admin.site.register(Faculty)
admin.site.register(Department)
admin.site.register(Subject)
admin.site.register(TimeTable)
admin.site.register(Holiday)
admin.site.register(Attendance)
# @admin.register(Student)
# class StudentAdmin(admin.ModelAdmin):
#     list_display = ('name', 'user', 'department')