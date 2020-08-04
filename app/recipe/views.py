from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient
from recipe import serializers


class BaseClassRecipeAttributes(viewsets.GenericViewSet,
                                mixins.ListModelMixin,
                                mixins.CreateModelMixin):
    """ Base class for recipes views """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    # Need to override the built-in get_queryset to specify
    # what query you want returned
    def get_queryset(self):
        """ Returns objects for the authenticated user only """
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        # Set the user model instane to the 'user' field on the Tag model
        serializer.save(user=self.request.user)


class TagViewSet(BaseClassRecipeAttributes):
    """ Manage tags in the database """

    # Need to provide a query_set when using a
    # ListModel mixin in the generics viewset
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class IngredientViewSet(BaseClassRecipeAttributes):

    """ Manage ingredients in the database """
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
