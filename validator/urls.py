from django.urls import path

from validator.views.questions import (
    QuestionPost,
) 
from validator.views.causes import (
    CausesPost
)


app_name = 'validator'

urlpatterns = [
    # questions
    path('baru/', QuestionPost.as_view(), name="create_question"),
    
    
    # causes
    path('causes/', CausesPost.as_view(), name="create_causes"),
]
