from django.urls import path

from .views import (
    QuestionPost, QuestionGet
)

urlpatterns = [
    path('submit/', QuestionPost.as_view(), name="create_question"),
    path('<uuid:pk>/', QuestionGet.as_view({ 'get': 'get' }), name="get_question"),
]
