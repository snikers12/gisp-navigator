from django.conf import settings
from rest_framework.pagination import PageNumberPagination


class PageNumberPaginationWithQueryParams(PageNumberPagination):
    page_size_query_param = 'page_size'
    max_page_size = settings.REST_FRAMEWORK['PAGE_SIZE']


class PageNumberPaginationWithQueryParamsBy10(PageNumberPagination):
    page_size = 10


class PageNumberPaginationWithQueryParamsBy20(PageNumberPagination):
    page_size = 20
