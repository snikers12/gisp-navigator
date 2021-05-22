from rest_framework import viewsets, mixins
from rest_framework.exceptions import ParseError
from rest_framework.parsers import MultiPartParser, FileUploadParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.request import Request

from pictures.models import Picture
from pictures.serializers import PictureSerializer


class PictureUploadViewSet(mixins.CreateModelMixin,
                           viewsets.GenericViewSet):
    """
    Accepts multipart form with the only field called `image`, or a raw body, like this:

    ```
    curl \
      -X PUT \
      -H "Authorization: Token 50152a5d7af1fab20a87744e2024b2a110916edc" \
      -H "Content-Disposition: attachment; filename=filename.jpg" \
      --data-binary @"/Downloads/tsjh.jpg" \
      http://127.0.0.1:8000/picture/
    ```
    """
    queryset = Picture.objects.all()
    permission_classes = (AllowAny,)
    parser_classes = (MultiPartParser, FileUploadParser)
    serializer_class = PictureSerializer

    def put(self, request: Request, **kwargs):
        """
        1. Allows using PUT instead of just POST for raw-body uploads
        2. Copies raw-body image from `file` to `image`
        :param request:
        :param kwargs:
        :return:
        """
        if 'file' in request.data and 'image' not in request.data:
            # Raw file upload
            request.data['image'] = request.data['file']
            return super().create(request)
        else:
            raise ParseError()

    def get_object(self):  # pragma: no cover
        """
        Fixes `OPTIONS`: the default one raises AssertionError.
        # See rest_framework.generics.GenericAPIView#get_object
        :return:
        """
        return None
