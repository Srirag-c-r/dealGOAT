from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class LaptopPrediction(models.Model):
    """Model to store laptop price predictions"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='laptop_predictions',
        null=True,
        blank=True
    )
    
    # Basic Information
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=200, blank=True)
    launch_year = models.IntegerField()
    launch_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Hardware Specifications
    processor = models.CharField(max_length=50)
    ram = models.IntegerField()  # in GB
    storage_type = models.CharField(max_length=50)
    storage_size = models.IntegerField()  # in GB
    gpu = models.CharField(max_length=200)
    screen_size = models.DecimalField(max_digits=4, decimal_places=2)
    
    # Condition & Usage
    battery_cycle_count = models.IntegerField(null=True, blank=True)
    condition = models.CharField(max_length=50)
    warranty_remaining = models.IntegerField()  # in months
    
    # Location
    seller_location = models.CharField(max_length=100, blank=True)
    
    # Prediction Results
    predicted_price = models.DecimalField(max_digits=10, decimal_places=2)
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'laptop_predictions'
        verbose_name = 'Laptop Prediction'
        verbose_name_plural = 'Laptop Predictions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['brand']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.brand} {self.model} - ₹{self.predicted_price}"
    
    def get_depreciation_percentage(self):
        """Calculate depreciation percentage"""
        if self.launch_price > 0:
            return ((float(self.launch_price) - float(self.predicted_price)) / float(self.launch_price)) * 100
        return 0


class SmartphonePrediction(models.Model):
    """Model to store smartphone price predictions"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='smartphone_predictions',
        null=True,
        blank=True
    )
    
    # Basic Information
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=200)
    launch_year = models.IntegerField()
    launch_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Hardware Specifications
    processor = models.CharField(max_length=100)
    ram = models.IntegerField()  # in GB
    storage = models.IntegerField()  # in GB
    battery_capacity = models.IntegerField()  # repurposed to store battery percentage
    screen_size = models.DecimalField(max_digits=3, decimal_places=1)
    camera_mp = models.IntegerField()  # rear camera MP
    camera_front_mp = models.IntegerField(null=True, blank=True)
    display_type = models.CharField(max_length=50, blank=True)
    supports_5g = models.BooleanField(default=False)
    
    # Condition & Usage
    condition = models.CharField(max_length=50)
    warranty_remaining = models.IntegerField()  # in months
    battery_health = models.IntegerField()  # percentage
    
    # Location
    seller_location = models.CharField(max_length=100, blank=True)
    seller_type = models.CharField(max_length=50, blank=True)
    accessories = models.CharField(max_length=200, blank=True)
    screen_cracked = models.BooleanField(default=False)
    body_damage = models.BooleanField(default=False)
    
    # Prediction Results
    predicted_price = models.DecimalField(max_digits=10, decimal_places=2)
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'smartphone_predictions'
        verbose_name = 'Smartphone Prediction'
        verbose_name_plural = 'Smartphone Predictions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['brand']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.brand} {self.model} - ₹{self.predicted_price}"
    
    def get_depreciation_percentage(self):
        """Calculate depreciation percentage"""
        if self.launch_price > 0:
            return ((float(self.launch_price) - float(self.predicted_price)) / float(self.launch_price)) * 100
        return 0


class Listing(models.Model):
    """Model to store device sell listings"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('sold', 'Sold'),
        ('inactive', 'Inactive'),
    ]
    
    DEVICE_TYPE_CHOICES = [
        ('smartphone', 'Smartphone'),
        ('laptop', 'Laptop'),
    ]
    
    # Link to Seller
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='listings'
    )
    
    # Link to Prediction (One of these will be set)
    smartphone_prediction = models.OneToOneField(
        SmartphonePrediction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='listing'
    )
    laptop_prediction = models.OneToOneField(
        LaptopPrediction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='listing'
    )
    
    device_type = models.CharField(max_length=20, choices=DEVICE_TYPE_CHOICES)
    
    # 2. Device Ownership & Authenticity
    imei_or_serial = models.CharField(max_length=100, help_text="IMEI for phones, Serial for laptops")
    invoice_available = models.BooleanField(default=False)
    invoice_date = models.DateField(null=True, blank=True)
    
    # Laptops only fields
    laptop_repair_history = models.TextField(blank=True, help_text="Repairs done on Screen, Battery, Motherboard etc")
    
    # 3. Physical Condition Breakdown
    screen_condition = models.CharField(max_length=50, help_text="No scratches, Minor, cracks etc")
    body_condition = models.CharField(max_length=50, help_text="Like new, dents etc")
    port_condition = models.CharField(max_length=50, help_text="Working, issues etc")
    camera_condition = models.CharField(max_length=50, blank=True, null=True, help_text="For phones")
    
    # 4. Images (5 mandatory in frontend)
    image_front = models.ImageField(upload_to='listings/images/')
    image_back = models.ImageField(upload_to='listings/images/')
    image_side = models.ImageField(upload_to='listings/images/')
    image_screen_on = models.ImageField(upload_to='listings/images/')
    image_proof = models.ImageField(upload_to='listings/proofs/', help_text="Blurred IMEI/Serial photo")
    
    # 5. Price & Flexibility
    expected_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_negotiable = models.BooleanField(default=False)
    
    # 6. Selling Preferences
    delivery_option = models.CharField(max_length=50, help_text="Pickup, Ship, Meetup")
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    is_willing_to_ship = models.BooleanField(default=False)
    
    # 7. Legal & Consent
    is_legal_owner = models.BooleanField(default=False)
    is_no_issues = models.BooleanField(default=False)
    is_details_accurate = models.BooleanField(default=False)
    
    # Admin moderation fields
    moderation_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending Approval'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('flagged', 'Flagged for Review'),
        ],
        default='pending',
        help_text="Moderation status"
    )
    moderated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='moderated_listings',
        help_text="Admin who moderated this listing"
    )
    moderated_at = models.DateTimeField(null=True, blank=True)
    moderation_notes = models.TextField(blank=True, help_text="Admin notes on moderation")
    
    # Metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Listing: {self.seller.email} - {self.device_type} - {self.expected_price}"


class Conversation(models.Model):
    """Model to store conversations between buyers and sellers"""
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='conversations'
    )
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='buyer_conversations'
    )
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='seller_conversations'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_message_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'conversations'
        verbose_name = 'Conversation'
        verbose_name_plural = 'Conversations'
        ordering = ['-last_message_at']
        unique_together = ['listing', 'buyer']  # One conversation per buyer per listing
        indexes = [
            models.Index(fields=['buyer', '-last_message_at']),
            models.Index(fields=['seller', '-last_message_at']),
        ]
    
    def __str__(self):
        return f"Conversation: {self.buyer.email} <-> {self.seller.email} (Listing #{self.listing.id})"


class Message(models.Model):
    """Model to store individual messages in conversations"""
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'messages'
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
            models.Index(fields=['conversation', 'is_read']),
        ]
    
    def __str__(self):
        return f"Message from {self.sender.email} at {self.created_at}"


class FlaggedListing(models.Model):
    """Model to track flagged/reported listings for moderation"""
    
    FLAG_REASONS = [
        ('duplicate_imei', 'Duplicate IMEI/Serial'),
        ('stock_photo', 'Stock Photos Used'),
        ('suspicious_price', 'Suspicious Pricing'),
        ('fake_invoice', 'Fake Invoice'),
        ('stolen_device', 'Suspected Stolen Device'),
        ('condition_mismatch', 'Condition Misrepresentation'),
        ('spam', 'Spam/Duplicate Listing'),
        ('fraud', 'Fraudulent Activity'),
        ('other', 'Other Reason'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('under_review', 'Under Review'),
        ('resolved_approved', 'Resolved - Approved'),
        ('resolved_rejected', 'Resolved - Rejected'),
        ('resolved_fraud', 'Resolved - Marked as Fraud'),
    ]
    
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='flags'
    )
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reported_listings',
        help_text="User who reported (null for automated detection)"
    )
    flag_reason = models.CharField(max_length=50, choices=FLAG_REASONS)
    description = models.TextField(help_text="Detailed reason for flagging")
    
    # Automated detection data
    is_automated = models.BooleanField(default=False, help_text="Flagged by automated system")
    detection_data = models.JSONField(default=dict, blank=True, help_text="Automated detection details")
    
    # Review status
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_flags'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'flagged_listings'
        verbose_name = 'Flagged Listing'
        verbose_name_plural = 'Flagged Listings'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['listing', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['flag_reason']),
            models.Index(fields=['is_automated']),
        ]
    
    def __str__(self):
        return f"Flag: {self.listing.id} - {self.get_flag_reason_display()} ({self.status})"


class ModerationAction(models.Model):
    """Model to track moderation history for listings"""
    
    ACTION_TYPES = [
        ('approve', 'Approved'),
        ('reject', 'Rejected'),
        ('request_info', 'Requested Additional Information'),
        ('mark_fraud', 'Marked as Fraudulent'),
        ('edit', 'Edited Listing Details'),
        ('status_change', 'Changed Status'),
        ('unflag', 'Removed Flag'),
    ]
    
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='moderation_history'
    )
    moderator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='moderation_actions'
    )
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    notes = models.TextField(help_text="Moderator notes/reason")
    
    # Changes made
    changes = models.JSONField(default=dict, blank=True, help_text="Details of changes made")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'moderation_actions'
        verbose_name = 'Moderation Action'
        verbose_name_plural = 'Moderation Actions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['listing', '-created_at']),
            models.Index(fields=['moderator', '-created_at']),
            models.Index(fields=['action_type']),
        ]
    
    def __str__(self):
        return f"{self.moderator.email if self.moderator else 'System'} - {self.get_action_type_display()} - Listing #{self.listing.id}"

