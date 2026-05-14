from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DataSourceViewSet, PipelineRunViewSet

router = DefaultRouter()
router.register('sources', DataSourceViewSet)
router.register('runs', PipelineRunViewSet)

urlpatterns = [path('', include(router.urls))]
