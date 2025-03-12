from django.urls import path

from .views import (
    CausesPost
)

urlpatterns = [
    path('causes/', CausesPost.as_view(), name="create_causes"),
]
