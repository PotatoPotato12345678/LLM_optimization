from django.contrib import admin
from .models import OptimizedShift
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

@admin.register(OptimizedShift)
class OptimizedShiftAdmin(admin.ModelAdmin):
    list_display = ('shift', 'year', 'month')
    search_fields = ('year', 'month')    
