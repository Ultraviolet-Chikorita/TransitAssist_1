from django.conf import settings


def external_api_settings(_request):
    """Expose public browser-side API configuration to templates.

    Values still need provider-side origin/API restrictions because any browser
    JavaScript key is visible to users by design.
    """
    return {
        "GOOGLE_MAPS_API_KEY": settings.GOOGLE_MAPS_API_KEY,
    }
