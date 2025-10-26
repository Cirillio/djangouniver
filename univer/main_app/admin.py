from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Member, Course, Lesson, Assignment, 
    StudentAnswer, Grade, Comment, CourseEnrollment
)

@admin.register(Member)
class MemberAdmin(UserAdmin):
    list_display = ('username', 'full_name', 'email', 'role', 'is_active')
    list_filter = ('role', 'is_active', 'date_joined')
    search_fields = ('username', 'full_name', 'email')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('role', 'full_name')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительная информация', {
            'fields': ('role', 'full_name', 'email')
        }),
    )

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'teacher', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at', 'teacher')
    search_fields = ('name', 'description', 'teacher__full_name')
    date_hierarchy = 'created_at'

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'date', 'created_at')
    list_filter = ('course', 'date')
    search_fields = ('title', 'description', 'course__name')
    date_hierarchy = 'date'

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson', 'due_date', 'is_active')
    list_filter = ('is_active', 'due_date', 'lesson__course')
    search_fields = ('title', 'description', 'lesson__title')
    date_hierarchy = 'due_date'

@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ('student', 'assignment', 'submitted_at', 'is_late')
    list_filter = ('submitted_at', 'assignment__lesson__course')
    search_fields = ('student__full_name', 'assignment__title', 'answer_text')
    date_hierarchy = 'submitted_at'
    
    def is_late(self, obj):
        return obj.is_late()
    is_late.boolean = True
    is_late.short_description = 'Опоздание'

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('answer', 'grade', 'graded_by', 'graded_at')
    list_filter = ('grade', 'graded_at', 'graded_by')
    search_fields = ('answer__student__full_name', 'answer__assignment__title')
    date_hierarchy = 'graded_at'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'assignment', 'created_at', 'text_preview')
    list_filter = ('created_at', 'author__role')
    search_fields = ('author__full_name', 'assignment__title', 'text')
    date_hierarchy = 'created_at'
    
    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Текст'

@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_at', 'is_active')
    list_filter = ('is_active', 'enrolled_at', 'course')
    search_fields = ('student__full_name', 'course__name')
    date_hierarchy = 'enrolled_at'