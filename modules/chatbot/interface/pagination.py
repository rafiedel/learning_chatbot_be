from rest_framework.pagination import PageNumberPagination

class ChatSessionPagination(PageNumberPagination):
    page_size = 20

class ChatMessagePagination(PageNumberPagination):
    page_size = 5