from rest_framework.viewsets import ViewSet
from rest_framework.response import Response


class TestApi(ViewSet):


    def list(self, request, format=None):
        """
        Return a list of all users.
        """
        return Response('test')