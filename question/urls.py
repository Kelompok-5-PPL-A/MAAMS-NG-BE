from django.urls import path
from . import views

urlpatterns = [
    path('form/', views.display_question_form, name='display_question_form'),
    path('submit/', views.process_question_form, name='process_question_form'),
    path('success/', views.success, name='success'),
    path('remove/<uuid:question_id>/', views.remove_question, name='remove_question'),
    path('remove-success/', views.remove_success, name='remove_success'),
]