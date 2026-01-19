from django.db import models
from django.conf import settings

class RequirementQuery(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    requirements_text = models.TextField()
    parsed_requirements = models.JSONField(default=dict)
    results = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.created_at}"

class ProductResult(models.Model):
    query = models.ForeignKey(RequirementQuery, on_delete=models.CASCADE, related_name='products')
    rank = models.IntegerField()
    
    product_name = models.CharField(max_length=1000)
    brand = models.CharField(max_length=255, blank=True)
    price = models.IntegerField(default=0)
    
    amazon_link = models.TextField(blank=True, null=True)
    flipkart_link = models.TextField(blank=True, null=True)
    product_image = models.TextField(blank=True, null=True)
    
    match_score = models.FloatField(default=0)
    match_reasons = models.JSONField(default=list)
    
    rating = models.FloatField(default=0)
    reviews_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['rank']
    
    def __str__(self):
        return f"{self.product_name} - {self.match_score}%"


class SystemMetric(models.Model):
    """Model to store system performance metrics for monitoring"""
    
    METRIC_TYPES = [
        ('counter', 'Counter'),
        ('gauge', 'Gauge'),
        ('histogram', 'Histogram'),
        ('timing', 'Timing'),
    ]
    
    metric_name = models.CharField(max_length=100, help_text="Name of the metric (e.g., api_response_time)")
    metric_value = models.FloatField(help_text="Numeric value of the metric")
    metric_type = models.CharField(max_length=20, choices=METRIC_TYPES, default='gauge')
    
    # Additional context
    metadata = models.JSONField(default=dict, blank=True, help_text="Additional metric data")
    tags = models.JSONField(default=list, blank=True, help_text="Tags for filtering (e.g., ['api', 'predictions'])")
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'system_metrics'
        verbose_name = 'System Metric'
        verbose_name_plural = 'System Metrics'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['metric_name', '-timestamp']),
            models.Index(fields=['metric_type']),
            models.Index(fields=['-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.metric_name}: {self.metric_value} ({self.timestamp})"
    
    @classmethod
    def record(cls, metric_name, metric_value, metric_type='gauge', **metadata):
        """Helper method to record a metric"""
        return cls.objects.create(
            metric_name=metric_name,
            metric_value=metric_value,
            metric_type=metric_type,
            metadata=metadata
        )


class SystemConfiguration(models.Model):
    """Model to store dynamic system settings"""
    
    VALUE_TYPES = [
        ('string', 'String'),
        ('integer', 'Integer'),
        ('float', 'Float'),
        ('boolean', 'Boolean'),
        ('json', 'JSON'),
    ]
    
    key = models.CharField(max_length=100, unique=True, help_text="Configuration key")
    value = models.TextField(help_text="Configuration value (stored as string)")
    value_type = models.CharField(max_length=20, choices=VALUE_TYPES, default='string')
    description = models.TextField(help_text="Description of this setting")
    
    # Metadata
    category = models.CharField(max_length=50, blank=True, help_text="Setting category (e.g., 'email', 'ml_model')")
    is_sensitive = models.BooleanField(default=False, help_text="Hide value in admin UI")
    
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='config_updates'
    )
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'system_configurations'
        verbose_name = 'System Configuration'
        verbose_name_plural = 'System Configurations'
        ordering = ['category', 'key']
        indexes = [
            models.Index(fields=['key']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return f"{self.key} = {self.value if not self.is_sensitive else '***'}"
    
    def get_value(self):
        """Get the typed value"""
        if self.value_type == 'integer':
            return int(self.value)
        elif self.value_type == 'float':
            return float(self.value)
        elif self.value_type == 'boolean':
            return self.value.lower() in ('true', '1', 'yes')
        elif self.value_type == 'json':
            import json
            return json.loads(self.value)
        return self.value
    
    def set_value(self, value, updated_by=None):
        """Set the typed value"""
        import json
        if self.value_type == 'json':
            self.value = json.dumps(value)
        else:
            self.value = str(value)
        
        if updated_by:
            self.updated_by = updated_by
        self.save()
    
    @classmethod
    def get_setting(cls, key, default=None):
        """Get a setting value by key"""
        try:
            config = cls.objects.get(key=key)
            return config.get_value()
        except cls.DoesNotExist:
            return default

