from rest_framework.negotiation import DefaultContentNegotiation
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer

from waffle_protected_drf import is_drf_browsable_api_allowed


class WaffleContentNegotiation(DefaultContentNegotiation):
    """
    Disables DRF Browsable API when the waffle flag is disabled.

    Tom Christie suggests to not do that:
      https://stackoverflow.com/a/13156314
    but still, Browsable API makes FK relations leak:
      https://github.com/encode/django-rest-framework/issues/3905
    so this looks like a reasonable work-around.
    """

    def select_renderer(self, request, renderers, format_suffix=None):
        renderer, media_type = super().select_renderer(request, renderers, format_suffix)
        if isinstance(renderer, BrowsableAPIRenderer) and not is_drf_browsable_api_allowed(request):
            renderer, media_type = super().select_renderer(request, renderers,
                                                           format_suffix=JSONRenderer.format)
            assert isinstance(renderer, JSONRenderer)
        return renderer, media_type
