from django.db.models import Case, When, F, Value
from django.db.models.functions import Concat
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter

from regions.models import FederalSubject
from regions.open_api.serializers import OpenApiFederalSubjectSerializer
from gisp.cache import controlled_cache_response, ListSqlNamedKeyConstructor
from gisp.filters import VolunteersSearchFilter


class FederalSubjectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FederalSubject.objects.all()
    serializer_class = OpenApiFederalSubjectSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend, VolunteersSearchFilter, OrderingFilter)
    filterset_fields = ('name', )
    search_fields = ('name', 'system_name')

    @controlled_cache_response(60 * 30, cache_errors=False,
                               key_func=ListSqlNamedKeyConstructor('region-list'))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
