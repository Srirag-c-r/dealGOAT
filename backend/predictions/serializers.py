from rest_framework import serializers
from django.core.validators import RegexValidator
from .models import LaptopPrediction, SmartphonePrediction, Listing, Conversation, Message


class LaptopPredictionInputSerializer(serializers.Serializer):
    """Serializer for laptop prediction input"""
    brand = serializers.CharField(max_length=100)
    model = serializers.CharField(max_length=200, required=False, allow_blank=True)
    launch_year = serializers.IntegerField(min_value=2010, max_value=2025)
    launch_price = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    processor = serializers.CharField(max_length=50)
    ram = serializers.IntegerField(min_value=2, max_value=128)
    storage_type = serializers.ChoiceField(choices=['HDD', 'SSD', 'Hybrid'])
    storage_size = serializers.IntegerField(min_value=128, max_value=4096)
    gpu = serializers.CharField(max_length=200)
    screen_size = serializers.DecimalField(max_digits=4, decimal_places=2, min_value=10, max_value=20)
    battery_cycle_count = serializers.IntegerField(min_value=0, max_value=2000, required=False, allow_null=True)
    condition = serializers.ChoiceField(choices=['Excellent', 'Good', 'Average', 'Poor'])
    warranty_remaining = serializers.IntegerField(min_value=0, max_value=60)
    seller_location = serializers.CharField(max_length=100, required=False, allow_blank=True)


class LaptopPredictionOutputSerializer(serializers.ModelSerializer):
    """Serializer for laptop prediction output"""
    depreciation_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = LaptopPrediction
        fields = [
            'id', 'brand', 'model', 'launch_year', 'launch_price',
            'processor', 'ram', 'storage_type', 'storage_size', 'gpu',
            'screen_size', 'battery_cycle_count', 'condition',
            'warranty_remaining', 'seller_location', 'predicted_price',
            'confidence_score', 'depreciation_percentage', 'created_at'
        ]
        read_only_fields = ['id', 'predicted_price', 'confidence_score', 'created_at']
    
    def get_depreciation_percentage(self, obj):
        return round(obj.get_depreciation_percentage(), 2)


class SmartphonePredictionInputSerializer(serializers.Serializer):
    """Serializer for smartphone prediction input"""
    brand = serializers.CharField(max_length=100)
    model = serializers.CharField(max_length=200)
    launch_year = serializers.IntegerField(min_value=2015, max_value=2025)
    launch_price = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    processor = serializers.CharField(max_length=100)
    storage_gb = serializers.IntegerField(min_value=32, max_value=2048)
    ram_gb = serializers.IntegerField(min_value=1, max_value=24)
    battery_percentage = serializers.IntegerField(min_value=40, max_value=100)
    battery_health = serializers.IntegerField(min_value=40, max_value=100)
    camera_rear_mp = serializers.IntegerField(min_value=5, max_value=200)
    camera_front_mp = serializers.IntegerField(min_value=2, max_value=64)
    display_type = serializers.ChoiceField(
        choices=['AMOLED', 'OLED', 'Super AMOLED', 'LCD', 'IPS LCD', 'LTPO', 'Unknown'],
        default='AMOLED'
    )
    display_size_inch = serializers.DecimalField(max_digits=3, decimal_places=2, min_value=4.5, max_value=8.5)
    supports_5g = serializers.BooleanField(default=True)
    condition = serializers.ChoiceField(
        choices=['Like New', 'Good', 'Fair', 'Average', 'Used', 'Refurbished', 'Screen Damage', 'No Box'],
        default='Good'
    )
    warranty_months = serializers.IntegerField(min_value=0, max_value=36)
    screen_cracked = serializers.BooleanField(default=False)
    body_damage = serializers.BooleanField(default=False)
    accessories = serializers.CharField(max_length=200, required=False, allow_blank=True)
    seller_type = serializers.ChoiceField(choices=['Store', 'Refurbisher', 'Individual'])
    seller_location = serializers.CharField(max_length=100)


class SmartphonePredictionOutputSerializer(serializers.ModelSerializer):
    """Serializer for smartphone prediction output"""
    depreciation_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = SmartphonePrediction
        fields = [
            'id', 'brand', 'model', 'launch_year', 'launch_price',
            'processor', 'ram', 'storage', 'battery_capacity',
            'camera_front_mp', 'display_type', 'supports_5g',
            'screen_size', 'camera_mp', 'condition', 'warranty_remaining',
            'battery_health', 'seller_location', 'seller_type', 'accessories',
            'screen_cracked', 'body_damage', 'predicted_price',
            'confidence_score', 'depreciation_percentage', 'created_at'
        ]
        read_only_fields = ['id', 'predicted_price', 'confidence_score', 'created_at']
    
    def get_depreciation_percentage(self, obj):
        return round(obj.get_depreciation_percentage(), 2)


class PredictionHistorySerializer(serializers.Serializer):
    """Serializer for prediction history"""
    laptop_predictions = LaptopPredictionOutputSerializer(many=True, read_only=True)
    smartphone_predictions = SmartphonePredictionOutputSerializer(many=True, read_only=True)


class ListingSerializer(serializers.ModelSerializer):
    """Serializer for device lisitings"""
    seller_name = serializers.CharField(source='seller.username', read_only=True)
    seller_email = serializers.EmailField(source='seller.email', read_only=True)
    seller_profile_picture = serializers.SerializerMethodField()
    brand = serializers.SerializerMethodField()
    model = serializers.SerializerMethodField()
    specs = serializers.SerializerMethodField()
    
    # Adding validators for listing fields
    imei_or_serial = serializers.CharField(
        max_length=100,
        validators=[RegexValidator(
            regex=r'^[a-zA-Z0-9]{8,20}$',
            message="IMEI/Serial must be 8-20 alphanumeric characters."
        )]
    )
    pincode = serializers.CharField(
        max_length=10,
        validators=[RegexValidator(
            regex=r'^\d{6}$',
            message="Pincode must be exactly 6 digits."
        )]
    )

    class Meta:
        model = Listing
        fields = [
            'id', 'seller', 'seller_name', 'seller_email', 'seller_profile_picture',
            'brand', 'model', 'specs',
            'smartphone_prediction', 'laptop_prediction', 'device_type',
            'imei_or_serial', 'invoice_available', 'invoice_date',
            'laptop_repair_history', 'screen_condition', 'body_condition',
            'port_condition', 'camera_condition',
            'image_front', 'image_back', 'image_side', 'image_screen_on', 'image_proof',
            'expected_price', 'is_negotiable',
            'delivery_option', 'city', 'pincode', 'is_willing_to_ship',
            'is_legal_owner', 'is_no_issues', 'is_details_accurate',
            'status', 'created_at'
        ]
        read_only_fields = ['id', 'seller', 'status', 'created_at']
    
    def get_seller_profile_picture(self, obj):
        if obj.seller.profile_picture:
            return obj.seller.profile_picture.url
        return None

    def get_brand(self, obj):
        """Return brand from prediction"""
        try:
            if obj.device_type == 'smartphone' and obj.smartphone_prediction:
                return obj.smartphone_prediction.brand
            elif obj.device_type == 'laptop' and obj.laptop_prediction:
                return obj.laptop_prediction.brand
        except Exception:
            pass
        return None
    
    def get_model(self, obj):
        """Return model from prediction"""
        try:
            if obj.device_type == 'smartphone' and obj.smartphone_prediction:
                return obj.smartphone_prediction.model
            elif obj.device_type == 'laptop' and obj.laptop_prediction:
                return obj.laptop_prediction.model
        except Exception:
            pass
        return None
    
    def get_specs(self, obj):
        """Return key specs formatted as a string"""
        try:
            if obj.device_type == 'smartphone' and obj.smartphone_prediction:
                p = obj.smartphone_prediction
                return f"{p.ram}GB RAM / {p.storage}GB Storage"
            elif obj.device_type == 'laptop' and obj.laptop_prediction:
                p = obj.laptop_prediction
                return f"{p.processor} / {p.ram}GB RAM / {p.storage_size}GB {p.storage_type}"
        except Exception:
            pass
        return None

    def validate_expected_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        if value > 1000000:
            raise serializers.ValidationError("Price cannot exceed ₹1,000,000.")
        return value


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for messages"""
    sender_name = serializers.SerializerMethodField()
    sender_email = serializers.EmailField(source='sender.email', read_only=True)
    sender_profile_picture = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = ['id', 'conversation', 'sender', 'sender_name', 'sender_email', 'sender_profile_picture', 'content', 'created_at', 'is_read']
        read_only_fields = ['id', 'sender', 'created_at']

    def get_sender_profile_picture(self, obj):
        if obj.sender.profile_picture:
            return obj.sender.profile_picture.url
        return None

    def get_sender_name(self, obj):
        if obj.sender.first_name:
            return f"{obj.sender.first_name} {obj.sender.last_name}".strip()
        return obj.sender.email


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for conversations"""
    buyer_name = serializers.SerializerMethodField()
    seller_name = serializers.SerializerMethodField()
    buyer_profile_picture = serializers.SerializerMethodField()
    seller_profile_picture = serializers.SerializerMethodField()
    listing_title = serializers.SerializerMethodField()
    listing_image = serializers.SerializerMethodField()
    listing_price = serializers.DecimalField(source='listing.expected_price', max_digits=10, decimal_places=2, read_only=True)
    listing_type = serializers.CharField(source='listing.device_type', read_only=True)
    listing_city = serializers.CharField(source='listing.city', read_only=True)
    listing_pincode = serializers.CharField(source='listing.pincode', read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'id', 'listing', 'buyer', 'seller', 'buyer_name', 'seller_name',
            'buyer_profile_picture', 'seller_profile_picture',
            'listing_title', 'listing_image', 'listing_price', 'listing_type',
            'listing_city', 'listing_pincode',
            'last_message', 'unread_count', 'created_at', 'last_message_at'
        ]
        read_only_fields = ['id', 'created_at', 'last_message_at']
    
    def get_buyer_profile_picture(self, obj):
        if obj.buyer.profile_picture:
            return obj.buyer.profile_picture.url
        return None

    def get_seller_profile_picture(self, obj):
        if obj.seller.profile_picture:
            return obj.seller.profile_picture.url
        return None

    def get_buyer_name(self, obj):
        if obj.buyer.first_name:
            return f"{obj.buyer.first_name} {obj.buyer.last_name}".strip()
        return obj.buyer.email

    def get_seller_name(self, obj):
        if obj.seller.first_name:
            return f"{obj.seller.first_name} {obj.seller.last_name}".strip()
        return obj.seller.email

    def get_listing_title(self, obj):
        """Get listing title safely"""
        try:
            listing = obj.listing
            brand = ""
            model = ""
            
            if listing.device_type == 'smartphone' and listing.smartphone_prediction:
                brand = listing.smartphone_prediction.brand or ""
                model = listing.smartphone_prediction.model or ""
            elif listing.device_type == 'laptop' and listing.laptop_prediction:
                brand = listing.laptop_prediction.brand or ""
                model = listing.laptop_prediction.model or ""
            
            if brand or model:
                return f"{brand} {model}".strip()
            
            return listing.device_type.title() if listing.device_type else 'Device'
        except Exception:
            return 'Device'
    
    def get_listing_image(self, obj):
        """Get listing image URL safely"""
        try:
            if obj.listing.image_front:
                # Return the URL path (not .url which might fail)
                image_path = str(obj.listing.image_front)
                if image_path.startswith('http'):
                    return image_path
                return f'/media/{image_path}' if not image_path.startswith('/media/') else image_path
        except Exception:
            pass
        return None
    
    def get_last_message(self, obj):
        last_msg = obj.messages.last()
        if last_msg:
            return {
                'content': last_msg.content,
                'sender': last_msg.sender.email,
                'created_at': last_msg.created_at
            }
        return None
    
    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user:
            return obj.messages.filter(is_read=False).exclude(sender=request.user).count()
        return 0
