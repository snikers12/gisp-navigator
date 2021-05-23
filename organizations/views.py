from django.db.models import Count, Q
from rest_framework import mixins, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from organizations.models import SupportMeasures, OrganizationCorrelation, Subsidies, Coefficients
from organizations.serializers import SupportMeasuresSerializer, SupportMeasuresListSerializer


class SupportMeasureViewSet(mixins.ListModelMixin,
                            mixins.RetrieveModelMixin,
                            viewsets.GenericViewSet):
    queryset = SupportMeasures.objects.all().annotate(
        count=Count('subsidies')
    ).order_by('-count')
    serializer_class = SupportMeasuresSerializer
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action == 'list':
            return SupportMeasuresListSerializer
        return self.serializer_class

    @action(detail=False, methods=['GET'], permission_classes=[permissions.AllowAny])
    def top(self, request, *args, **kwargs):
        qs = self.get_queryset()[:4]
        data = SupportMeasuresSerializer(qs, many=True).data
        return Response(data)

    @action(detail=False, methods=['GET'], permission_classes=[permissions.AllowAny])
    def recommended(self, request, *args, **kwargs):
        inn = request.GET.get('inn', '')
        if not inn:
            return self.top(request, args, kwargs)
        org_correlations = OrganizationCorrelation.objects.filter(
            correlation__gte=Coefficients.objects.first().similarity_coefficient
        ).order_by('-correlation').values_list('org_2__id', flat=True)
        recommended_org_ids = []
        recommended_org_ids += list(
            org_correlations.filter(org_1__inn=inn).values_list('org_2__id', flat=True)
        )
        recommended_org_ids += list(
            org_correlations.filter(org_2__inn=inn).values_list('org_1__id', flat=True)
        )
        support_measures_ids = Subsidies.objects.filter(
            organization__in=recommended_org_ids
        ).values_list('support_measure', flat=True)
        support_measures = SupportMeasures.objects.filter(id__in=support_measures_ids)
        data = SupportMeasuresListSerializer(support_measures, many=True).data
        return Response(data)

