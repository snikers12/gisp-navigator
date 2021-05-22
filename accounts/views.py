from django.contrib.auth import get_user_model, authenticate, login, logout
from django.http import HttpRequest as DjangoHttpRequest
from rest_framework import mixins, viewsets, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request as RestFrameworkRequest
from rest_framework.response import Response

from accounts import serializers
from gisp.pagination import PageNumberPaginationWithQueryParams

User = get_user_model()


class UserViewSet(mixins.CreateModelMixin,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    """
    Текущий юзер: `me/`
    """
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    search_fields = ('username',)
    pagination_class = PageNumberPaginationWithQueryParams

    def dispatch(self, request: DjangoHttpRequest, *args, **kwargs):
        assert isinstance(request, DjangoHttpRequest)
        request = self.initialize_request(request, *args, **kwargs)
        assert isinstance(request, RestFrameworkRequest)
        try:
            self.perform_authentication(request)
            if kwargs.get('pk') == 'me' and request.user.is_authenticated:
                kwargs['pk'] = str(request.user.pk)
        except AuthenticationFailed:
            # possibly due to a bad auth token - do nothing
            assert not request.user.is_authenticated
        return super().dispatch(request._request, *args, **kwargs)

    def get_serializer_class(self):
        return super().get_serializer_class()

    def get_success_headers(self, data):
        token, _ = Token.objects.get_or_create(user_id=data['id'])
        return {'Token': token.key}


class AuthViewSet(mixins.ListModelMixin,  # Simply for web UI
                  viewsets.GenericViewSet):
    """
    Авторизоваться: `POST login/`

    Вход через Добровольцев: `POST volunteer/`

    Разлогиниться: `POST logout/`
    """
    queryset = User.objects.none()
    serializer_class = serializers.UserSerializer

    def get_headers(self, data):
        token, _ = Token.objects.get_or_create(user_id=data['id'])
        return {'Token': token.key}

    @action(detail=False, methods=['GET'], permission_classes=(permissions.IsAuthenticated,))
    def me(self, request):  # todo maybe remove this? this seems to be unused
        serializer = self.get_serializer(instance=request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], permission_classes=(permissions.AllowAny,))
    def login(self, request):
        username = request.data.get('username', '').lower()
        if '@' not in username and username.startswith('8'):
            username = f'+7{username[1:]}'
        password = request.data.get('password')
        user = authenticate(email_or_phone=username, password=password)
        return self._login(request, user)

    def _login(self, request, user):
        if user is None:
            message = 'Введены неверные данные'
            return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)

        login(request, user)
        serializer = self.get_serializer(instance=user)
        headers = self.get_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)

    @action(detail=False, methods=['POST'])
    def logout(self, request):
        # There can be at most one token per user
        Token.objects.filter(user=request.user).delete()
        logout(request)
        return Response({'status': 'Logged out'}, status=status.HTTP_200_OK)
