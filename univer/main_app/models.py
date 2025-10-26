from django.db import models

class Group(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return str(self.name)
    

class Student(models.Model):
    name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    mid_name = models.CharField(max_length=20, blank=True, null=True)

    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    def __str__(self):
        return  f"{self.last_name} {self.name} {self.group}"     


class Subject(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    

class GradeType(models.Model):
    name = models.CharField(max_length=20, unique=True)
    display_name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.display_name

class Grade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    grade_type = models.ForeignKey(GradeType, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    
    class Meta:
        unique_together = ('student', 'subject')
    
    def __str__(self):
        return f"{self.student} - {self.subject}: {self.grade_type}"