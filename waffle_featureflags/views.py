from django.conf import settings
from rest_framework import mixins, viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import waffle

waffle_type_to_getter = {
    'flag': lambda name, request: waffle.flag_is_active(request, name),
    'switch': lambda name, request: waffle.switch_is_active(name),
    'sample': lambda name, request: waffle.sample_is_active(name),
}


class FeatureFlagsViewSet(mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    queryset = None
    permission_classes = (AllowAny,)

    def list(self, request, *args, **kwargs):
        return Response(self._generate_featureflags(), status=status.HTTP_200_OK)

    def _generate_featureflags(self):
        expose = getattr(settings, 'WAFFLE_FEATUREFLAGS_EXPOSE', [])
        return {name: waffle_type_to_getter[waffle_type](name, self.request)
                for waffle_type, name in expose
                if waffle_type in waffle_type_to_getter}
