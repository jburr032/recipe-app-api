from django.urls import path, include
from rest_framework.routers import DefaultRouter

from recipe import views

# DefaultRouter generates routers for all of our viewsets
router = DefaultRouter()

# Register our viewset with our router
router.register('tags', views.TagViewSet)

app_name = 'recipe'

urlpatterns = [
    path('', include(router.urls))
]
