from django.urls import path
from cause.views import CausesPost

urlpatterns = [
    path('causes/', CausesPost.as_view(), name='causes-create'),
]
