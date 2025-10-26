from django.shortcuts import render
from django.core.paginator import Paginator
from .models import Student, Group, Grade, Subject

def home(request):
    return render(request, 'main/home.html')

def students(request):
    students_list = Student.objects.select_related('group').all()

    # Пагинация: по 2 студента на страницу
    paginator = Paginator(students_list, 2)
    page_number = request.GET.get('page')
    students = paginator.get_page(page_number)

    return render(request, 'main/students.html', {
        'students': students,
        'total_students': students_list.count()
    })

def journal(request):
    subjects = Subject.objects.all()
    groups = Group.objects.all()
    context = {
        'subjects': subjects, 
        'groups': groups,
        'selected_subject': None,
        'selected_group': None,
        'students': [],
        'error': None
    }

    selected_subject_id = request.GET.get('subject')
    selected_group_id = request.GET.get('group')

    if selected_subject_id and selected_group_id:
        try:
            subject = Subject.objects.get(id=selected_subject_id)
            group = Group.objects.get(id=selected_group_id)
            students = Student.objects.filter(group=group).order_by('last_name', 'name')

            context.update({
                'selected_subject': subject,
                'selected_group': group,
                'students': students,
            })

        except (Subject.DoesNotExist, Group.DoesNotExist, ValueError):
            context['error'] = 'Выбранный предмет или группа не найдены'

    return render(request, 'main/journal.html', context)