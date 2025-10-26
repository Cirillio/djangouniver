from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('students/list', views.students, name='students'),
    path('journal/', views.journal, name='journal'),
]