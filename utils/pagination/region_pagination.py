from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class RegionPagination(PageNumberPagination):
    page_size = 24
    page_query_param = "page"
    page_size_query_param = "page_size"  # 클라이언트가 ?page_size=로 조절 가능
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            "count": self.page.paginator.count,
            "total_pages": self.page.paginator.num_pages,
            "page": self.page.number,
            "page_size": self.get_page_size(self.request) or self.page_size,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            "regions": data,
        })