from django.contrib import admin
from .models import ShiftRequirement, ManagerRequirement, User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

@admin.register(ShiftRequirement)
class ShiftRequirementAdmin(admin.ModelAdmin):
    list_display = ('employee', 'content')
    search_fields = ('content', 'employee__username')
@admin.register(ManagerRequirement)
class ManagerRequirementAdmin(admin.ModelAdmin):
    list_display = ('hard_rule', 'content')
    search_fields = ('content', 'manager_username',)
