from rest_framework.pagination import PageNumberPagination

CUSTOM_PAGINATION_PAGE_SIZE = 6


class CustomPagination(PageNumberPagination):
    page_size = CUSTOM_PAGINATION_PAGE_SIZE
    page_size_query_param = 'limit'
