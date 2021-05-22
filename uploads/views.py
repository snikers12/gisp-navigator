from rest_framework import mixins, viewsets
from rest_framework.parsers import MultiPartParser, FileUploadParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.request import Request

from . import serializers
from .models import FileUpload


class FileUploadViewSet(mixins.CreateModelMixin,
                        viewsets.GenericViewSet, ):
    """
    Accepts multipart form with the only field called `file`, or a raw body, like this:
    ```
    curl \
      -X PUT \
      -H "Authorization: Token 50152a5d7af1fab20a87744e2024b2a110916edc" \
      -H "Content-Disposition: attachment; filename=filename.jpg" \
      --data-binary @"/Downloads/tsjh.jpg" \
      http://127.0.0.1:8000/file_upload/
    ```
    """
    queryset = FileUpload.objects.none()
    serializer_class = serializers.FileUploadSerializer
    permission_classes = (AllowAny,)
    parser_classes = (MultiPartParser, FileUploadParser)

    def put(self, request: Request, **kwargs):
        # Raw body contents are stored in `request.data['file']`.
        # Multipart form fields are also stored in `request.data`.
        # We use `file` field name for multipart form, thus the file is always
        # stored in the `request.data['file']` regardless
        # of content encoding (raw body/multipart form).
        # Hence we can simply use the POST logic here w/o any modifications.
        return super().create(request)

    def get_object(self):  # pragma: no cover
        """
        Fixes `OPTIONS`: the default one raises AssertionError.
        # See rest_framework.generics.GenericAPIView#get_object
        :return:
        """
        return None
