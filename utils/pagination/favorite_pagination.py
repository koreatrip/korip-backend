from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class FavoritePagination(PageNumberPagination):
    page_size = 9
    page_query_param = "page"
    page_size_query_param = 'page_size'
    max_page_size = 100
    results_field_name = "results"

    def get_paginated_response(self, data):
        return Response({
            "count": self.page.paginator.count,
            "total_pages": self.page.paginator.num_pages,
            "page": self.page.number,
            "page_size": self.get_page_size(self.request) or self.page_size,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            self.results_field_name: data,
        })