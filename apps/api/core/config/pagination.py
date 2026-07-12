from rest_framework.pagination import PageNumberPagination


class DefaultPageNumberPagination(PageNumberPagination):
    """Honors `page`, `page_size`, and `per_page` query params for grid UIs."""

    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_page_size(self, request):
        per_page = request.query_params.get('per_page')
        if per_page is not None:
            try:
                return min(int(per_page), self.max_page_size)
            except (TypeError, ValueError):
                pass
        return super().get_page_size(request)
