from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from phonenumber_field.phonenumber import PhoneNumber
from django.http import JsonResponse
from .models import userPreferences, userMapSettings, userRoutes, accessibilityIssues, goodAccessibility
import json

# Create your views here.

def login(request): 
    if request.method == "GET":
        return render(request, 'signin.html')
    else:
        email = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(request, username=email, password=password)
        print(user)
        if user is not None:
            auth_login(request, user)
            return redirect('home')
        return redirect('login')


def signup(request):
    if request.method == "GET":
        return render(request, 'signup.html')
    else:
        firstname = request.POST["firstname"]
        lastname = request.POST["lastname"]
        email = request.POST["email"]
        password = request.POST["password"]
        CustomUser = get_user_model()
        user = CustomUser(
            username=email,
            first_name=firstname,
            last_name=lastname,
            email=email
        )
        user.set_password(password)
        user.save()
        currUser = CustomUser.objects.latest('id')
        prefs = userPreferences(user=currUser)
        prefs.save()
        mapsettings = userMapSettings(user=currUser)
        mapsettings.save()
        return redirect('login')

def get_saved_routes(request):
    if request.method == "POST":
        try:
            CustomUser = get_user_model()
            user = CustomUser.objects.filter(id=request.user.id)[0]
            savedRoutes = list(user.routes.filter(saved=True))
            processedSavedRoutes = []
            for route in savedRoutes:
                processedSavedRoutes.append({"start": route.start, "end": route.end, "date": route.time.strftime("%d/%m/%Y")})
            return JsonResponse({"status": "OK", "routes": processedSavedRoutes})
        except:
            return JsonResponse({"Status": "Fail"})


def update_user_details(request):
    if request.method == "POST":
        try:
            data = json.load(request)
            firstname = data.get("firstname")
            lastname = data.get("lastname")
            phone = PhoneNumber.from_string(data.get("phonenumber"))
            CustomUser = get_user_model()
            user = CustomUser.objects.filter(id=request.user.id)[0]
            user.first_name = firstname
            user.last_name = lastname
            user.phone_number = phone
            user.save()
            return JsonResponse({"status": "OK"})
        except Exception as e:
            errorMessage = str(e)
            if errorMessage == "(0) Missing or invalid default region.":
                errorMessage = "Phone number invalid, please use international format"
            return JsonResponse({"status": "Fail", "msg": errorMessage})


def check_completed_profile(request):
    if request.method == "POST":
        CustomUser = get_user_model()
        user = CustomUser.objects.filter(id=request.user.id)[0]
        return JsonResponse({"status": (user.first_name != "" and user.last_name != "" and user.email != "" and user.phone_number != None)})


def update_user_prefs(request):
    if request.method == "POST":
        try:
            data = json.load(request)
            floors = data.get("lowfloorbuses")
            wheels = data.get("wheelchair")
            animals = data.get("serviceanimal")
            braille = data.get("braille")
            elevators = data.get("elevators")
            CustomUser = get_user_model()
            user = CustomUser.objects.filter(id=request.user.id)[0]
            prefs = user.preferences.all()[0]
            prefs.floors = floors
            prefs.wheels = wheels
            prefs.animals = animals
            prefs.braille = braille
            prefs.elevators = elevators
            prefs.save()
            return JsonResponse({"status": "OK"})
        except:
            return JsonResponse({"Status": "Fail"})


def save_route(request):
    if request.method == "POST":
        try:
            data = json.load(request)
            start = data.get("start")
            end = data.get("end")
            CustomUser = get_user_model()
            user = CustomUser.objects.filter(id=request.user.id)[0]
            route = userRoutes(user=user, start=start, end=end)
            if user.mapsettings.all()[0].autosave:
                route.saved = True
            route.save()
            return JsonResponse({"status": "OK"})
        except Exception as e:
            print(e)
            return JsonResponse({"status": "Fail"})


def update_user_mapsettings(request):
    if request.method == "POST":
        data = json.load(request)
        challenge = data.get("challenge")
        accessibility = data.get("accessibility")
        autosave = data.get("autosave")
        CustomUser = get_user_model()
        user = CustomUser.objects.filter(id=request.user.id)[0]
        mapsettings = user.mapsettings.all()[0]
        mapsettings.challenge = challenge
        mapsettings.accessibility = accessibility
        mapsettings.autosave = autosave
        mapsettings.save()
        return JsonResponse({"status": "OK"})


def add_issue(request):
    if request.method == "POST":
        data = json.load(request)
        places = data.get("places")
        issue = data.get("issue")
        CustomUser = get_user_model()
        user = CustomUser.objects.filter(id=request.user.id)[0]
        for place in places:
            matches = user.issues.filter(place_id=place,issue=issue)
            if not matches:
                curr = accessibilityIssues(user=user, place_id=place, issue=issue)
                curr.save()
        return JsonResponse({"status": "OK"})

def add_good(request):
    if request.method == "POST":
        data = json.load(request)
        places = data.get("places")
        good = data.get("good")
        CustomUser = get_user_model()
        user = CustomUser.objects.filter(id=request.user.id)[0]
        for place in places:
            matches = user.good.filter(place_id=place,good=good)
            if not matches:
                curr = goodAccessibility(user=user, place_id=place, good=good)
                curr.save()
        return JsonResponse({"status": "OK"})

def get_issues(request):
    if request.method == "POST":
        data = json.loads(request.body)
        places = data.get("places")
        issueDict = {}
        if len(places) > 1:
            if places[0] == places[1]:
                places = [places[0]]
        for place in places:
            issues = accessibilityIssues.objects.filter(place_id=place).values('issue')
            for issue_dict in issues:
                issue = issue_dict['issue']
                if issue in issueDict:
                    issueDict[issue] += 1
                else:
                    issueDict[issue] = 1
        return JsonResponse({"status": "OK", "data": [[k, v] for k, v in issueDict.items()]})

def get_goods(request):
    if request.method == "POST":
        data = json.loads(request.body)
        places = data.get("places")
        goodDict = {}
        if len(places) > 1:
            if places[0] == places[1]:
                places = [places[0]]
        CustomUser = get_user_model()
        user = CustomUser.objects.filter(id=request.user.id)[0]
        prefs = user.preferences.all()[0]
        prefList = []
        if prefs.floors:
            prefList.append("Low Floor Buses")
        if prefs.wheels:
            prefList.append("Wheelchair Ramps and Lifts")
        if prefs.animals:
            prefList.append("Service Animal Friendly")
        if prefs.braille:
            prefList.append("Braille and Large Print Signage")
        if prefs.elevators:
            prefList.append("Elevators and Escalators")
        print(prefList)
        for place in places:
            goods = goodAccessibility.objects.filter(place_id=place).values('good')
            for good_dict in goods:
                good = good_dict['good']
                print(good)
                if good in prefList:
                    if good in goodDict:
                        goodDict[good] += 1
                    else:
                        goodDict[good] = 1
        return JsonResponse({"status": "OK", "data": [[k, v] for k, v in goodDict.items()]})


def get_map_settings(request):
    if request.method == "POST":
        CustomUser = get_user_model()
        user = CustomUser.objects.filter(id=request.user.id)[0]
        mapsettings = user.mapsettings.all()[0]
        challenge = mapsettings.challenge
        accessibility = mapsettings.accessibility
        autosave = mapsettings.autosave
        return JsonResponse({"status": "OK", "challenge": challenge, "accessibility": accessibility, "autosave": autosave})

def navigate(request):
    if request.user.is_authenticated:
        return render(request, 'navigate.html')
    return redirect('login')

def mark_route_as_saved(request):
    if request.method == "POST":
        data = json.loads(request.body)
        id = data.get("id")
        routeToSave = userRoutes.objects.filter(id=int(id))[0]
        routeToSave.saved = True
        routeToSave.save()
        return JsonResponse({"status": "OK"})


def home(request):
    if request.user.is_authenticated:
        CustomUser = get_user_model()
        user = CustomUser.objects.filter(id=request.user.id)[0]
        firstname = user.first_name
        lastname = user.last_name
        phonenumber = user.phone_number
        email = user.email
        prefs = user.preferences.all()[0]
        floors = prefs.floors
        wheels = prefs.wheels
        animals = prefs.animals
        braille = prefs.braille
        elevators = prefs.elevators
        mapsettings = user.mapsettings.all()[0]
        challenge = mapsettings.challenge
        accessibility = mapsettings.accessibility
        autosave = mapsettings.autosave
        savedRoutes = list(user.routes.filter(saved=True))
        savedRoutes.reverse()
        processedSavedRoutes = []
        for route in savedRoutes:
            processedSavedRoutes.append({"start": route.start, "end": route.end, "date": route.time.strftime("%d/%m/%Y")})
        try:
            unsavedRoute = list(user.routes.filter(saved=False))[-1]
            processedRoute = {"id": unsavedRoute.id, "start": unsavedRoute.start, "end": unsavedRoute.end, "date":unsavedRoute.time.strftime("%d/%m/%Y")}
        except:
            processedRoute = {"start": ""}
        return render(request, "dashloggedin.html", {'route': processedRoute, 'savedroutes': processedSavedRoutes ,'firstname': firstname, 'lastname': lastname, 'phone': phonenumber, 'email': email, 'floors': floors, 'wheels': wheels, 'animals': animals, 'braille': braille, 'elevators': elevators, 'challenge': challenge, 'accessibility': accessibility, 'autosave': autosave})
    return render(request, "home.html")

def home_about(request):
    return render(request, "about.html")

def home_contact(request):
    return render(request, "contact.html")