from django.urls import path

from .views import (
    QuestionPost,
)

urlpatterns = [
    path('submit/', QuestionPost.as_view(), name="create_question"),
]
