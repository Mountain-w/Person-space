from django.contrib import admin
from dynamic.models import Dynamic
# Register your models here.

@admin.register(Dynamic)
class DynamicAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = (
        'created_at',
        'user',
        'content',
    )