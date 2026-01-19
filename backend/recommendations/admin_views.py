"""
Admin views for system monitoring and analytics
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Count, Avg, Max
from django.utils import timezone
from datetime import timedelta

from users.permissions import IsSuperAdmin, IsAdminUser
from .models import RequirementQuery, ProductResult, SystemMetric, SystemConfiguration


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_recommendation_stats(request):
    """
    Get recommendation system statistics.
    
    GET /api/recommendations/admin/dashboard/stats/
    """
    try:
        now = timezone.now()
        last_7_days = now - timedelta(days=7)
        last_30_days = now - timedelta(days=30)
        
        # Query statistics
        total_queries = RequirementQuery.objects.count()
        queries_7d = RequirementQuery.objects.filter(created_at__gte=last_7_days).count()
        queries_30d = RequirementQuery.objects.filter(created_at__gte=last_30_days).count()
        
        # Average match scores
        avg_match_score = ProductResult.objects.aggregate(
            avg_score=Avg('match_score')
        )['avg_score'] or 0
        
        # Total products recommended
        total_products = ProductResult.objects.count()
        
        # Top brands
        top_brands = ProductResult.objects.values('brand').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        stats = {
            'queries': {
                'total': total_queries,
                'queries_7d': queries_7d,
                'queries_30d': queries_30d,
            },
            'products': {
                'total_recommended': total_products,
                'avg_match_score': round(avg_match_score, 2),
            },
            'top_brands': list(top_brands),
            'timestamp': now.isoformat(),
        }
        
        return Response(stats, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch recommendation stats: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_system_health(request):
    """
    Get system health metrics.
    
    GET /api/recommendations/admin/system-health/
    """
    try:
        now = timezone.now()
        last_hour = now - timedelta(hours=1)
        last_24h = now - timedelta(hours=24)
        
        # Get recent metrics
        recent_metrics = SystemMetric.objects.filter(
            timestamp__gte=last_hour
        ).values('metric_name').annotate(
            avg_value=Avg('metric_value'),
            count=Count('id')
        )
        
        # API response times (if tracked)
        api_metrics = SystemMetric.objects.filter(
            metric_name__contains='api_response_time',
            timestamp__gte=last_24h
        ).aggregate(
            avg_response_time=Avg('metric_value'),
            max_response_time=Max('metric_value')
        )
        
        # Error rates (if tracked)
        error_count = SystemMetric.objects.filter(
            metric_name='error_count',
            timestamp__gte=last_24h
        ).count()
        
        health_data = {
            'status': 'healthy',  # Can be determined by thresholds
            'recent_metrics': list(recent_metrics),
            'api_performance': {
                'avg_response_time_ms': api_metrics.get('avg_response_time', 0),
                'max_response_time_ms': api_metrics.get('max_response_time', 0),
            },
            'errors_24h': error_count,
            'timestamp': now.isoformat(),
        }
        
        return Response(health_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch system health: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_get_settings(request):
    """
    Get all system configurations.
    
    GET /api/recommendations/admin/settings/get/
    """
    try:
        settings = SystemConfiguration.objects.all()
        
        settings_data = [{
            'id': setting.id,
            'key': setting.key,
            'value': setting.value if not setting.is_sensitive else '***',
            'value_type': setting.value_type,
            'description': setting.description,
            'category': setting.category,
            'is_sensitive': setting.is_sensitive,
            'updated_at': setting.updated_at.isoformat(),
            'updated_by': setting.updated_by.email if setting.updated_by else None,
        } for setting in settings]
        
        return Response({
            'settings': settings_data,
            'count': len(settings_data),
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch settings: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsSuperAdmin])
def admin_update_setting(request):
    """
    Update a system configuration.
    
    POST /api/recommendations/admin/settings/update/
    {
        "key": "setting_key",
        "value": "new_value"
    }
    """
    try:
        key = request.data.get('key')
        value = request.data.get('value')
        
        if not key:
            return Response(
                {'error': 'Setting key is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            setting = SystemConfiguration.objects.get(key=key)
            setting.set_value(value, updated_by=request.user)
            
            return Response({
                'message': f'Setting {key} updated successfully',
                'setting': {
                    'key': setting.key,
                    'value': setting.value if not setting.is_sensitive else '***',
                    'updated_at': setting.updated_at.isoformat(),
                }
            }, status=status.HTTP_200_OK)
            
        except SystemConfiguration.DoesNotExist:
            return Response(
                {'error': f'Setting {key} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
    except Exception as e:
        return Response(
            {'error': f'Failed to update setting: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_generate_report(request):
    """
    Generate admin report.
    
    POST /api/recommendations/admin/reports/generate/
    {
        "report_type": "users" | "listings" | "predictions" | "system",
        "date_from": "2024-01-01",
        "date_to": "2024-01-31"
    }
    """
    try:
        from django.contrib.auth import get_user_model
        from predictions.models import Listing, LaptopPrediction, SmartphonePrediction
        from datetime import datetime
        
        User = get_user_model()
        
        report_type = request.data.get('report_type')
        date_from = request.data.get('date_from')
        date_to = request.data.get('date_to')
        
        # Parse dates
        if date_from:
            date_from = datetime.fromisoformat(date_from)
        else:
            date_from = timezone.now() - timedelta(days=30)
        
        if date_to:
            date_to = datetime.fromisoformat(date_to)
        else:
            date_to = timezone.now()
        
        report_data = {
            'report_type': report_type,
            'date_range': {
                'from': date_from.isoformat(),
                'to': date_to.isoformat(),
            },
            'generated_at': timezone.now().isoformat(),
            'generated_by': request.user.email,
        }
        
        if report_type == 'users':
            users = User.objects.filter(date_joined__range=[date_from, date_to])
            report_data['data'] = {
                'total_users': users.count(),
                'verified_users': users.filter(email_verified=True).count(),
                'suspended_users': users.filter(is_suspended=True).count(),
                'users_by_location': list(users.values('location').annotate(count=Count('id')).order_by('-count')[:10]),
            }
            
        elif report_type == 'listings':
            listings = Listing.objects.filter(created_at__range=[date_from, date_to])
            report_data['data'] = {
                'total_listings': listings.count(),
                'approved': listings.filter(moderation_status='approved').count(),
                'pending': listings.filter(moderation_status='pending').count(),
                'rejected': listings.filter(moderation_status='rejected').count(),
                'sold': listings.filter(status='sold').count(),
                'by_device_type': {
                    'smartphone': listings.filter(device_type='smartphone').count(),
                    'laptop': listings.filter(device_type='laptop').count(),
                },
            }
            
        elif report_type == 'predictions':
            laptop_preds = LaptopPrediction.objects.filter(created_at__range=[date_from, date_to])
            smartphone_preds = SmartphonePrediction.objects.filter(created_at__range=[date_from, date_to])
            
            report_data['data'] = {
                'total_predictions': laptop_preds.count() + smartphone_preds.count(),
                'laptop_predictions': laptop_preds.count(),
                'smartphone_predictions': smartphone_preds.count(),
                'avg_laptop_price': laptop_preds.aggregate(avg=Avg('predicted_price'))['avg'] or 0,
                'avg_smartphone_price': smartphone_preds.aggregate(avg=Avg('predicted_price'))['avg'] or 0,
            }
            
        elif report_type == 'system':
            queries = RequirementQuery.objects.filter(created_at__range=[date_from, date_to])
            report_data['data'] = {
                'total_queries': queries.count(),
                'total_products_recommended': ProductResult.objects.filter(created_at__range=[date_from, date_to]).count(),
                'avg_match_score': ProductResult.objects.filter(created_at__range=[date_from, date_to]).aggregate(avg=Avg('match_score'))['avg'] or 0,
            }
        
        else:
            return Response(
                {'error': 'Invalid report type'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(report_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to generate report: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
