from django.urls import path
from . import views, admin_views

urlpatterns = [
    # Prediction endpoints
    path('laptop/', views.predict_laptop_price, name='predict_laptop'),
    path('smartphone/', views.predict_smartphone_price, name='predict_smartphone'),
    
    # History and info endpoints
    path('history/', views.get_prediction_history, name='prediction_history'),
    path('model-info/', views.get_model_info, name='model_info'),
    path('specs/', views.get_brands_and_specs, name='brands_specs'),
    path('imei-lookup/', views.check_imei, name='check_imei'),
    
    # Listing endpoints
    path('listings/create/', views.create_listing, name='create_listing'),
    path('listings/my-listings/', views.get_user_listings, name='get_user_listings'),
    path('listings/all/', views.get_active_listings, name='get_active_listings'),
    path('listings/details/<int:pk>/', views.get_listing_details, name='get_listing_details'),
    path('listings/delete/<int:pk>/', views.delete_listing, name='delete_listing'),
    path('listings/status/<int:pk>/', views.update_listing_status, name='update_listing_status'),
    
    # Messaging endpoints
    path('messages/start/<int:listing_id>/', views.start_conversation, name='start_conversation'),
    path('messages/conversations/', views.get_conversations, name='get_conversations'),
    path('messages/conversation/<int:conversation_id>/', views.get_conversation_messages, name='get_conversation_messages'),
    path('messages/read/<int:conversation_id>/', views.mark_messages_read, name='mark_messages_read'),
    
    # Admin endpoints
    path('admin/dashboard/stats/', admin_views.admin_listing_stats, name='admin_listing_stats'),
    path('admin/listings/list/', admin_views.admin_listing_list, name='admin_listing_list'),
    path('admin/listings/pending/', admin_views.admin_pending_listings, name='admin_pending_listings'),
    path('admin/listings/flagged/', admin_views.admin_flagged_listings, name='admin_flagged_listings'),
    path('admin/listings/<int:listing_id>/moderate/', admin_views.admin_moderate_listing, name='admin_moderate_listing'),
    path('admin/listings/fraud-check/', admin_views.admin_fraud_check, name='admin_fraud_check'),
    
    # Admin Analytics - NEW
    path('admin/analytics/trends/', admin_views.admin_prediction_trends, name='admin_prediction_trends'),
    path('admin/analytics/devices/', admin_views.admin_device_popularity, name='admin_device_popularity'),
    path('admin/analytics/price-distribution/', admin_views.admin_price_distribution, name='admin_price_distribution'),
    path('admin/analytics/listings/trends/', admin_views.admin_listing_trends, name='admin_listing_trends'),
]

