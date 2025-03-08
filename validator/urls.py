from django.urls import path

from validator.views.causes import (
    CausesPost
)


app_name = 'validator'

urlpatterns = [    
    # causes
    path('causes/', CausesPost.as_view(), name="create_causes"),
]
