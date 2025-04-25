from django.urls import path

from .views import (
    QuestionGetMatched, QuestionPost, QuestionGet, QuestionGetRecent, QuestionGetPrivileged, QuestionGetAll
)

urlpatterns = [
    path('submit/', QuestionPost.as_view(), name="create_question"),
    path('<uuid:pk>/', QuestionGet.as_view({'get': 'retrieve'}), name="get_question"),
    path('recent/', QuestionGetRecent.as_view(), name='recent-question'),
    path('search/', QuestionGetMatched.as_view(), name="get_matched"),
    path('history/', QuestionGetAll.as_view(), name='get_all'),
    path('privileged/', QuestionGetPrivileged.as_view(), name='privileged-question'),
]
