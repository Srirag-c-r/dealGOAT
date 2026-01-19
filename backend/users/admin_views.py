"""
Admin dashboard views for user management and statistics
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import timedelta

from .permissions import IsSuperAdmin, IsModerator, IsAdminUser
from .admin_utils import log_admin_action
from .models import AdminActionLog
from predictions.models import LaptopPrediction, SmartphonePrediction, Listing, Conversation, Message
from recommendations.models import RequirementQuery

User = get_user_model()


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_dashboard_stats(request):
    """
    Get overall dashboard statistics for admin panel.
    
    GET /api/users/admin/dashboard/stats/
    """
    try:
        # Calculate date ranges
        now = timezone.now()
        last_7_days = now - timedelta(days=7)
        last_30_days = now - timedelta(days=30)
        
        # User statistics
        total_users = User.objects.count()
        active_users_7d = User.objects.filter(last_login__gte=last_7_days).count()
        active_users_30d = User.objects.filter(last_login__gte=last_30_days).count()
        verified_users = User.objects.filter(email_verified=True).count()
        suspended_users = User.objects.filter(is_suspended=True).count()
        new_users_7d = User.objects.filter(date_joined__gte=last_7_days).count()
        new_users_30d = User.objects.filter(date_joined__gte=last_30_days).count()
        
        # Prediction statistics
        total_laptop_predictions = LaptopPrediction.objects.count()
        total_smartphone_predictions = SmartphonePrediction.objects.count()
        predictions_7d = (
            LaptopPrediction.objects.filter(created_at__gte=last_7_days).count() +
            SmartphonePrediction.objects.filter(created_at__gte=last_7_days).count()
        )
        
        # Listing statistics
        total_listings = Listing.objects.count()
        active_listings = Listing.objects.filter(status='active', moderation_status='approved').count()
        pending_listings = Listing.objects.filter(moderation_status='pending').count()
        sold_listings = Listing.objects.filter(status='sold').count()
        flagged_listings = Listing.objects.filter(moderation_status='flagged').count()
        listings_7d = Listing.objects.filter(created_at__gte=last_7_days).count()
        
        # Messaging statistics
        total_conversations = Conversation.objects.count()
        total_messages = Message.objects.count()
        messages_7d = Message.objects.filter(created_at__gte=last_7_days).count()
        active_conversations_7d = Conversation.objects.filter(last_message_at__gte=last_7_days).count()
        
        # Recommendation statistics
        total_queries = RequirementQuery.objects.count()
        queries_7d = RequirementQuery.objects.filter(created_at__gte=last_7_days).count()
        
        # Admin action statistics
        admin_actions_7d = AdminActionLog.objects.filter(created_at__gte=last_7_days).count()
        admin_actions_30d = AdminActionLog.objects.filter(created_at__gte=last_30_days).count()
        
        stats = {
            'users': {
                'total': total_users,
                'active_7d': active_users_7d,
                'active_30d': active_users_30d,
                'verified': verified_users,
                'suspended': suspended_users,
                'new_7d': new_users_7d,
                'new_30d': new_users_30d,
                'verification_rate': round((verified_users / total_users * 100) if total_users > 0 else 0, 2),
            },
            'predictions': {
                'total': total_laptop_predictions + total_smartphone_predictions,
                'laptop': total_laptop_predictions,
                'smartphone': total_smartphone_predictions,
                'recent_7d': predictions_7d,
            },
            'listings': {
                'total': total_listings,
                'active': active_listings,
                'pending_moderation': pending_listings,
                'sold': sold_listings,
                'flagged': flagged_listings,
                'recent_7d': listings_7d,
            },
            'messaging': {
                'total_conversations': total_conversations,
                'total_messages': total_messages,
                'messages_7d': messages_7d,
                'active_conversations_7d': active_conversations_7d,
            },
            'recommendations': {
                'total_queries': total_queries,
                'queries_7d': queries_7d,
            },
            'admin_activity': {
                'actions_7d': admin_actions_7d,
                'actions_30d': admin_actions_30d,
            },
            'timestamp': now.isoformat(),
        }
        
        return Response(stats, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch dashboard stats: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_user_analytics(request):
    """
    Get detailed user analytics for charts and graphs.
    
    GET /api/users/admin/analytics/users/
    """
    try:
        # User registration trend (last 30 days)
        now = timezone.now()
        registration_trend = []
        for i in range(30, -1, -1):
            date = (now - timedelta(days=i)).date()
            count = User.objects.filter(date_joined__date=date).count()
            registration_trend.append({
                'date': date.isoformat(),
                'count': count
            })
        
        # User demographics
        gender_distribution = User.objects.values('gender').annotate(count=Count('id'))
        
        # Location distribution (top 10)
        location_distribution = User.objects.exclude(location='').values('location').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # Most active users (by predictions + listings)
        from django.db.models import Count
        active_users = User.objects.annotate(
            prediction_count=Count('laptop_predictions') + Count('smartphone_predictions'),
            listing_count=Count('listings')
        ).order_by('-prediction_count', '-listing_count')[:10]
        
        active_users_data = [{
            'id': user.id,
            'email': user.email,
            'name': user.get_full_name(),
            'predictions': user.prediction_count,
            'listings': user.listing_count,
        } for user in active_users]
        
        analytics = {
            'registration_trend': registration_trend,
            'gender_distribution': list(gender_distribution),
            'location_distribution': list(location_distribution),
            'most_active_users': active_users_data,
        }
        
        return Response(analytics, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch user analytics: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_user_list(request):
    """
    Get paginated list of all users with filters.
    
    GET /api/users/admin/list/?page=1&search=email&status=active&verified=true
    """
    try:
        # Get query parameters
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        search = request.GET.get('search', '')
        user_status = request.GET.get('status', '')  # active, suspended
        verified = request.GET.get('verified', '')  # true, false
        
        # Build query
        users = User.objects.all()
        
        # Apply filters
        if search:
            users = users.filter(
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        
        if user_status == 'suspended':
            users = users.filter(is_suspended=True)
        elif user_status == 'active':
            users = users.filter(is_suspended=False, is_active=True)
        
        if verified == 'true':
            users = users.filter(email_verified=True)
        elif verified == 'false':
            users = users.filter(email_verified=False)
        
        # Get total count
        total_count = users.count()
        
        # Paginate
        start = (page - 1) * page_size
        end = start + page_size
        users = users.order_by('-date_joined')[start:end]
        
        # Serialize users
        users_data = [{
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone': user.phone,
            'location': user.location,
            'email_verified': user.email_verified,
            'is_active': user.is_active,
            'is_suspended': user.is_suspended,
            'is_staff': user.is_staff,
            'date_joined': user.date_joined.isoformat(),
            'last_login': user.last_login.isoformat() if user.last_login else None,
        } for user in users]
        
        response_data = {
            'users': users_data,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_count': total_count,
                'total_pages': (total_count + page_size - 1) // page_size,
            }
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch users: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_user_details(request, user_id):
    """
    Get detailed information about a specific user.
    
    GET /api/users/admin/<user_id>/details/
    """
    try:
        user = User.objects.get(id=user_id)
        
        # Get user's activity
        laptop_predictions = LaptopPrediction.objects.filter(user=user).count()
        smartphone_predictions = SmartphonePrediction.objects.filter(user=user).count()
        listings = Listing.objects.filter(seller=user).count()
        conversations = Conversation.objects.filter(Q(buyer=user) | Q(seller=user)).count()
        queries = RequirementQuery.objects.filter(user=user).count()
        
        # Get recent admin actions on this user
        recent_actions = AdminActionLog.objects.filter(
            target_model='User',
            target_id=user_id
        ).order_by('-created_at')[:10]
        
        actions_data = [{
            'id': action.id,
            'action_type': action.get_action_type_display(),
            'admin': action.admin_user.email if action.admin_user else 'System',
            'description': action.description,
            'created_at': action.created_at.isoformat(),
        } for action in recent_actions]
        
        user_data = {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone': user.phone,
            'location': user.location,
            'gender': user.gender,
            'age': user.age,
            'email_verified': user.email_verified,
            'is_active': user.is_active,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'is_suspended': user.is_suspended,
            'suspension_reason': user.suspension_reason,
            'suspended_at': user.suspended_at.isoformat() if user.suspended_at else None,
            'is_banned_from_messaging': user.is_banned_from_messaging,
            'profile_picture': user.profile_picture.url if user.profile_picture else None,
            'date_joined': user.date_joined.isoformat(),
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'activity': {
                'laptop_predictions': laptop_predictions,
                'smartphone_predictions': smartphone_predictions,
                'total_predictions': laptop_predictions + smartphone_predictions,
                'listings': listings,
                'conversations': conversations,
                'recommendation_queries': queries,
            },
            'recent_admin_actions': actions_data,
        }
        
        return Response(user_data, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch user details: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsModerator])
def admin_suspend_user(request, user_id):
    """
    Suspend or unsuspend a user.
    
    POST /api/users/admin/<user_id>/suspend/
    {
        "action": "suspend" or "unsuspend",
        "reason": "Reason for suspension"
    }
    """
    try:
        user = User.objects.get(id=user_id)
        action = request.data.get('action')
        reason = request.data.get('reason', '')
        
        if action == 'suspend':
            user.is_suspended = True
            user.suspension_reason = reason
            user.suspended_at = timezone.now()
            user.suspended_by = request.user
            user.save()
            
            # Log action
            log_admin_action(
                admin_user=request.user,
                action_type='user_suspend',
                target_model='User',
                target_id=user_id,
                description=f"Suspended user {user.email}. Reason: {reason}",
                request=request,
                reason=reason
            )
            
            message = f'User {user.email} has been suspended'
            
        elif action == 'unsuspend':
            user.is_suspended = False
            user.suspension_reason = ''
            user.suspended_at = None
            user.suspended_by = None
            user.save()
            
            # Log action
            log_admin_action(
                admin_user=request.user,
                action_type='user_activate',
                target_model='User',
                target_id=user_id,
                description=f"Unsuspended user {user.email}",
                request=request
            )
            
            message = f'User {user.email} has been unsuspended'
        else:
            return Response(
                {'error': 'Invalid action. Use "suspend" or "unsuspend"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({
            'message': message,
            'user': {
                'id': user.id,
                'email': user.email,
                'is_suspended': user.is_suspended,
            }
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to update user status: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_user_trends(request):
    """
    Get time-series user trends for analytics charts.
    
    GET /api/auth/admin/analytics/users/trends/?period=30&interval=daily
    """
    try:
        # Get query parameters
        period = int(request.GET.get('period', 30))  # days
        interval = request.GET.get('interval', 'daily')  # daily, weekly, monthly
        
        now = timezone.now()
        start_date = now - timedelta(days=period)
        
        # User registration trend
        registration_trend = []
        login_trend = []
        
        if interval == 'daily':
            for i in range(period, -1, -1):
                date = (now - timedelta(days=i)).date()
                reg_count = User.objects.filter(date_joined__date=date).count()
                login_count = User.objects.filter(last_login__date=date).count()
                
                registration_trend.append({
                    'date': date.isoformat(),
                    'count': reg_count
                })
                login_trend.append({
                    'date': date.isoformat(),
                    'count': login_count
                })
        
        elif interval == 'weekly':
            weeks = period // 7
            for i in range(weeks, -1, -1):
                week_start = (now - timedelta(weeks=i)).date()
                week_end = week_start + timedelta(days=7)
                
                reg_count = User.objects.filter(
                    date_joined__date__gte=week_start,
                    date_joined__date__lt=week_end
                ).count()
                
                registration_trend.append({
                    'date': week_start.isoformat(),
                    'count': reg_count
                })
        
        # Active users trend
        active_trend = []
        for i in range(min(period, 30), -1, -1):
            date = (now - timedelta(days=i)).date()
            active_count = User.objects.filter(
                last_login__date=date
            ).count()
            
            active_trend.append({
                'date': date.isoformat(),
                'count': active_count
            })
        
        trends = {
            'registration_trend': registration_trend,
            'login_trend': login_trend[:30],  # Limit to 30 days for performance
            'active_trend': active_trend,
            'period': period,
            'interval': interval,
        }
        
        return Response(trends, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch user trends: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_user_cohorts(request):
    """
    Get cohort retention analysis.
    
    GET /api/auth/admin/analytics/users/cohorts/
    """
    try:
        now = timezone.now()
        cohorts = []
        
        # Generate weekly cohorts for last 12 weeks
        for i in range(11, -1, -1):
            cohort_start = (now - timedelta(weeks=i)).replace(hour=0, minute=0, second=0, microsecond=0)
            cohort_end = cohort_start + timedelta(days=7)
            
            # Users who joined in this cohort
            cohort_users = User.objects.filter(
                date_joined__gte=cohort_start,
                date_joined__lt=cohort_end
            )
            cohort_size = cohort_users.count()
            
            if cohort_size > 0:
                # Calculate retention for different periods
                day_1_active = cohort_users.filter(
                    last_login__gte=cohort_start + timedelta(days=1),
                    last_login__lt=cohort_start + timedelta(days=2)
                ).count()
                
                day_7_active = cohort_users.filter(
                    last_login__gte=cohort_start + timedelta(days=7),
                    last_login__lt=cohort_start + timedelta(days=8)
                ).count()
                
                day_14_active = cohort_users.filter(
                    last_login__gte=cohort_start + timedelta(days=14),
                    last_login__lt=cohort_start + timedelta(days=15)
                ).count()
                
                day_30_active = cohort_users.filter(
                    last_login__gte=cohort_start + timedelta(days=30)
                ).count()
                
                cohorts.append({
                    'cohort_date': cohort_start.date().isoformat(),
                    'cohort_size': cohort_size,
                    'day_1_retention': round((day_1_active / cohort_size * 100), 2) if cohort_size > 0 else 0,
                    'day_7_retention': round((day_7_active / cohort_size * 100), 2) if cohort_size > 0 else 0,
                    'day_14_retention': round((day_14_active / cohort_size * 100), 2) if cohort_size > 0 else 0,
                    'day_30_retention': round((day_30_active / cohort_size * 100), 2) if cohort_size > 0 else 0,
                })
        
        return Response({
            'cohorts': cohorts,
            'total_cohorts': len(cohorts),
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch cohort data: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_user_geography(request):
    """
    Get geographic distribution of users.
    
    GET /api/auth/admin/analytics/users/geography/
    """
    try:
        # Get user count by location
        location_data = User.objects.exclude(
            Q(location='') | Q(location__isnull=True)
        ).values('location').annotate(
            user_count=Count('id')
        ).order_by('-user_count')[:50]  # Top 50 locations
        
        # Format for frontend
        geography = [{
            'location': item['location'],
            'count': item['user_count']
        } for item in location_data]
        
        # Get total users by location
        total_with_location = sum(item['count'] for item in geography)
        total_users = User.objects.count()
        
        return Response({
            'geography': geography,
            'total_with_location': total_with_location,
            'total_users': total_users,
            'coverage_percentage': round((total_with_location / total_users * 100), 2) if total_users > 0 else 0,
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch geography data: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_user_segments(request):
    """
    Get user segmentation analysis.
    
    GET /api/auth/admin/analytics/users/segments/
    """
    try:
        now = timezone.now()
        last_7_days = now - timedelta(days=7)
        last_30_days = now - timedelta(days=30)
        
        # Define user segments
        power_users = User.objects.annotate(
            prediction_count=Count('laptop_predictions') + Count('smartphone_predictions'),
            listing_count=Count('listings')
        ).filter(
            Q(prediction_count__gte=5) | Q(listing_count__gte=3)
        ).count()
        
        active_users = User.objects.filter(
            last_login__gte=last_7_days
        ).count()
        
        inactive_users = User.objects.filter(
            last_login__lt=last_30_days,
            last_login__isnull=False
        ).count()
        
        new_users = User.objects.filter(
            date_joined__gte=last_7_days
        ).count()
        
        churned_users = User.objects.filter(
            last_login__lt=now - timedelta(days=60),
            last_login__isnull=False
        ).count()
        
        # Users with no activity
        dormant_users = User.objects.filter(
            last_login__isnull=True
        ).count()
        
        segments = {
            'power_users': power_users,
            'active_users': active_users,
            'inactive_users': inactive_users,
            'new_users': new_users,
            'churned_users': churned_users,
            'dormant_users': dormant_users,
            'total_users': User.objects.count(),
        }
        
        return Response(segments, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch user segments: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsSuperAdmin])
def admin_list_admins(request):
    """
    List all admin users (staff and superusers).
    
    GET /api/auth/admin/admins/list/
    """
    try:
        admins = User.objects.filter(is_staff=True).order_by('-is_superuser', 'email')
        
        admin_data = [{
            'id': admin.id,
            'email': admin.email,
            'first_name': admin.first_name,
            'last_name': admin.last_name,
            'is_superuser': admin.is_superuser,
            'is_staff': admin.is_staff,
            'is_suspended': admin.is_suspended,
            'email_verified': admin.email_verified,
            'date_joined': admin.date_joined.isoformat(),
            'last_login': admin.last_login.isoformat() if admin.last_login else None,
        } for admin in admins]
        
        return Response({
            'admins': admin_data,
            'total': len(admin_data),
            'super_admins': sum(1 for a in admin_data if a['is_superuser']),
            'regular_admins': sum(1 for a in admin_data if not a['is_superuser']),
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch admins: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsSuperAdmin])
def admin_create_admin(request):
    """
    Create a new admin user.
    
    POST /api/auth/admin/admins/create/
    {
        "email": "admin@example.com",
        "password": "password123",
        "first_name": "John",
        "last_name": "Doe",
        "is_superuser": false
    }
    """
    try:
        email = request.data.get('email')
        password = request.data.get('password')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        is_superuser = request.data.get('is_superuser', False)
        
        if not email or not password:
            return Response(
                {'error': 'Email and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            return Response(
                {'error': 'User with this email already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create admin user
        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_staff=True,
            is_superuser=is_superuser,
            email_verified=True  # Auto-verify admin accounts
        )
        
        # Log action
        log_admin_action(
            request.user,
            'create_admin',
            f"Created {'super admin' if is_superuser else 'admin'}: {email}"
        )
        
        return Response({
            'message': f"{'Super admin' if is_superuser else 'Admin'} created successfully",
            'admin': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_superuser': user.is_superuser,
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to create admin: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsSuperAdmin])
def admin_promote_user(request, user_id):
    """
    Promote a user to admin or superadmin.
    
    POST /api/auth/admin/admins/<user_id>/promote/
    {
        "to_superuser": false
    }
    """
    try:
        user = User.objects.get(id=user_id)
        to_superuser = request.data.get('to_superuser', False)
        
        if user.is_superuser:
            return Response(
                {'error': 'User is already a super admin'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if user.is_staff and not to_superuser:
            return Response(
                {'error': 'User is already an admin'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Promote user
        user.is_staff = True
        if to_superuser:
            user.is_superuser = True
        user.save()
        
        # Log action
        new_role = "super admin" if to_superuser else "admin"
        log_admin_action(
            request.user,
            'promote_user',
            f"Promoted {user.email} to {new_role}"
        )
        
        return Response({
            'message': f'User promoted to {new_role} successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
            }
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to promote user: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsSuperAdmin])
def admin_demote_admin(request, user_id):
    """
    Demote an admin to regular user.
    
    POST /api/auth/admin/admins/<user_id>/demote/
    """
    try:
        user = User.objects.get(id=user_id)
        
        if not user.is_staff:
            return Response(
                {'error': 'User is not an admin'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Prevent self-demotion
        if user.id == request.user.id:
            return Response(
                {'error': 'You cannot demote yourself'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Demote user
        user.is_staff = False
        user.is_superuser = False
        user.save()
        
        # Log action
        log_admin_action(
            request.user,
            'demote_admin',
            f"Demoted {user.email} to regular user"
        )
        
        return Response({
            'message': 'Admin demoted to regular user successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
            }
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to demote admin: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
@permission_classes([IsSuperAdmin])
def admin_delete_admin(request, user_id):
    """
    Delete an admin user.
    
    DELETE /api/auth/admin/admins/<user_id>/delete/
    """
    try:
        user = User.objects.get(id=user_id)
        
        # Prevent self-deletion
        if user.id == request.user.id:
            return Response(
                {'error': 'You cannot delete yourself'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        email = user.email
        
        # Log action before deletion
        log_admin_action(
            request.user,
            'delete_admin',
            f"Deleted admin user: {email}"
        )
        
        # Delete user
        user.delete()
        
        return Response({
            'message': 'Admin deleted successfully',
            'email': email
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to delete admin: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

