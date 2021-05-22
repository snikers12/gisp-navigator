from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from pictures.models import Picture


def get_raw_image(width=800, height=600, color=0, mime_format='jpeg'):
    im_size = (width, height)  # WxH
    color = color  # 0 is black

    # http://pillow.readthedocs.io/en/3.1.x/reference/Image.html#PIL.Image.new
    im = Image.new('RGB', im_size, color)
    im_file = BytesIO()
    im.save(im_file, mime_format)
    im_file.seek(0)
    size = len(im_file.read())
    im_file.seek(0)
    return im_file, size


def get_image_file(mime_format='jpeg', **kwargs):
    im_file, _ = get_raw_image(**kwargs, mime_format=mime_format)

    # http://www.freeformatter.com/mime-types-list.html
    image_input = SimpleUploadedFile(f"img.{mime_format}", im_file.read(),
                                     content_type=f"image/{mime_format}")
    return image_input


def create_test_picture() -> Picture:
    return Picture.objects.create(image=get_image_file())
