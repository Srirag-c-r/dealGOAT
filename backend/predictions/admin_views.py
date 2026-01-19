"""
Admin views for listing moderation and fraud detection
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta

from users.permissions import IsSuperAdmin, IsModerator, IsAdminUser
from users.admin_utils import log_admin_action
from .models import (
    Listing, FlaggedListing, ModerationAction,
    LaptopPrediction, SmartphonePrediction
)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_listing_stats(request):
    """
    Get listing statistics for admin dashboard.
    
    GET /api/predictions/admin/dashboard/stats/
    """
    try:
        now = timezone.now()
        last_7_days = now - timedelta(days=7)
        
        # Overall listing stats
        total_listings = Listing.objects.count()
        active_listings = Listing.objects.filter(status='active', moderation_status='approved').count()
        pending_moderation = Listing.objects.filter(moderation_status='pending').count()
        flagged_listings = Listing.objects.filter(moderation_status='flagged').count()
        rejected_listings = Listing.objects.filter(moderation_status='rejected').count()
        sold_listings = Listing.objects.filter(status='sold').count()
        
        # Recent activity
        listings_7d = Listing.objects.filter(created_at__gte=last_7_days).count()
        moderated_7d = ModerationAction.objects.filter(created_at__gte=last_7_days).count()
        
        # Device type breakdown
        smartphone_listings = Listing.objects.filter(device_type='smartphone').count()
        laptop_listings = Listing.objects.filter(device_type='laptop').count()
        
        # Fraud detection stats
        total_flags = FlaggedListing.objects.count()
        pending_flags = FlaggedListing.objects.filter(status='pending').count()
        automated_flags = FlaggedListing.objects.filter(is_automated=True).count()
        
        # Flag reasons breakdown
        flag_reasons = FlaggedListing.objects.values('flag_reason').annotate(
            count=Count('id')
        ).order_by('-count')
        
        stats = {
            'listings': {
                'total': total_listings,
                'active': active_listings,
                'pending_moderation': pending_moderation,
                'flagged': flagged_listings,
                'rejected': rejected_listings,
                'sold': sold_listings,
                'recent_7d': listings_7d,
            },
            'device_types': {
                'smartphone': smartphone_listings,
                'laptop': laptop_listings,
            },
            'moderation': {
                'actions_7d': moderated_7d,
            },
            'fraud_detection': {
                'total_flags': total_flags,
                'pending_flags': pending_flags,
                'automated_flags': automated_flags,
                'flag_reasons': list(flag_reasons),
            },
            'timestamp': now.isoformat(),
        }
        
        return Response(stats, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch listing stats: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_listing_list(request):
    """
    Get paginated list of all listings with filters.
    
    GET /api/predictions/admin/listings/list/?page=1&status=pending&device_type=smartphone
    """
    try:
        # Get query parameters
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        moderation_status = request.GET.get('moderation_status', '')
        device_type = request.GET.get('device_type', '')
        listing_status = request.GET.get('status', '')
        search = request.GET.get('search', '')
        
        # Build query
        listings = Listing.objects.select_related('seller').all()
        
        # Apply filters
        if moderation_status:
            listings = listings.filter(moderation_status=moderation_status)
        
        if device_type:
            listings = listings.filter(device_type=device_type)
        
        if listing_status:
            listings = listings.filter(status=listing_status)
        
        if search:
            listings = listings.filter(
                Q(seller__email__icontains=search) |
                Q(imei_or_serial__icontains=search) |
                Q(city__icontains=search)
            )
        
        # Get total count
        total_count = listings.count()
        
        # Paginate
        start = (page - 1) * page_size
        end = start + page_size
        listings = listings.order_by('-created_at')[start:end]
        
        # Serialize listings
        listings_data = []
        for listing in listings:
            # Get prediction data
            predicted_price = None
            if listing.device_type == 'smartphone' and listing.smartphone_prediction:
                predicted_price = float(listing.smartphone_prediction.predicted_price)
            elif listing.device_type == 'laptop' and listing.laptop_prediction:
                predicted_price = float(listing.laptop_prediction.predicted_price)
            
            # Check for flags
            has_flags = listing.flags.filter(status='pending').exists()
            flag_count = listing.flags.count()
            
            listings_data.append({
                'id': listing.id,
                'device_type': listing.device_type,
                'seller': {
                    'id': listing.seller.id,
                    'email': listing.seller.email,
                    'name': listing.seller.get_full_name(),
                },
                'expected_price': float(listing.expected_price),
                'predicted_price': predicted_price,
                'price_deviation': round(((float(listing.expected_price) - predicted_price) / predicted_price * 100) if predicted_price else 0, 2),
                'status': listing.status,
                'moderation_status': listing.moderation_status,
                'has_flags': has_flags,
                'flag_count': flag_count,
                'city': listing.city,
                'created_at': listing.created_at.isoformat(),
                'moderated_at': listing.moderated_at.isoformat() if listing.moderated_at else None,
            })
        
        response_data = {
            'listings': listings_data,
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
            {'error': f'Failed to fetch listings: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_pending_listings(request):
    """
    Get listings pending moderation approval.
    
    GET /api/predictions/admin/listings/pending/
    """
    try:
        pending = Listing.objects.filter(
            moderation_status='pending'
        ).select_related('seller').order_by('created_at')
        
        listings_data = []
        for listing in pending:
            # Get prediction
            predicted_price = None
            if listing.device_type == 'smartphone' and listing.smartphone_prediction:
                predicted_price = float(listing.smartphone_prediction.predicted_price)
            elif listing.device_type == 'laptop' and listing.laptop_prediction:
                predicted_price = float(listing.laptop_prediction.predicted_price)
            
            listings_data.append({
                'id': listing.id,
                'device_type': listing.device_type,
                'seller_email': listing.seller.email,
                'expected_price': float(listing.expected_price),
                'predicted_price': predicted_price,
                'price_deviation': round(((float(listing.expected_price) - predicted_price) / predicted_price * 100) if predicted_price else 0, 2),
                'imei_or_serial': listing.imei_or_serial,
                'city': listing.city,
                'created_at': listing.created_at.isoformat(),
                'waiting_days': (timezone.now() - listing.created_at).days,
            })
        
        return Response({
            'pending_listings': listings_data,
            'count': len(listings_data),
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch pending listings: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_flagged_listings(request):
    """
    Get flagged listings requiring review.
    
    GET /api/predictions/admin/listings/flagged/
    """
    try:
        flagged = FlaggedListing.objects.filter(
            status__in=['pending', 'under_review']
        ).select_related('listing', 'listing__seller', 'reporter').order_by('-created_at')
        
        flagged_data = []
        for flag in flagged:
            flagged_data.append({
                'id': flag.id,
                'listing_id': flag.listing.id,
                'device_type': flag.listing.device_type,
                'seller_email': flag.listing.seller.email,
                'flag_reason': flag.get_flag_reason_display(),
                'description': flag.description,
                'is_automated': flag.is_automated,
                'detection_data': flag.detection_data,
                'reporter': flag.reporter.email if flag.reporter else 'Automated System',
                'status': flag.get_status_display(),
                'created_at': flag.created_at.isoformat(),
            })
        
        return Response({
            'flagged_listings': flagged_data,
            'count': len(flagged_data),
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch flagged listings: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsModerator])
def admin_moderate_listing(request, listing_id):
    """
    Moderate a listing (approve, reject, flag).
    
    POST /api/predictions/admin/listings/<listing_id>/moderate/
    {
        "action": "approve" | "reject" | "flag",
        "notes": "Moderator notes",
        "flag_reason": "duplicate_imei" (if action is flag)
    }
    """
    try:
        listing = Listing.objects.get(id=listing_id)
        action = request.data.get('action')
        notes = request.data.get('notes', '')
        
        if action == 'approve':
            listing.moderation_status = 'approved'
            listing.moderated_by = request.user
            listing.moderated_at = timezone.now()
            listing.moderation_notes = notes
            listing.save()
            
            # Create moderation action record
            ModerationAction.objects.create(
                listing=listing,
                moderator=request.user,
                action_type='approve',
                notes=notes
            )
            
            # Log admin action
            log_admin_action(
                admin_user=request.user,
                action_type='listing_approve',
                target_model='Listing',
                target_id=listing_id,
                description=f"Approved listing #{listing_id}",
                request=request,
                notes=notes
            )
            
            message = f'Listing #{listing_id} approved'
            
        elif action == 'reject':
            listing.moderation_status = 'rejected'
            listing.moderated_by = request.user
            listing.moderated_at = timezone.now()
            listing.moderation_notes = notes
            listing.status = 'inactive'
            listing.save()
            
            # Create moderation action record
            ModerationAction.objects.create(
                listing=listing,
                moderator=request.user,
                action_type='reject',
                notes=notes
            )
            
            # Log admin action
            log_admin_action(
                admin_user=request.user,
                action_type='listing_reject',
                target_model='Listing',
                target_id=listing_id,
                description=f"Rejected listing #{listing_id}. Reason: {notes}",
                request=request,
                notes=notes
            )
            
            message = f'Listing #{listing_id} rejected'
            
        elif action == 'flag':
            flag_reason = request.data.get('flag_reason', 'other')
            
            listing.moderation_status = 'flagged'
            listing.save()
            
            # Create flag record
            FlaggedListing.objects.create(
                listing=listing,
                reporter=request.user,
                flag_reason=flag_reason,
                description=notes,
                is_automated=False,
                status='under_review'
            )
            
            # Create moderation action record
            ModerationAction.objects.create(
                listing=listing,
                moderator=request.user,
                action_type='mark_fraud',
                notes=notes
            )
            
            # Log admin action
            log_admin_action(
                admin_user=request.user,
                action_type='listing_flag',
                target_model='Listing',
                target_id=listing_id,
                description=f"Flagged listing #{listing_id} for {flag_reason}",
                request=request,
                flag_reason=flag_reason,
                notes=notes
            )
            
            message = f'Listing #{listing_id} flagged for review'
            
        else:
            return Response(
                {'error': 'Invalid action. Use "approve", "reject", or "flag"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({
            'message': message,
            'listing': {
                'id': listing.id,
                'moderation_status': listing.moderation_status,
                'status': listing.status,
            }
        }, status=status.HTTP_200_OK)
        
    except Listing.DoesNotExist:
        return Response(
            {'error': 'Listing not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to moderate listing: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_fraud_check(request):
    """
    Run automated fraud detection checks on listings.
    
    POST /api/predictions/admin/listings/fraud-check/
    {
        "listing_id": 123 (optional, checks specific listing or all if not provided)
    }
    """
    try:
        listing_id = request.data.get('listing_id')
        
        if listing_id:
            listings = Listing.objects.filter(id=listing_id)
        else:
            # Check all active/pending listings
            listings = Listing.objects.filter(
                moderation_status__in=['pending', 'approved']
            )
        
        flags_created = 0
        
        for listing in listings:
            # Check 1: Duplicate IMEI/Serial
            duplicate_count = Listing.objects.filter(
                imei_or_serial=listing.imei_or_serial
            ).exclude(id=listing.id).count()
            
            if duplicate_count > 0:
                FlaggedListing.objects.get_or_create(
                    listing=listing,
                    flag_reason='duplicate_imei',
                    defaults={
                        'description': f'Duplicate IMEI/Serial found in {duplicate_count} other listing(s)',
                        'is_automated': True,
                        'detection_data': {'duplicate_count': duplicate_count},
                        'status': 'pending'
                    }
                )
                flags_created += 1
            
            # Check 2: Suspicious pricing (>30% deviation from predicted)
            predicted_price = None
            if listing.device_type == 'smartphone' and listing.smartphone_prediction:
                predicted_price = float(listing.smartphone_prediction.predicted_price)
            elif listing.device_type == 'laptop' and listing.laptop_prediction:
                predicted_price = float(listing.laptop_prediction.predicted_price)
            
            if predicted_price:
                deviation = ((float(listing.expected_price) - predicted_price) / predicted_price) * 100
                
                if deviation < -30:  # Price is 30% below predicted
                    FlaggedListing.objects.get_or_create(
                        listing=listing,
                        flag_reason='suspicious_price',
                        defaults={
                            'description': f'Price is {abs(deviation):.1f}% below predicted price',
                            'is_automated': True,
                            'detection_data': {
                                'expected_price': float(listing.expected_price),
                                'predicted_price': predicted_price,
                                'deviation_percent': round(deviation, 2)
                            },
                            'status': 'pending'
                        }
                    )
                    flags_created += 1
            
            # Check 3: Multiple listings from same user
            user_listing_count = Listing.objects.filter(
                seller=listing.seller,
                status='active'
            ).count()
            
            if user_listing_count > 5:
                FlaggedListing.objects.get_or_create(
                    listing=listing,
                    flag_reason='spam',
                    defaults={
                        'description': f'User has {user_listing_count} active listings',
                        'is_automated': True,
                        'detection_data': {'user_listing_count': user_listing_count},
                        'status': 'pending'
                    }
                )
                flags_created += 1
        
        return Response({
            'message': f'Fraud check completed. {flags_created} new flags created.',
            'listings_checked': listings.count(),
            'flags_created': flags_created,
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to run fraud check: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_prediction_trends(request):
    """
    Get prediction volume trends over time.
    
    GET /api/predictions/admin/analytics/trends/?period=30
    """
    try:
        from django.utils import timezone
        from datetime import timedelta
        
        period = int(request.GET.get('period', 30))
        now = timezone.now()
        
        # Daily prediction counts
        prediction_trend = []
        for i in range(period, -1, -1):
            date = (now - timedelta(days=i)).date()
            
            laptop_count = LaptopPrediction.objects.filter(created_at__date=date).count()
            smartphone_count = SmartphonePrediction.objects.filter(created_at__date=date).count()
            
            prediction_trend.append({
                'date': date.isoformat(),
                'laptop': laptop_count,
                'smartphone': smartphone_count,
                'total': laptop_count + smartphone_count
            })
        
        # Summary stats
        total_predictions = (
            LaptopPrediction.objects.count() + 
            SmartphonePrediction.objects.count()
        )
        
        recent_predictions = (
            LaptopPrediction.objects.filter(created_at__gte=now - timedelta(days=7)).count() +
            SmartphonePrediction.objects.filter(created_at__gte=now - timedelta(days=7)).count()
        )
        
        return Response({
            'prediction_trend': prediction_trend,
            'total_predictions': total_predictions,
            'recent_predictions_7d': recent_predictions,
            'period': period,
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch prediction trends: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_device_popularity(request):
    """
    Get device popularity and trends.
    
    GET /api/predictions/admin/analytics/devices/
    """
    try:
        # Top laptop brands
        laptop_brands = LaptopPrediction.objects.values('brand').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # Top smartphone brands
        smartphone_brands = SmartphonePrediction.objects.values('brand').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # Device type distribution
        total_laptop = LaptopPrediction.objects.count()
        total_smartphone = SmartphonePrediction.objects.count()
        
        device_distribution = {
            'laptop': total_laptop,
            'smartphone': total_smartphone,
            'total': total_laptop + total_smartphone
        }
        
        # Average predicted prices
        from django.db.models import Avg
        avg_laptop_price = LaptopPrediction.objects.aggregate(
            avg_price=Avg('predicted_price')
        )['avg_price'] or 0
        
        avg_smartphone_price = SmartphonePrediction.objects.aggregate(
            avg_price=Avg('predicted_price')
        )['avg_price'] or 0
        
        return Response({
            'top_laptop_brands': list(laptop_brands),
            'top_smartphone_brands': list(smartphone_brands),
            'device_distribution': device_distribution,
            'average_prices': {
                'laptop': round(float(avg_laptop_price), 2),
                'smartphone': round(float(avg_smartphone_price), 2),
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch device popularity: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_price_distribution(request):
    """
    Get price range distribution for predictions.
    
    GET /api/predictions/admin/analytics/price-distribution/
    """
    try:
        # Define price ranges
        price_ranges = [
            {'min': 0, 'max': 10000, 'label': 'Under ₹10k'},
            {'min': 10000, 'max': 25000, 'label': '₹10k-25k'},
            {'min': 25000, 'max': 50000, 'label': '₹25k-50k'},
            {'min': 50000, 'max': 75000, 'label': '₹50k-75k'},
            {'min': 75000, 'max': 100000, 'label': '₹75k-1L'},
            {'min': 100000, 'max': 999999999, 'label': 'Above ₹1L'},
        ]
        
        # Count predictions in each range
        laptop_distribution = []
        smartphone_distribution = []
        
        for range_def in price_ranges:
            laptop_count = LaptopPrediction.objects.filter(
                predicted_price__gte=range_def['min'],
                predicted_price__lt=range_def['max']
            ).count()
            
            smartphone_count = SmartphonePrediction.objects.filter(
                predicted_price__gte=range_def['min'],
                predicted_price__lt=range_def['max']
            ).count()
            
            laptop_distribution.append({
                'range': range_def['label'],
                'count': laptop_count
            })
            
            smartphone_distribution.append({
                'range': range_def['label'],
                'count': smartphone_count
            })
        
        return Response({
            'laptop_distribution': laptop_distribution,
            'smartphone_distribution': smartphone_distribution,
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch price distribution: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_listing_trends(request):
    """
    Get listing creation and sales trends.
    
    GET /api/predictions/admin/analytics/listings/trends/?period=30
    """
    try:
        from django.utils import timezone
        from datetime import timedelta
        
        period = int(request.GET.get('period', 30))
        now = timezone.now()
        
        # Daily listing trends
        listing_trend = []
        for i in range(period, -1, -1):
            date = (now - timedelta(days=i)).date()
            
            created_count = Listing.objects.filter(created_at__date=date).count()
            sold_count = Listing.objects.filter(
                status='sold',
                updated_at__date=date
            ).count()
            
            listing_trend.append({
                'date': date.isoformat(),
                'created': created_count,
                'sold': sold_count
            })
        
        # Calculate average time to sell
        sold_listings = Listing.objects.filter(status='sold')
        total_days = 0
        count = 0
        
        for listing in sold_listings[:100]:  # Sample for performance
            if listing.updated_at and listing.created_at:
                days = (listing.updated_at - listing.created_at).days
                total_days += days
                count += 1
        
        avg_time_to_sell = round(total_days / count, 1) if count > 0 else 0
        
        return Response({
            'listing_trend': listing_trend,
            'avg_time_to_sell_days': avg_time_to_sell,
            'period': period,
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch listing trends: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

