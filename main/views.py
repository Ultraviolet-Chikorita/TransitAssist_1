import json

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from phonenumber_field.phonenumber import PhoneNumber

from .models import (
    accessibilityIssues,
    goodAccessibility,
    userMapSettings,
    userPreferences,
    userRoutes,
)


def _preferences_for(user):
    preferences, _ = userPreferences.objects.get_or_create(user=user)
    return preferences


def _map_settings_for(user):
    settings, _ = userMapSettings.objects.get_or_create(user=user)
    return settings


def _json_payload(request):
    try:
        return json.loads(request.body or b"{}")
    except (TypeError, ValueError, json.JSONDecodeError):
        return None


def login(request):
    if request.method == "GET":
        return render(request, "signin.html")
    if request.method != "POST":
        return JsonResponse({"status": "Fail", "msg": "Method not allowed"}, status=405)

    email = request.POST.get("email", "")
    password = request.POST.get("password", "")
    user = authenticate(request, username=email, password=password)
    if user is not None:
        auth_login(request, user)
        return redirect("home")
    return redirect("login")


def signup(request):
    if request.method == "GET":
        return render(request, "signup.html")
    if request.method != "POST":
        return JsonResponse({"status": "Fail", "msg": "Method not allowed"}, status=405)

    firstname = request.POST.get("firstname", "").strip()
    lastname = request.POST.get("lastname", "").strip()
    email = request.POST.get("email", "").strip()
    password = request.POST.get("password", "")
    if not email or not password:
        return render(request, "signup.html", {"error": "Email and password are required."}, status=400)

    CustomUser = get_user_model()
    if CustomUser.objects.filter(username=email).exists():
        return render(request, "signup.html", {"error": "An account already exists for this email."}, status=400)

    user = CustomUser.objects.create_user(
        username=email,
        email=email,
        password=password,
        first_name=firstname,
        last_name=lastname,
    )
    _preferences_for(user)
    _map_settings_for(user)
    return redirect("login")


@login_required
@require_POST
def get_saved_routes(request):
    saved_routes = request.user.routes.filter(saved=True).order_by("-time")
    routes = [
        {
            "id": route.id,
            "start": route.start,
            "end": route.end,
            "date": route.time.strftime("%d/%m/%Y"),
        }
        for route in saved_routes
    ]
    return JsonResponse({"status": "OK", "routes": routes})


@login_required
@require_POST
def update_user_details(request):
    data = _json_payload(request)
    if data is None:
        return JsonResponse({"status": "Fail", "msg": "Invalid JSON"}, status=400)

    try:
        phone = PhoneNumber.from_string(data.get("phonenumber"))
    except Exception:
        return JsonResponse(
            {"status": "Fail", "msg": "Phone number invalid, please use international format"},
            status=400,
        )

    request.user.first_name = (data.get("firstname") or "").strip()
    request.user.last_name = (data.get("lastname") or "").strip()
    request.user.phone_number = phone
    request.user.save(update_fields=["first_name", "last_name", "phone_number"])
    return JsonResponse({"status": "OK"})


@login_required
@require_POST
def check_completed_profile(request):
    user = request.user
    complete = bool(user.first_name and user.last_name and user.email and user.phone_number)
    return JsonResponse({"status": complete})


@login_required
@require_POST
def update_user_prefs(request):
    data = _json_payload(request)
    if data is None:
        return JsonResponse({"status": "Fail", "msg": "Invalid JSON"}, status=400)

    prefs = _preferences_for(request.user)
    prefs.floors = bool(data.get("lowfloorbuses"))
    prefs.wheels = bool(data.get("wheelchair"))
    prefs.animals = bool(data.get("serviceanimal"))
    prefs.braille = bool(data.get("braille"))
    prefs.elevators = bool(data.get("elevators"))
    prefs.save()
    return JsonResponse({"status": "OK"})


@login_required
@require_POST
def save_route(request):
    data = _json_payload(request)
    if data is None:
        return JsonResponse({"status": "Fail", "msg": "Invalid JSON"}, status=400)

    start = (data.get("start") or "").strip()
    end = (data.get("end") or "").strip()
    if not start or not end:
        return JsonResponse({"status": "Fail", "msg": "Start and end are required"}, status=400)

    route = userRoutes.objects.create(
        user=request.user,
        start=start,
        end=end,
        saved=_map_settings_for(request.user).autosave,
    )
    return JsonResponse({"status": "OK", "id": route.id})


@login_required
@require_POST
def update_user_mapsettings(request):
    data = _json_payload(request)
    if data is None:
        return JsonResponse({"status": "Fail", "msg": "Invalid JSON"}, status=400)

    map_settings = _map_settings_for(request.user)
    map_settings.challenge = bool(data.get("challenge"))
    map_settings.accessibility = bool(data.get("accessibility"))
    map_settings.autosave = bool(data.get("autosave"))
    map_settings.save()
    return JsonResponse({"status": "OK"})


@login_required
@require_POST
def add_issue(request):
    data = _json_payload(request)
    places = data.get("places") if data else None
    issue = (data.get("issue") or "").strip() if data else ""
    if not isinstance(places, list) or not issue:
        return JsonResponse({"status": "Fail", "msg": "Places and issue are required"}, status=400)

    for place in {str(place).strip() for place in places if str(place).strip()}:
        accessibilityIssues.objects.get_or_create(
            user=request.user,
            place_id=place,
            issue=issue,
        )
    return JsonResponse({"status": "OK"})


@login_required
@require_POST
def add_good(request):
    data = _json_payload(request)
    places = data.get("places") if data else None
    good = (data.get("good") or "").strip() if data else ""
    if not isinstance(places, list) or not good:
        return JsonResponse({"status": "Fail", "msg": "Places and accessibility feature are required"}, status=400)

    for place in {str(place).strip() for place in places if str(place).strip()}:
        goodAccessibility.objects.get_or_create(
            user=request.user,
            place_id=place,
            good=good,
        )
    return JsonResponse({"status": "OK"})


@login_required
@require_POST
def get_issues(request):
    data = _json_payload(request)
    places = data.get("places") if data else None
    if not isinstance(places, list):
        return JsonResponse({"status": "Fail", "msg": "Places must be a list"}, status=400)

    issue_counts = {}
    for place in dict.fromkeys(str(place) for place in places):
        for issue in accessibilityIssues.objects.filter(place_id=place).values_list("issue", flat=True):
            issue_counts[issue] = issue_counts.get(issue, 0) + 1
    return JsonResponse({"status": "OK", "data": [[key, value] for key, value in issue_counts.items()]})


@login_required
@require_POST
def get_goods(request):
    data = _json_payload(request)
    places = data.get("places") if data else None
    if not isinstance(places, list):
        return JsonResponse({"status": "Fail", "msg": "Places must be a list"}, status=400)

    prefs = _preferences_for(request.user)
    preferred_features = set()
    if prefs.floors:
        preferred_features.add("Low Floor Buses")
    if prefs.wheels:
        preferred_features.add("Wheelchair Ramps and Lifts")
    if prefs.animals:
        preferred_features.add("Service Animal Friendly")
    if prefs.braille:
        preferred_features.add("Braille and Large Print Signage")
    if prefs.elevators:
        preferred_features.add("Elevators and Escalators")

    good_counts = {}
    for place in dict.fromkeys(str(place) for place in places):
        for good in goodAccessibility.objects.filter(place_id=place).values_list("good", flat=True):
            if good in preferred_features:
                good_counts[good] = good_counts.get(good, 0) + 1
    return JsonResponse({"status": "OK", "data": [[key, value] for key, value in good_counts.items()]})


@login_required
@require_POST
def get_map_settings(request):
    map_settings = _map_settings_for(request.user)
    return JsonResponse(
        {
            "status": "OK",
            "challenge": map_settings.challenge,
            "accessibility": map_settings.accessibility,
            "autosave": map_settings.autosave,
        }
    )


@login_required
def navigate(request):
    return render(request, "navigate.html")


@login_required
@require_POST
def mark_route_as_saved(request):
    data = _json_payload(request)
    route_id = data.get("id") if data else None
    if route_id is None:
        return JsonResponse({"status": "Fail", "msg": "Route id is required"}, status=400)

    route = get_object_or_404(userRoutes, id=route_id, user=request.user)
    route.saved = True
    route.save(update_fields=["saved"])
    return JsonResponse({"status": "OK"})


def home(request):
    if not request.user.is_authenticated:
        return render(request, "home.html")

    user = request.user
    prefs = _preferences_for(user)
    map_settings = _map_settings_for(user)
    saved_routes = user.routes.filter(saved=True).order_by("-time")
    processed_saved_routes = [
        {
            "id": route.id,
            "start": route.start,
            "end": route.end,
            "date": route.time.strftime("%d/%m/%Y"),
        }
        for route in saved_routes
    ]

    unsaved_route = user.routes.filter(saved=False).order_by("-time").first()
    processed_route = (
        {
            "id": unsaved_route.id,
            "start": unsaved_route.start,
            "end": unsaved_route.end,
            "date": unsaved_route.time.strftime("%d/%m/%Y"),
        }
        if unsaved_route
        else {"start": ""}
    )

    return render(
        request,
        "dashloggedin.html",
        {
            "route": processed_route,
            "savedroutes": processed_saved_routes,
            "firstname": user.first_name,
            "lastname": user.last_name,
            "phone": user.phone_number,
            "email": user.email,
            "floors": prefs.floors,
            "wheels": prefs.wheels,
            "animals": prefs.animals,
            "braille": prefs.braille,
            "elevators": prefs.elevators,
            "challenge": map_settings.challenge,
            "accessibility": map_settings.accessibility,
            "autosave": map_settings.autosave,
        },
    )


def home_about(request):
    return render(request, "about.html")


def home_contact(request):
    return render(request, "contact.html")
