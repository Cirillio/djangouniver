from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from .models import Member

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), label="Пароль")
    password_confirm = forms.CharField(widget=forms.PasswordInput(), label="Подтвердите пароль")
    
    class Meta:
        model = Member
        fields = ['username', 'email', 'full_name', 'role', 'password']
        labels = {
            'username': 'Логин',
            'email': 'Email',
            'full_name': 'ФИО',
            'role': 'Роль',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].widget = forms.RadioSelect(choices=Member.ROLE_CHOICES)
    
    def clean_password_confirm(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Пароли не совпадают")
        return password_confirm
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

def home(request):
    if request.user.is_authenticated:
        if request.user.is_teacher():
            return redirect('teacher_dashboard')
        else:
            return redirect('student_dashboard')
    return render(request, 'main/home.html')


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {user.full_name}!')
                return redirect('home')
    else:
        form = AuthenticationForm()

    form.fields['username'].widget.attrs.update({'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg'})
    form.fields['password'].widget.attrs.update({'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg'})
    
    return render(request, 'main/login.html', {'form': form})


def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserRegistrationForm()
        
    
    # Добавляй CSS классы ВСЕГДА, не только в else
    form.fields['username'].widget.attrs.update({'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'})
    form.fields['email'].widget.attrs.update({'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'})
    form.fields['full_name'].widget.attrs.update({'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'})
    form.fields['password'].widget.attrs.update({'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'})
    form.fields['password_confirm'].widget.attrs.update({'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'})
    
    return render(request, 'main/register.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'Вы вышли из системы')
    return redirect('home')

@login_required
def teacher_dashboard(request):
    if not request.user.is_teacher():
        messages.error(request, 'Доступ запрещен')
        return redirect('home')
    
    from .models import Course, Assignment
    courses = Course.objects.filter(teacher=request.user)
    recent_assignments = Assignment.objects.filter(lesson__course__teacher=request.user).order_by('-created_at')[:5]
    
    context = {
        'courses': courses,
        'recent_assignments': recent_assignments,
    }
    return render(request, 'main/teacher_dashboard.html', context)

@login_required  
def student_dashboard(request):
    if not request.user.is_student():
        messages.error(request, 'Доступ запрещен')
        return redirect('home')
    
    from .models import CourseEnrollment, Assignment, StudentAnswer
    enrollments = CourseEnrollment.objects.filter(student=request.user, is_active=True)
    
    # Получаем активные задания для студента
    active_assignments = Assignment.objects.filter(
        lesson__course__enrollments__student=request.user,
        lesson__course__enrollments__is_active=True,
        is_active=True
    ).order_by('due_date')[:5]
    
    # Получаем последние ответы студента
    recent_answers = StudentAnswer.objects.filter(student=request.user).order_by('-submitted_at')[:5]
    
    context = {
        'enrollments': enrollments,
        'active_assignments': active_assignments,
        'recent_answers': recent_answers,
    }
    return render(request, 'main/student_dashboard.html', context)