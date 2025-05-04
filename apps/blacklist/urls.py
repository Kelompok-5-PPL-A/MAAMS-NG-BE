from django.urls import path
from apps.blacklist.views import (
    BlacklistCheckView,
    CurrentUserBlacklistCheckView,
    BlacklistAddView,
    BlacklistRemoveView,
    BlacklistHistoryView,
    ActiveBlacklistsView
)

urlpatterns = [
    path('blacklist/check/', BlacklistCheckView.as_view(), name='blacklist_check'),
    path('blacklist/check/me/', CurrentUserBlacklistCheckView.as_view(), name='blacklist_check_me'),
    
    # Admin-only endpoints
    path('blacklist/add/', BlacklistAddView.as_view(), name='blacklist_add'),
    path('blacklist/remove/', BlacklistRemoveView.as_view(), name='blacklist_remove'),
    path('blacklist/history/', BlacklistHistoryView.as_view(), name='blacklist_history'),
    path('blacklist/active/', ActiveBlacklistsView.as_view(), name='active_blacklists'),
]