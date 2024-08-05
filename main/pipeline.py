from .models import userMapSettings, userPreferences
from django.contrib.auth import get_user_model
import logging

# Configure logging
logger = logging.getLogger(__name__)

def save_user_details(backend, user, response, *args, **kwargs):
    # Ensure we only get the details if the backend is GitHub
    if backend.name == 'github':
        CustomUser = get_user_model()
        email = response.get('email')

        if email and not user.email:
            user.email = email
            user.save()

        currUser = CustomUser.objects.latest('id')
        if not currUser.preferences.exists():
            prefs = userPreferences(user=currUser)
            prefs.save()
        if not currUser.mapsettings.exists():
            mapsettings = userMapSettings(user=currUser)
            mapsettings.save()
