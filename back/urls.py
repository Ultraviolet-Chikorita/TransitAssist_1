"""
URL configuration for back project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from main import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout', auth_views.LogoutView.as_view(), name='logout'),
    path('social-auth/', include('social_django.urls', namespace='social')),
    path("", views.home, name='home'),
    path("update-user-details/", views.update_user_details, name="update-user-details"),
    path("update-user-prefs/", views.update_user_prefs, name="update-user-prefs"),
    path("update-user-mapsettings/", views.update_user_mapsettings, name="update-user-mapsettings"),
    path("check-completed-profile/", views.check_completed_profile, name="check-completed-profile"),
    path("add-issue/", views.add_issue, name="add-issue"),
    path("get-issues/", views.get_issues, name="get-issues"),
    path("add-good/", views.add_good, name="add-good"),
    path("get-goods/", views.get_goods, name="get-goods"),
    path("save-route/", views.save_route, name="save-route"),
    path("get-map-settings/", views.get_map_settings, name="get-map-settings"),
    path("home-about/", views.home_about, name="home-about"),
    path("home-contact/", views.home_contact, name="home-contact"),
]
