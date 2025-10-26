from django.contrib import admin

from .models import Group, Student, Grade, Subject, GradeType

admin.site.register(Group)
admin.site.register(Student)
admin.site.register(Subject)
admin.site.register(GradeType)
admin.site.register(Grade)