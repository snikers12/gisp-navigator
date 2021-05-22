import uuid

from stdimage.utils import UploadTo


class UploadToClassNameDirUUIDDirOriginalFileName(UploadTo):
    path_pattern = '%(class_name)s/%(path)s'

    def __call__(self, instance, filename):
        self.kwargs.update({
            'path': uuid.uuid4().hex,
        })
        return super().__call__(instance, filename)
