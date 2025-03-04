from django.urls import path
from . import views

urlpatterns = [
    path('submit/', views.submit_question, name='submit_question'),
    path('success/', views.success, name='success'),  # A success page after form submission
]