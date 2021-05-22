"""ikrta URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from accounts import views as account_views
from pictures import views as pictures_views
from regions import views as regions_views
from uploads import views as uploads_views
from waffle_featureflags import views as waffle_featureflags_views
from waffle_protected_drf.routers import WaffleProtectedDefaultRouter


router = WaffleProtectedDefaultRouter()
router.register('auth', account_views.AuthViewSet, basename='auth')
router.register('featureflags', waffle_featureflags_views.FeatureFlagsViewSet,
                basename='featureflags')
router.register('file_upload', uploads_views.FileUploadViewSet)
router.register('picture', pictures_views.PictureUploadViewSet)
router.register('regions/federal_district', regions_views.FederalDistrictViewSet)
router.register('regions/federal_subject', regions_views.FederalSubjectViewSet)
router.register('users', account_views.UserViewSet)

api_urls = router.urls

app_name = 'gisp'
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^redactor/', include('redactor.urls')),
    url('', include((api_urls, app_name), namespace='api')),
]

if settings.DEBUG and '://' not in settings.MEDIA_URL:

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:  # pragma: no cover
    import debug_toolbar  # noqa: WPS433
    from django.conf.urls.static import static  # noqa: WPS433

    urlpatterns = [
        # URLs specific only to django-debug-toolbar:
        path('__debug__/', include(debug_toolbar.urls)),  # noqa: DJ05
    ] + urlpatterns
