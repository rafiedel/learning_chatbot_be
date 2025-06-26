from rest_framework.pagination import PageNumberPagination

class BigPagination(PageNumberPagination):
    page_size = 20

class SmallPagination(PageNumberPagination):
    page_size = 5