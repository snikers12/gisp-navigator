from django.http import Http404, HttpResponse, HttpResponseNotFound
from functools import wraps
from rest_framework.renderers import JSONRenderer

from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedMixin

from waffle_protected_drf import is_drf_browsable_api_allowed


def _waffle_protected_view_wrapper(view):
    @wraps(view)
    def new_view(request, *args, **kwargs):
        if not is_drf_browsable_api_allowed(request):
            return HttpResponseNotFound('{}', content_type=JSONRenderer.media_type)
        return view(request, *args, **kwargs)

    return new_view


class WaffleProtectedDefaultRouter(DefaultRouter):
    def get_schema_root_view(self, api_urls=None):
        return _waffle_protected_view_wrapper(super().get_schema_root_view(api_urls))

    def get_api_root_view(self, api_urls=None):
        return _waffle_protected_view_wrapper(super().get_api_root_view(api_urls))


class WaffleProtectedNestedDefaultRouter(NestedMixin, WaffleProtectedDefaultRouter):
    pass
