from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import (
    LaptopPredictionInputSerializer,
    LaptopPredictionOutputSerializer,
    SmartphonePredictionInputSerializer,
    SmartphonePredictionOutputSerializer,
    ListingSerializer,
    ConversationSerializer,
    MessageSerializer,
)
from .models import LaptopPrediction, SmartphonePrediction, Listing, Conversation, Message
from .ml_service import laptop_predictor, smartphone_predictor
from .imei_service import get_specs_from_imei

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def predict_laptop_price(request):
    """Predict laptop resale price"""
    if laptop_predictor is None:
        return Response(
            {
                'success': False,
                'message': 'Laptop model not loaded. Please run train_laptop_model.py and restart the server.'
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    try:
        # Validate input
        input_serializer = LaptopPredictionInputSerializer(data=request.data)
        
        if not input_serializer.is_valid():
            return Response(
                {
                    'success': False,
                    'message': 'Invalid input data',
                    'errors': input_serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get validated data
        data = input_serializer.validated_data
        
        # Make prediction
        try:
            prediction_result = laptop_predictor.predict(data)
        except Exception as e:
            return Response(
                {
                    'success': False,
                    'message': f'Prediction error: {str(e)}',
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Get user if authenticated
        user = None
        if request.user.is_authenticated:
            user = request.user
        
        # Save prediction to database
        laptop_prediction = LaptopPrediction.objects.create(
            user=user,
            brand=data.get('brand'),
            model=data.get('model', ''),
            launch_year=data.get('launch_year'),
            launch_price=data.get('launch_price'),
            processor=data.get('processor'),
            ram=data.get('ram'),
            storage_type=data.get('storage_type'),
            storage_size=data.get('storage_size'),
            gpu=data.get('gpu'),
            screen_size=data.get('screen_size'),
            battery_cycle_count=data.get('battery_cycle_count'),
            condition=data.get('condition'),
            warranty_remaining=data.get('warranty_remaining'),
            seller_location=data.get('seller_location', ''),
            predicted_price=prediction_result['predicted_price'],
            confidence_score=prediction_result['confidence_score']
        )
        
        # Serialize output
        output_serializer = LaptopPredictionOutputSerializer(laptop_prediction)
        
        return Response(
            {
                'success': True,
                'message': 'Prediction successful',
                'data': output_serializer.data,
                'prediction': {
                    'predicted_price': prediction_result['predicted_price'],
                    'confidence_score': prediction_result['confidence_score'],
                    'price_range': prediction_result['price_range'],
                },
                'model_info': prediction_result['model_metrics']
            },
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        return Response(
            {
                'success': False,
                'message': f'Server error: {str(e)}'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def predict_smartphone_price(request):
    """Predict smartphone resale price"""
    if smartphone_predictor is None:
        return Response(
            {
                'success': False,
                'message': 'Smartphone model not loaded. Please run train_smartphone_model.py and restart the server.'
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    try:
        # Validate input
        input_serializer = SmartphonePredictionInputSerializer(data=request.data)
        
        if not input_serializer.is_valid():
            return Response(
                {
                    'success': False,
                    'message': 'Invalid input data',
                    'errors': input_serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data = input_serializer.validated_data

        # Make prediction
        try:
            prediction_result = smartphone_predictor.predict(data)
        except Exception as e:
            return Response(
                {
                    'success': False,
                    'message': f'Prediction error: {str(e)}',
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Get user if authenticated
        user = None
        if request.user.is_authenticated:
            user = request.user
        
        # Save prediction to database
        smartphone_prediction = SmartphonePrediction.objects.create(
            user=user,
            brand=data.get('brand'),
            model=data.get('model'),
            launch_year=data.get('launch_year'),
            launch_price=data.get('launch_price'),
            processor=data.get('processor'),
            ram=data.get('ram_gb'),
            storage=data.get('storage_gb'),
            battery_capacity=data.get('battery_percentage'),
            screen_size=data.get('display_size_inch'),
            camera_mp=data.get('camera_rear_mp'),
            camera_front_mp=data.get('camera_front_mp'),
            display_type=data.get('display_type'),
            supports_5g=data.get('supports_5g', False),
            condition=data.get('condition'),
            warranty_remaining=data.get('warranty_months'),
            battery_health=data.get('battery_health'),
            seller_location=data.get('seller_location', ''),
            seller_type=data.get('seller_type', ''),
            accessories=data.get('accessories', ''),
            screen_cracked=data.get('screen_cracked', False),
            body_damage=data.get('body_damage', False),
            predicted_price=prediction_result['predicted_price'],
            confidence_score=prediction_result['confidence_score']
        )
        
        # Serialize output
        output_serializer = SmartphonePredictionOutputSerializer(smartphone_prediction)
        
        return Response(
            {
                'success': True,
                'message': 'Prediction successful',
                'data': output_serializer.data,
                'prediction': prediction_result,
                'model_info': prediction_result['model_metrics']
            },
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        return Response(
            {
                'success': False,
                'message': f'Server error: {str(e)}'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_prediction_history(request):
    """Get user's prediction history"""
    try:
        if not request.user.is_authenticated:
            return Response(
                {
                    'success': False,
                    'message': 'Authentication required'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Get user's predictions
        laptop_predictions = LaptopPrediction.objects.filter(user=request.user).order_by('-created_at')[:20]
        smartphone_predictions = SmartphonePrediction.objects.filter(user=request.user).order_by('-created_at')[:20]
        
        # Serialize
        laptop_serializer = LaptopPredictionOutputSerializer(laptop_predictions, many=True)
        smartphone_serializer = SmartphonePredictionOutputSerializer(smartphone_predictions, many=True)
        
        return Response(
            {
                'success': True,
                'data': {
                    'laptop_predictions': laptop_serializer.data,
                    'smartphone_predictions': smartphone_serializer.data,
                    'total_predictions': laptop_predictions.count() + smartphone_predictions.count()
                }
            },
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        return Response(
            {
                'success': False,
                'message': f'Server error: {str(e)}'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_model_info(request):
    """Get ML model information"""
    try:
        laptop_info = laptop_predictor.get_model_info() if laptop_predictor else None
        smartphone_info = smartphone_predictor.get_model_info() if smartphone_predictor else None
        
        if not laptop_info and not smartphone_info:
            return Response(
                {
                    'success': False,
                    'message': 'No models are currently loaded. Please train the models first.'
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        return Response(
            {
                'success': True,
                'data': {
                    'laptop': laptop_info,
                    'smartphone': smartphone_info
                }
            },
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        return Response(
            {
                'success': False,
                'message': f'Server error: {str(e)}'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_brands_and_specs(request):
    """Get common laptop brands and specifications for form dropdowns"""
    try:
        brands = [
            'HP', 'Dell', 'Lenovo', 'Asus', 'Acer', 'Apple', 'MSI',
            'Samsung', 'Microsoft', 'LG', 'Razer', 'Alienware', 'Other'
        ]
        
        processors = [
            'Intel Core i3', 'Intel Core i5', 'Intel Core i7', 'Intel Core i9',
            'AMD Ryzen 3', 'AMD Ryzen 5', 'AMD Ryzen 7', 'AMD Ryzen 9',
            'Apple M1', 'Apple M2', 'Apple M3', 'Other'
        ]
        
        gpus = [
            'Intel Integrated Graphics', 'Intel Iris Xe Graphics',
            'NVIDIA GeForce GTX 1650', 'NVIDIA GeForce RTX 3050',
            'NVIDIA GeForce RTX 3060', 'NVIDIA GeForce RTX 4050',
            'AMD Radeon Graphics', 'AMD Radeon RX 6500M',
            'Apple GPU', 'Other'
        ]
        
        ram_options = [4, 8, 16, 32, 64]
        storage_options = [128, 256, 512, 1024, 2048]
        screen_sizes = [13.3, 14.0, 15.6, 16.0, 17.3]
        
        conditions = ['Excellent', 'Good', 'Average', 'Poor']
        
        return Response(
            {
                'success': True,
                'data': {
                    'brands': brands,
                    'processors': processors,
                    'gpus': gpus,
                    'ram_options': ram_options,
                    'storage_options': storage_options,
                    'storage_types': ['SSD', 'HDD', 'Hybrid'],
                    'screen_sizes': screen_sizes,
                    'conditions': conditions
                }
            },
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        return Response(
            {
                'success': False,
                'message': f'Server error: {str(e)}'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def check_imei(request):
    """
    Check IMEI and return device specifications.
    For this project, we are using a mock database of valid IMEIs.
    """
    try:
        imei = request.data.get('imei')
        
        if not imei:
            return Response(
                {
                    'success': False,
                    'message': 'IMEI number is required'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Basic validation (15 digits usually)
        if not str(imei).isdigit() or len(str(imei)) < 14:
             return Response(
                {
                    'success': False,
                    'message': 'Invalid IMEI format. Value must be at least 14 digits.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        specs = get_specs_from_imei(imei)
        
        if specs:
            return Response(
                {
                    'success': True,
                    'message': 'Device details found',
                    'data': specs
                },
                status=status.HTTP_200_OK
            )
        else:
             return Response(
                {
                    'success': False,
                    'message': 'IMEI not found in database. Please enter details manually.',
                    'data': None # Explicitly return null data so frontend knows to ask for manual input
                },
                status=status.HTTP_404_NOT_FOUND
            )

    except Exception as e:
        return Response(
            {
                'success': False,
                'message': f'Server error: {str(e)}'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
def create_listing(request):
    """Create a new sell listing"""
    try:
        if not request.user.is_authenticated:
            return Response(
                {
                    'success': False,
                    'message': 'Authentication required to create a listing'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        data = request.data.copy()
        data['seller'] = request.user.id
        
        # Link to prediction if provided
        smartphone_pred_id = data.get('smartphone_prediction')
        laptop_pred_id = data.get('laptop_prediction')
        
        # Simple validation ensuring one is present if needed, though models handle nullable.
        # Ideally we want to link it to the prediction the user just saw.
        
        # Images are expected in request.FILES
        # DRF ModelSerializer handles file uploads if they are in request.data/request.FILES
        
        serializer = ListingSerializer(data=data)
        if serializer.is_valid():
            serializer.save(seller=request.user)
            return Response(
                {
                    'success': True,
                    'message': 'Listing created successfully',
                    'data': serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {
                    'success': False,
                    'message': 'Invalid listing data',
                    'errors': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

    except Exception as e:
        return Response(
            {
                'success': False,
                'message': f'Server error: {str(e)}'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

from .models import Listing

@api_view(['GET'])
def get_user_listings(request):
    """Get listings created by the current user"""
    try:
        if not request.user.is_authenticated:
            return Response(
                {
                    'success': False,
                    'message': 'Authentication required'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        listings = Listing.objects.filter(seller=request.user).order_by('-created_at')
        serializer = ListingSerializer(listings, many=True)
        
        return Response(
            {
                'success': True,
                'data': serializer.data
            },
            status=status.HTTP_200_OK
        )

    except Exception as e:
        return Response(
            {
                'success': False,
                'message': f'Server error: {str(e)}'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_active_listings(request):
    """Get all active listings with filtering"""
    try:
        listings = Listing.objects.all().order_by('-created_at')
        
        # Filter by device type
        device_type = request.query_params.get('type')
        if device_type:
            listings = listings.filter(device_type=device_type)
            
        # Filter by brand
        brand = request.query_params.get('brand')
        if brand and brand != 'All':
            listings = listings.filter(brand__iexact=brand)
            
        # Filter by price range
        min_price = request.query_params.get('min_price')
        if min_price:
            listings = listings.filter(expected_price__gte=min_price)
            
        max_price = request.query_params.get('max_price')
        if max_price:
            listings = listings.filter(expected_price__lte=max_price)

        serializer = ListingSerializer(listings, many=True)
        
        return Response(
            {
                'success': True,
                'data': serializer.data
            },
            status=status.HTTP_200_OK
        )

    except Exception as e:
        return Response(
            {
                'success': False,
                'message': f'Server error: {str(e)}'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_listing_details(request, pk):
    """Get single listing details"""
    try:
        try:
            listing = Listing.objects.get(pk=pk)
        except Listing.DoesNotExist:
             return Response(
                {
                    'success': False,
                    'message': 'Listing not found'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ListingSerializer(listing)
        
        return Response(
            {
                'success': True,
                'data': serializer.data
            },
            status=status.HTTP_200_OK
        )

    except Exception as e:
        return Response(
            {
                'success': False,
                'message': f'Server error: {str(e)}'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['DELETE'])
def delete_listing(request, pk):
    """Delete a listing"""
    try:
        if not request.user.is_authenticated:
             return Response({'success': False, 'message': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
             
        try:
            listing = Listing.objects.get(pk=pk)
        except Listing.DoesNotExist:
             return Response({'success': False, 'message': 'Listing not found'}, status=status.HTTP_404_NOT_FOUND)
             
        if listing.seller != request.user:
            return Response({'success': False, 'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
            
        listing.delete()
        return Response({'success': True, 'message': 'Listing deleted'}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'success': False, 'message': f'Server error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
def update_listing_status(request, pk):
    """Update listing status"""
    try:
        if not request.user.is_authenticated:
             return Response({'success': False, 'message': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
             
        try:
            listing = Listing.objects.get(pk=pk)
        except Listing.DoesNotExist:
             return Response({'success': False, 'message': 'Listing not found'}, status=status.HTTP_404_NOT_FOUND)
             
        if listing.seller != request.user:
            return Response({'success': False, 'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
            
        new_status = request.data.get('status')
        if new_status not in ['active', 'sold', 'inactive']:
             return Response({'success': False, 'message': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
             
        listing.status = new_status
        listing.save()
        
        return Response({'success': True, 'message': 'Status updated'}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'success': False, 'message': f'Server error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ==================== MESSAGING VIEWS ====================

@api_view(['POST'])
def start_conversation(request, listing_id):
    """Start or get existing conversation for a listing"""
    try:
        print(f"[DEBUG] Starting conversation for listing {listing_id}")
        print(f"[DEBUG] User authenticated: {request.user.is_authenticated}")
        print(f"[DEBUG] User: {request.user}")
        
        if not request.user.is_authenticated:
            return Response({'success': False, 'message': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            listing = Listing.objects.get(pk=listing_id)
            print(f"[DEBUG] Listing found: {listing}")
        except Listing.DoesNotExist:
            return Response({'success': False, 'message': 'Listing not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Prevent seller from messaging themselves
        if listing.seller == request.user:
            return Response({'success': False, 'message': 'You cannot message yourself'}, status=status.HTTP_400_BAD_REQUEST)
        
        print(f"[DEBUG] Creating conversation - Buyer: {request.user}, Seller: {listing.seller}")
        
        # Get or create conversation
        conversation, created = Conversation.objects.get_or_create(
            listing=listing,
            buyer=request.user,
            seller=listing.seller
        )
        
        print(f"[DEBUG] Conversation created/found: {conversation.id}, Created: {created}")
        
        try:
            serializer = ConversationSerializer(conversation, context={'request': request})
            data = serializer.data
            print(f"[DEBUG] Serialization successful")
        except Exception as e:
            print(f"[ERROR] Serialization failed: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
        
        return Response({
            'success': True,
            'data': data,
            'created': created
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        print(f"[ERROR] Exception in start_conversation: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({'success': False, 'message': f'Server error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_conversations(request):
    """Get all conversations for the authenticated user"""
    try:
        if not request.user.is_authenticated:
            return Response({'success': False, 'message': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Get conversations where user is either buyer or seller
        from django.db import models as db_models
        conversations = Conversation.objects.filter(
            db_models.Q(buyer=request.user) | db_models.Q(seller=request.user)
        ).select_related('listing', 'buyer', 'seller').prefetch_related('messages')
        
        serializer = ConversationSerializer(conversations, many=True, context={'request': request})
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({'success': False, 'message': f'Server error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_conversation_messages(request, conversation_id):
    """Get all messages in a conversation"""
    try:
        if not request.user.is_authenticated:
            return Response({'success': False, 'message': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            conversation = Conversation.objects.get(pk=conversation_id)
        except Conversation.DoesNotExist:
            return Response({'success': False, 'message': 'Conversation not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Verify user is part of conversation
        if conversation.buyer != request.user and conversation.seller != request.user:
            return Response({'success': False, 'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        messages = conversation.messages.all()
        serializer = MessageSerializer(messages, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({'success': False, 'message': f'Server error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PATCH'])
def mark_messages_read(request, conversation_id):
    """Mark all messages in a conversation as read"""
    try:
        if not request.user.is_authenticated:
            return Response({'success': False, 'message': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            conversation = Conversation.objects.get(pk=conversation_id)
        except Conversation.DoesNotExist:
            return Response({'success': False, 'message': 'Conversation not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Verify user is part of conversation
        if conversation.buyer != request.user and conversation.seller != request.user:
            return Response({'success': False, 'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        # Mark all messages from the other user as read
        updated_count = conversation.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
        
        return Response({
            'success': True,
            'message': f'{updated_count} messages marked as read'
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({'success': False, 'message': f'Server error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
