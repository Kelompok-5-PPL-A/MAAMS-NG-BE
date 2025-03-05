from django.urls import path
from . import views

urlpatterns = [
    path('submit/', views.submit_question, name='submit_question'),
    path('success/', views.success, name='success'),  # A success page after form submission
    path('remove/<uuid:question_id>/', views.remove_question, name='remove_question'),
    path('remove-success/', views.remove_success, name='remove_success'),
]