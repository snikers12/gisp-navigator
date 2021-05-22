from logging import getLogger

from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from gisp.cache import ListSqlNamedKeyConstructor, controlled_cache_response
from .models import FederalSubject, FederalDistrict
from .serializers import (
    FederalSubjectSerializer,
    FederalDistrictSerializer,
)

logger = getLogger(__name__)


class FederalSubjectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FederalSubject.objects.all()
    serializer_class = FederalSubjectSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filterset_fields = ('name',)
    search_fields = ('name', 'system_name')

    @controlled_cache_response(60 * 30, cache_errors=False,
                               key_func=ListSqlNamedKeyConstructor('region-list'))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @controlled_cache_response(60 * 30, cache_errors=False,
                               key_func=ListSqlNamedKeyConstructor('region-top'))
    @action(detail=False, methods=['GET'])
    def top(self, request):
        qs = FederalSubject.objects.annotate(
            cnt=Count('applications_ul_region')
        ).filter(cnt__gt=0).order_by('cnt')[:20]

        if qs.count() < 20:
            qs = FederalSubject.objects.all()[:20]

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class FederalDistrictViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FederalDistrict.objects.all()
    serializer_class = FederalDistrictSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_fields = ('name',)
    search_fields = ('name', 'name_short')

    @controlled_cache_response(60 * 30, cache_errors=False,
                               key_func=ListSqlNamedKeyConstructor('district-list'))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
