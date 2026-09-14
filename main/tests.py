import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import accessibilityIssues, userMapSettings, userPreferences, userRoutes


class TransitAssistApiTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="user@example.com",
            email="user@example.com",
            password="password123",
            first_name="Test",
            last_name="User",
        )
        self.other_user = User.objects.create_user(
            username="other@example.com",
            email="other@example.com",
            password="password123",
            first_name="Other",
            last_name="User",
        )
        userPreferences.objects.create(user=self.user)
        userMapSettings.objects.create(user=self.user)
        userPreferences.objects.create(user=self.other_user)
        userMapSettings.objects.create(user=self.other_user)

    def post_json(self, name, payload):
        return self.client.post(
            reverse(name),
            data=json.dumps(payload),
            content_type="application/json",
        )

    def test_authenticated_api_redirects_anonymous_users(self):
        response = self.post_json("update-user-prefs", {"wheelchair": True})
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_user_cannot_save_another_users_route(self):
        route = userRoutes.objects.create(
            user=self.other_user,
            start="A",
            end="B",
        )
        self.client.force_login(self.user)

        response = self.post_json("mark-route-as-saved", {"id": route.id})

        self.assertEqual(response.status_code, 404)
        route.refresh_from_db()
        self.assertFalse(route.saved)

    def test_user_can_save_own_route(self):
        route = userRoutes.objects.create(user=self.user, start="A", end="B")
        self.client.force_login(self.user)

        response = self.post_json("mark-route-as-saved", {"id": route.id})

        self.assertEqual(response.status_code, 200)
        route.refresh_from_db()
        self.assertTrue(route.saved)

    def test_report_submission_is_deduplicated_per_user_and_place(self):
        self.client.force_login(self.user)
        payload = {"places": ["place-1", "place-1"], "issue": "Lift unavailable"}

        first = self.post_json("add-issue", payload)
        second = self.post_json("add-issue", payload)

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(
            accessibilityIssues.objects.filter(
                user=self.user,
                place_id="place-1",
                issue="Lift unavailable",
            ).count(),
            1,
        )

    def test_autosave_setting_is_applied_when_route_is_created(self):
        settings = self.user.mapsettings.get()
        settings.autosave = True
        settings.save(update_fields=["autosave"])
        self.client.force_login(self.user)

        response = self.post_json("save-route", {"start": "A", "end": "B"})

        self.assertEqual(response.status_code, 200)
        route = self.user.routes.get(id=response.json()["id"])
        self.assertTrue(route.saved)

    def test_signup_creates_companion_preference_records(self):
        response = self.client.post(
            reverse("signup"),
            {
                "firstname": "New",
                "lastname": "Person",
                "email": "new@example.com",
                "password": "password123",
            },
        )

        self.assertEqual(response.status_code, 302)
        user = get_user_model().objects.get(username="new@example.com")
        self.assertTrue(user.preferences.exists())
        self.assertTrue(user.mapsettings.exists())
