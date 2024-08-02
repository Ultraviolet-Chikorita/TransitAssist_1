
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser, userPreferences, userMapSettings, userRoutes, accessibilityIssues, goodAccessibility

class UserAdmin(BaseUserAdmin):
    ordering = ('email',)
    list_display = ['username', 'email', 'first_name', 'last_name', 'phone_number']


admin.site.register(CustomUser, UserAdmin)

admin.site.register(userPreferences)
admin.site.register(userMapSettings)
admin.site.register(userRoutes)
admin.site.register(accessibilityIssues)
admin.site.register(goodAccessibility)