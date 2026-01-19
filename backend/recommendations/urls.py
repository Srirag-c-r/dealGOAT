from django.urls import path
from . import views, admin_views

urlpatterns = [
    path('find-products/', views.find_products, name='find_products'),
    path('query-history/', views.query_history, name='query_history'),
    path('query-detail/<int:query_id>/', views.query_detail, name='query_detail'),
    
    # Admin endpoints
    path('admin/dashboard/stats/', admin_views.admin_recommendation_stats, name='admin_recommendation_stats'),
    path('admin/system-health/', admin_views.admin_system_health, name='admin_system_health'),
    path('admin/settings/get/', admin_views.admin_get_settings, name='admin_get_settings'),
    path('admin/settings/update/', admin_views.admin_update_setting, name='admin_update_setting'),
    path('admin/reports/generate/', admin_views.admin_generate_report, name='admin_generate_report'),
]
