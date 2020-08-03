from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag
from recipe import serializers


class TagViewSet(viewsets.GenericViewSet,
                 mixins.ListModelMixin,
                 mixins.CreateModelMixin):
    """ Manage tags in the database """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    # Need to provide a query_set when using a
    # ListModel mixin in the generics viewset
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer

    # Need to override the built-in get_queryset to specify what query you want returned
    def get_queryset(self):
        """ Return tag objects for the authenticated user only """
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """ A new tag """
        # Set the user model instane to the 'user' field on the Tag model
        print('THIS IS THE SERIALIZER', serializer)
        serializer.save(user=self.request.user)