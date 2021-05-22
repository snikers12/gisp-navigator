from regions.open_api.views import FederalSubjectViewSet
from waffle_protected_drf.routers import WaffleProtectedDefaultRouter

regions_router_for_open_api = WaffleProtectedDefaultRouter()
regions_router_for_open_api.register('v1/regions', FederalSubjectViewSet)

regions_open_api_urls = regions_router_for_open_api.urls
