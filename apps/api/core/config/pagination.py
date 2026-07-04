from rest_framework.pagination import PageNumberPagination


# Class representing DefaultPageNumberPagination
class DefaultPageNumberPagination(PageNumberPagination):
    """Honors `page` and `page_size` query params for grid UIs."""

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100
