from django.urls import path
from . import views, admin_views

urlpatterns = [
    path('register/', views.register_user, name='register'),
    path('send-otp/', views.send_otp, name='send_otp'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('complete-registration/', views.complete_registration, name='complete_registration'),
    path('check-email/', views.check_email, name='check_email'),
    path('login/', views.login_view, name='login'),
    path('password-reset/request/', views.request_password_reset, name='request_password_reset'),
    path('password-reset/verify/', views.verify_password_reset_token, name='verify_password_reset_token'),
    path('password-reset/reset/', views.reset_password, name='reset_password'),
    path('update-profile/', views.update_profile, name='update_profile'),
    
    # Admin endpoints
    path('admin/dashboard/stats/', admin_views.admin_dashboard_stats, name='admin-dashboard-stats'),
    path('admin/analytics/users/', admin_views.admin_user_analytics, name='admin-user-analytics'),
    path('admin/list/', admin_views.admin_user_list, name='admin-user-list'),
    path('admin/<int:user_id>/details/', admin_views.admin_user_details, name='admin-user-details'),
    path('admin/<int:user_id>/suspend/', admin_views.admin_suspend_user, name='admin-suspend-user'),
    
    # Admin Analytics - NEW
    path('admin/analytics/users/trends/', admin_views.admin_user_trends, name='admin-user-trends'),
    path('admin/analytics/users/cohorts/', admin_views.admin_user_cohorts, name='admin-user-cohorts'),
    path('admin/analytics/users/geography/', admin_views.admin_user_geography, name='admin-user-geography'),
    path('admin/analytics/users/segments/', admin_views.admin_user_segments, name='admin-user-segments'),
    
    # Admin Management - NEW
    path('admin/admins/list/', admin_views.admin_list_admins, name='admin-list-admins'),
    path('admin/admins/create/', admin_views.admin_create_admin, name='admin-create-admin'),
    path('admin/admins/<int:user_id>/promote/', admin_views.admin_promote_user, name='admin-promote-user'),
    path('admin/admins/<int:user_id>/demote/', admin_views.admin_demote_admin, name='admin-demote-admin'),
    path('admin/admins/<int:user_id>/delete/', admin_views.admin_delete_admin, name='admin-delete-admin'),
]

