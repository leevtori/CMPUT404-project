from rest_framework import pagination
from rest_framework.response import Response


class CustomPaginator(pagination.PageNumberPagination):
    def get_paginated_response(self, data, **kwargs):
        response_data = {}
        query = kwargs.get("query", None)
        if query:
            response_data["query"] = query
        if self.get_next_link():
            response_data["next"] = self.get_next_link()

        if self.get_previous_link():
            response_data["previous"] = self.get_previous_link()

        response_data["count"] = self.page.paginator.count

        key = kwargs.get("model", "data")
        response_data[key] = data

        return Response(response_data)
