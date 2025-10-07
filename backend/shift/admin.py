from django.contrib import admin
from .models import ShiftRequirement, User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

@admin.register(ShiftRequirement)
class ShiftRequirementAdmin(admin.ModelAdmin):
    list_display = ('employee', 'content')
    search_fields = ('content', 'employee__username')
