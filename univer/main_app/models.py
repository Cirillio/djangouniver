from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class Member(AbstractUser):
    """Кастомная модель пользователя с ролями"""
    ROLE_CHOICES = [
        ('teacher', 'Преподаватель'),
        ('student', 'Студент'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    full_name = models.CharField(max_length=100, verbose_name="ФИО")
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
    
    def __str__(self):
        return f"{self.full_name} ({self.get_role_display()})"
    
    def is_teacher(self):
        return self.role == 'teacher'
    
    def is_student(self):
        return self.role == 'student'


class Course(models.Model):
    """Курсы, которые создают преподаватели"""
    name = models.CharField(max_length=200, verbose_name="Название курса")
    description = models.TextField(verbose_name="Описание")
    teacher = models.ForeignKey(
        Member, 
        on_delete=models.CASCADE, 
        limit_choices_to={'role': 'teacher'},
        verbose_name="Преподаватель"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    
    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.teacher.full_name}"


class Lesson(models.Model):
    """Занятия в курсе"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200, verbose_name="Название занятия")
    description = models.TextField(verbose_name="Описание занятия")
    date = models.DateField(verbose_name="Дата проведения")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Занятие"
        verbose_name_plural = "Занятия"
        ordering = ['date']
    
    def __str__(self):
        return f"{self.course.name} - {self.title}"


class Assignment(models.Model):
    """Задания по занятиям"""
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=200, verbose_name="Название задания")
    description = models.TextField(verbose_name="Описание задания")
    due_date = models.DateTimeField(verbose_name="Срок сдачи")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, verbose_name="Активно")
    
    class Meta:
        verbose_name = "Задание"
        verbose_name_plural = "Задания"
        ordering = ['due_date']
    
    def __str__(self):
        return f"{self.lesson.course.name} - {self.title}"
    
    def is_overdue(self):
        return timezone.now() > self.due_date


class StudentAnswer(models.Model):
    """Ответы студентов на задания"""
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='answers')
    student = models.ForeignKey(
        Member, 
        on_delete=models.CASCADE, 
        limit_choices_to={'role': 'student'},
        verbose_name="Студент"
    )
    answer_text = models.TextField(verbose_name="Текст ответа", blank=True)
    answer_file = models.FileField(
        upload_to='answers/%Y/%m/%d/', 
        blank=True, 
        null=True, 
        verbose_name="Файл ответа"
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Ответ студента"
        verbose_name_plural = "Ответы студентов"
        unique_together = ['assignment', 'student']
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"{self.student.full_name} - {self.assignment.title}"
    
    def is_late(self):
        return self.submitted_at > self.assignment.due_date


class Grade(models.Model):
    """Оценки за выполненные задания"""
    GRADE_CHOICES = [
        ('5', 'Отлично (5)'),
        ('4', 'Хорошо (4)'),
        ('3', 'Удовлетворительно (3)'),
        ('2', 'Неудовлетворительно (2)'),
        ('pass', 'Зачтено'),
        ('fail', 'Не зачтено'),
    ]
    
    answer = models.OneToOneField(StudentAnswer, on_delete=models.CASCADE, related_name='grade')
    grade = models.CharField(max_length=4, choices=GRADE_CHOICES, verbose_name="Оценка")
    comment = models.TextField(blank=True, verbose_name="Комментарий преподавателя")
    graded_by = models.ForeignKey(
        Member, 
        on_delete=models.CASCADE, 
        limit_choices_to={'role': 'teacher'},
        verbose_name="Оценил"
    )
    graded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Оценка"
        verbose_name_plural = "Оценки"
        ordering = ['-graded_at']
    
    def __str__(self):
        return f"{self.answer.student.full_name} - {self.get_grade_display()}"


class Comment(models.Model):
    """Комментарии к заданиям"""
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(Member, on_delete=models.CASCADE, verbose_name="Автор")
    text = models.TextField(verbose_name="Текст комментария")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.author.full_name}: {self.text[:50]}..."


class CourseEnrollment(models.Model):
    """Запись студентов на курсы"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    student = models.ForeignKey(
        Member, 
        on_delete=models.CASCADE, 
        limit_choices_to={'role': 'student'},
        related_name='enrolled_courses'
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Запись на курс"
        verbose_name_plural = "Записи на курсы"
        unique_together = ['course', 'student']
        ordering = ['-enrolled_at']
    
    def __str__(self):
        return f"{self.student.full_name} -> {self.course.name}"