from .models import userMapSettings, userPreferences
from django.contrib.auth import get_user_model
import logging

# Configure logging
logger = logging.getLogger(__name__)

def save_user_details(backend, user, response, *args, **kwargs):
    # Ensure we only get the details if the backend is GitHub
    if backend.name == 'github':
        CustomUser = get_user_model()
        filtered = CustomUser.objects.filter(username=user.username)
        if not filtered:
            email = response.get('email')

            if email:
                user.email = email
            user.save()
            
            currUser = CustomUser.objects.latest('id')
            matching = currUser.preferences.all()
            if len(matching) == 0:
                prefs = userPreferences(user=currUser)
                prefs.save()
            matching = currUser.mapsettings.all()
            if len(matching) == 0:
                mapsettings = userMapSettings(user=currUser)
                mapsettings.save()
