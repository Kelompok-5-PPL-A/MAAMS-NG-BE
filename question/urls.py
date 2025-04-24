from django.urls import path

from .views import (
    QuestionPost, QuestionGet, QuestionGetRecent, QuestionGetPrivileged,
)

urlpatterns = [
    path('submit/', QuestionPost.as_view(), name="create_question"),
    path('<uuid:pk>/', QuestionGet.as_view({'get': 'retrieve'}), name="get_question"),
    path('recent/', QuestionGetRecent.as_view(), name='recent-question'),
    path('search/', QuestionGet.as_view({'get': 'get_matched'}), name="get_matched"),
    path('privileged/', QuestionGetPrivileged.as_view(), name='privileged-question'),

]
