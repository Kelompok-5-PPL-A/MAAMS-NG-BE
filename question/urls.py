from django.urls import path

from .views import (
    QuestionGetMatched, QuestionPost, QuestionGet, QuestionGetRecent, QuestionGetPrivileged, QuestionDelete, QuestionGetAll, QuestionGetFieldValues, QuestionPatch
)

urlpatterns = [
    path('submit/', QuestionPost.as_view(), name="create_question"),
    path('<uuid:pk>/', QuestionGet.as_view({'get': 'retrieve'}), name="get_question"),
    path('recent/', QuestionGetRecent.as_view(), name='recent-question'),
    path('history/', QuestionGetAll.as_view(), name='get_all'),
    path('history/search/', QuestionGetMatched.as_view(), name="get_matched"),
    path('history/field-values/', QuestionGetFieldValues.as_view(), name='get_field_values'),
    path('history/privileged/', QuestionGetPrivileged.as_view(), name='privileged-question'),
    path('<uuid:pk>/delete/', QuestionDelete.as_view(), name="delete_question"),
    path('ubah/<uuid:pk>/', QuestionPatch.as_view({'patch': 'patch_mode'}), name="patch_mode_question"),
    path('ubah/judul/<uuid:pk>/', QuestionPatch.as_view({'patch': 'patch_title'}), name="patch_title_question"),
    path('ubah/tags/<uuid:pk>/', QuestionPatch.as_view({'patch': 'patch_tags'}), name="patch_tags_question"),
]