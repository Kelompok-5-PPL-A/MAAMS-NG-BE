from django.urls import path
from apps.blacklist.views import (add_blacklist, remove_blacklist, check_blacklist_status, check_current_user_blacklist) 

urlpatterns = [
    path('blacklist/add/', add_blacklist, name='add_blacklist'),
    path('blacklist/remove/', remove_blacklist, name='remove_blacklist'),
    path('blacklist/check/auth/', check_blacklist_status, name='check_blacklist_auth'),
    path('blacklist/check/me/', check_current_user_blacklist, name='check_current_user_blacklist'),
]