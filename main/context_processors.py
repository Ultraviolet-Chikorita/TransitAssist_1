from django.conf import settings


def external_api_settings(_request):
    """Expose browser-side map API configuration to templates.

    Browser API keys are visible to users by design, so deployments must also
    restrict them by allowed origins and enabled APIs at the provider level.
    """
    return {
        "GOOGLE_MAPS_API_KEY": settings.GOOGLE_MAPS_API_KEY,
        "GEOAPIFY_API_KEY": settings.GEOAPIFY_API_KEY,
    }
