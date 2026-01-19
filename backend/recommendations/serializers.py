from rest_framework import serializers
from .models import RequirementQuery, ProductResult

class ProductResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductResult
        fields = [
            'id', 'rank', 'product_name', 'brand', 'price',
            'amazon_link', 'flipkart_link', 'product_image',
            'match_score', 'match_reasons', 'rating', 'reviews_count'
        ]

class RequirementQuerySerializer(serializers.ModelSerializer):
    products = ProductResultSerializer(many=True, read_only=True)
    
    class Meta:
        model = RequirementQuery
        fields = [
            'id', 'requirements_text', 'parsed_requirements',
            'products', 'created_at'
        ]
        read_only_fields = ['parsed_requirements', 'products']
