from rest_framework.pagination import PageNumberPagination

from foodgram_backend.settings import CUSTOM_PAGINATION_PAGE_SIZE


class CustomPagination(PageNumberPagination):
    page_size = CUSTOM_PAGINATION_PAGE_SIZE
    page_size_query_param = 'limit'
