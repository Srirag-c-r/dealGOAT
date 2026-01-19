from django.contrib import admin
from .models import RequirementQuery, ProductResult

@admin.register(RequirementQuery)
class RequirementQueryAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'requirements_text']
    search_fields = ['user__username', 'requirements_text']
    list_filter = ['created_at']

@admin.register(ProductResult)
class ProductResultAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'rank', 'price', 'match_score', 'rating']
    search_fields = ['product_name', 'brand']
    list_filter = ['rank', 'match_score', 'rating']
