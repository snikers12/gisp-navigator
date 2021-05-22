import waffle


def is_geocoder_disabled(request):
    return waffle.flag_is_active(request, 'geocoder_disabled')
