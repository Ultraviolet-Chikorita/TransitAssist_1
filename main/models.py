from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

class CustomUser(AbstractUser):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone_number = PhoneNumberField(blank=True)

    def __str__(self):
        return self.username

class userPreferences(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="preferences")
    floors = models.BooleanField(default=False)
    wheels = models.BooleanField(default=False)
    animals = models.BooleanField(default=False)
    braille = models.BooleanField(default=False)
    elevators = models.BooleanField(default=False)

    def __str__(self):
        returnvals = []
        if self.floors:
            returnvals.append("Low Floor Buses")
        if self.wheels:
            returnvals.append("Wheelchair Ramps and Lifts")
        if self.animals:
            returnvals.append("Service Animal Friendly")
        if self.braille:
            returnvals.append("Braille and Large Print Signage")
        if self.elevators:
            returnvals.append("Elevators and Escalators")
        returnval = "Priorities for user " + str(self.user) + ": "
        if len(returnvals) == 0:
            returnval += "NONE"
        elif len(returnvals) == 1:
            returnval += returnvals[0]
        else:
            returnval += ", ".join(returnvals[:-1])
            returnval += " and " + returnvals[-1]
        return returnval

class userMapSettings(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="mapsettings")
    challenge = models.BooleanField(default=False)
    accessibility = models.BooleanField(default=False)
    autosave = models.BooleanField(default=False)

    def __str__(self):
        returnvals = []
        if self.challenge:
            returnvals.append("Show areas of potential challenge in red")
        if self.accessibility:
            returnvals.append("Prioritize accessibility over time")
        if self.autosave:
            returnvals.append("Auto-save each route to your history")
        returnval = "Map settings for user " + str(self.user) + ": "
        if len(returnvals) == 0:
            returnval += "NONE"
        elif len(returnvals) == 1:
            returnval += returnvals[0]
        else:
            returnval += ", ".join(returnvals[:-1]) + " and " + returnvals[-1]
        return returnval


class userRoutes(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="routes")
    start = models.CharField(max_length=1023)
    end = models.CharField(max_length=1023)
    time = models.DateTimeField(auto_now_add=True, blank=True)
    saved = models.BooleanField(default=False)

    def __str__(self):
        returnval = self.user.username + ": Route from " + self.start + " to " + self.end + " at " + self.time.strftime("%d/%m/%Y")
        if self.saved:
            returnval = "SAVED ||||| " + returnval
        if self.saved == False:
            returnval += " NOT SAVED"
        return returnval

class accessibilityIssues(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="issues")
    place_id = models.CharField(max_length=5095)
    issue = models.CharField(max_length=511)

    def __str__(self):
        return self.user.username + ": " + self.place_id + ", issue '" + self.issue + "'"

class goodAccessibility(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="good")
    place_id = models.CharField(max_length=5095)
    good = models.CharField(max_length=511)

    def __str__(self):
        return self.user.username + ": " + self.place_id + ", good thing '" + self.good + "'"