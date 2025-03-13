from django.urls import path

from .views import (
    CausesGet,
    CausesPatch,
    CausesPost,
    ValidateView
)

urlpatterns = [
    path('', CausesPost.as_view(), name="create_causes"),
    path('<uuid:question_id>/', CausesGet.as_view({ 'get': 'get_list' }), name="get_causes_list"),
    path('<uuid:question_id>/<uuid:pk>', CausesGet.as_view({ 'get': 'get' }), name="get_causes"),
    path('patch/<uuid:question_id>/<uuid:pk>/', CausesPatch.as_view({'patch': 'patch_cause'}), name="patch_causes"),
    path('validate/<uuid:question_id>/', ValidateView.as_view(), name="validate_causes"),
]