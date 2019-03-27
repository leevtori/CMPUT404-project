from rest_framework import pagination
from rest_framework.response import Response


class CustomPaginator(pagination.PageNumberPagination):
    def get_paginated_response(self, data):
        response_data = {}
        if self.get_next_link():
            response_data["next"] = self.get_next_link()

        if self.get_previous_link():
            response_data["previous"] = self.get_previous_link()

        response_data["count"] = self.page.paginator.count,
        response_data["data"] = data

        return Response(response_data)
