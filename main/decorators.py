# Get GPS Location
def get_gps_location(function):
    def wrap(request, *args, **kwargs):
        lat = request.data.get('lat', 0.0)
        lng = request.data.get('lng', 0.0)
        if lat != 0.0 and lng != 0.0:
            request.user.latitude = lat
            request.user.longitude = lng
            request.user.save()
        return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
