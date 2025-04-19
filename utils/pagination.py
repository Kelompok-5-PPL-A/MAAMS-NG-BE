from rest_framework import pagination
from rest_framework.response import Response

class CustomPageNumberPagination(pagination.PageNumberPagination):
    '''
    Custom class to enable pagination with count

    Example how to use this pagination:
    Suppose we want to get the history data for page 1, but we limit it to 4.
    We can call
    <BASE>/api/history/search?keyword=Indo&count=4&p=1
    '''
    page_size = 3
    page_size_query_param = 'count'
    max_page_size = 5
    page_query_param = 'p'

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })