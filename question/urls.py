from django.urls import path

from .views import (
    QuestionGetMatched, QuestionPost, QuestionGet, QuestionGetRecent, QuestionGetPrivileged, QuestionDelete
)

urlpatterns = [
    path('submit/', QuestionPost.as_view(), name="create_question"),
    path('<uuid:pk>/', QuestionGet.as_view({'get': 'retrieve'}), name="get_question"),
    path('recent/', QuestionGetRecent.as_view(), name='recent-question'),
    path('search/', QuestionGetMatched.as_view(), name="get_matched"),
    path('<uuid:pk>/delete/', QuestionDelete.as_view(), name="delete_question"),
    path('privileged/', QuestionGetPrivileged.as_view(), name='privileged-question'),
]
