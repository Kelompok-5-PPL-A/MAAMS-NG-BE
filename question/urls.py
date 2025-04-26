from django.urls import path

from .views import (
    QuestionGetMatched, QuestionPost, QuestionGet, QuestionGetRecent, QuestionGetPrivileged, QuestionGetAll, QuestionGetFieldValues
)

urlpatterns = [
    path('submit/', QuestionPost.as_view(), name="create_question"),
    path('<uuid:pk>/', QuestionGet.as_view({'get': 'retrieve'}), name="get_question"),
    path('recent/', QuestionGetRecent.as_view(), name='recent-question'),
    path('history/', QuestionGetAll.as_view(), name='get_all'),
    path('history/search/', QuestionGetMatched.as_view(), name="get_matched"),
    path('history/field-values/', QuestionGetFieldValues.as_view(), name='get_field_values'),
    path('privileged/', QuestionGetPrivileged.as_view(), name='privileged-question'),
]