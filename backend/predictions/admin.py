from django.contrib import admin
from .models import LaptopPrediction, SmartphonePrediction, Listing, Conversation, Message


@admin.register(LaptopPrediction)
class LaptopPredictionAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'brand', 'model', 'launch_year',
        'predicted_price', 'confidence_score', 'created_at'
    ]
    list_filter = ['brand', 'condition', 'created_at']
    search_fields = ['brand', 'model', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Basic Information', {
            'fields': ('brand', 'model', 'launch_year', 'launch_price')
        }),
        ('Hardware Specifications', {
            'fields': (
                'processor', 'ram', 'storage_type', 'storage_size',
                'gpu', 'screen_size'
            )
        }),
        ('Condition & Usage', {
            'fields': ('battery_cycle_count', 'condition', 'warranty_remaining')
        }),
        ('Location', {
            'fields': ('seller_location',)
        }),
        ('Prediction Results', {
            'fields': ('predicted_price', 'confidence_score')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SmartphonePrediction)
class SmartphonePredictionAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'brand', 'model', 'launch_year',
        'supports_5g', 'predicted_price', 'confidence_score', 'created_at'
    ]
    list_filter = ['brand', 'condition', 'supports_5g', 'created_at']
    search_fields = ['brand', 'model', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Basic Information', {
            'fields': ('brand', 'model', 'launch_year', 'launch_price', 'supports_5g')
        }),
        ('Hardware Specifications', {
            'fields': (
                'processor', 'ram', 'storage', 'battery_capacity', 'battery_health',
                'screen_size', 'display_type', 'camera_mp', 'camera_front_mp'
            )
        }),
        ('Condition & Usage', {
            'fields': (
                'condition', 'warranty_remaining', 'screen_cracked',
                'body_damage', 'accessories'
            )
        }),
        ('Location', {
            'fields': ('seller_type', 'seller_location',)
        }),
        ('Prediction Results', {
            'fields': ('predicted_price', 'confidence_score')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'buyer', 'seller', 'listing', 'created_at', 'last_message_at']
    list_filter = ['created_at', 'last_message_at']
    search_fields = ['buyer__email', 'seller__email', 'listing__id']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'conversation', 'sender', 'content_preview', 'created_at', 'is_read']
    list_filter = ['is_read', 'created_at']
    search_fields = ['sender__email', 'content']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'

