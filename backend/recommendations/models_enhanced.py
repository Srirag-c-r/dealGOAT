from django.db import models
from django.contrib.auth.models import User
import json
from datetime import datetime, timedelta


class UserPreferenceProfile(models.Model):
    """User preference profile for personalized recommendations"""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Device preferences
    preferred_device_types = models.JSONField(default=list, blank=True)  # ['laptop', 'phone']
    preferred_brands = models.JSONField(default=list, blank=True)  # ['Apple', 'Dell', 'ASUS']

    # Price preferences
    budget_ranges = models.JSONField(default=dict, blank=True)  # {'laptop': [50000, 100000], 'phone': [20000, 50000]}

    # Feature preferences
    preferred_features = models.JSONField(default=dict, blank=True)  # {'gaming': 0.8, 'battery': 0.6}

    # Use case preferences
    use_case_weights = models.JSONField(default=dict, blank=True)  # {'gaming': 0.9, 'coding': 0.7}

    # Performance preferences
    performance_priorities = models.JSONField(default=dict, blank=True)  # {'processor': 0.8, 'ram': 0.6}

    class Meta:
        db_table = 'user_preference_profiles'

    def update_from_search(self, requirements, selected_product):
        """Update preferences based on user search and selection"""
        # Update device type preference
        device_type = requirements.get('device_type', 'laptop')
        if device_type not in self.preferred_device_types:
            self.preferred_device_types.append(device_type)

        # Update brand preference
        brand = selected_product.get('brand')
        if brand and brand not in self.preferred_brands:
            self.preferred_brands.append(brand)

        # Update budget preferences
        budget_max = requirements.get('budget_max')
        if budget_max:
            if device_type not in self.budget_ranges:
                self.budget_ranges[device_type] = [budget_max * 0.7, budget_max * 1.3]
            else:
                # Update range based on new data
                current_range = self.budget_ranges[device_type]
                self.budget_ranges[device_type] = [
                    min(current_range[0], budget_max * 0.8),
                    max(current_range[1], budget_max * 1.2)
                ]

        # Update use case preferences
        use_cases = requirements.get('use_case', [])
        for use_case in use_cases:
            if use_case not in self.use_case_weights:
                self.use_case_weights[use_case] = 0.5
            else:
                # Increase weight for repeated use cases
                self.use_case_weights[use_case] = min(1.0, self.use_case_weights[use_case] + 0.1)

        self.save()

    def get_personalized_score(self, product, requirements):
        """Calculate personalized score for a product"""
        score = 0
        reasons = []

        # Brand preference bonus
        if product.get('brand') in self.preferred_brands:
            score += 10
            reasons.append(f"Preferred brand: {product.get('brand')}")

        # Device type preference
        device_type = requirements.get('device_type', 'laptop')
        if device_type in self.preferred_device_types:
            score += 5
            reasons.append(f"Preferred device type: {device_type}")

        # Budget alignment
        price = product.get('price', 0)
        if device_type in self.budget_ranges:
            budget_min, budget_max = self.budget_ranges[device_type]
            if budget_min <= price <= budget_max:
                score += 8
                reasons.append("Within preferred budget range")

        # Use case alignment
        use_cases = requirements.get('use_case', [])
        for use_case in use_cases:
            if use_case in self.use_case_weights:
                weight = self.use_case_weights[use_case]
                score += int(weight * 10)
                reasons.append(f"Matches preferred use case: {use_case}")

        return score, reasons


class SearchAnalytics(models.Model):
    """Analytics for search patterns and performance"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    search_query = models.TextField()
    device_type = models.CharField(max_length=20, default='laptop')
    parsed_requirements = models.JSONField(default=dict)
    results_count = models.IntegerField(default=0)
    selected_product = models.JSONField(null=True, blank=True)
    search_duration = models.FloatField(default=0)  # seconds
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'search_analytics'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['device_type', 'created_at']),
        ]

    @classmethod
    def get_popular_searches(cls, days=30):
        """Get popular search patterns"""
        since = datetime.now() - timedelta(days=days)
        return cls.objects.filter(created_at__gte=since)\
                         .values('device_type', 'search_query')\
                         .annotate(count=models.Count('id'))\
                         .order_by('-count')[:10]

    @classmethod
    def get_user_search_history(cls, user, limit=20):
        """Get user's search history"""
        return cls.objects.filter(user=user)\
                         .order_by('-created_at')[:limit]


class ProductFeedback(models.Model):
    """User feedback on recommended products"""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=200)
    product_brand = models.CharField(max_length=100)
    product_price = models.IntegerField()
    search_query = models.ForeignKey('RequirementQuery', on_delete=models.CASCADE)

    # Feedback
    rating = models.IntegerField(choices=[(1, 'Poor'), (2, 'Fair'), (3, 'Good'), (4, 'Very Good'), (5, 'Excellent')])
    would_buy = models.BooleanField(default=False)
    feedback_text = models.TextField(blank=True)

    # Why they liked/didn't like it
    liked_features = models.JSONField(default=list, blank=True)
    disliked_features = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'product_feedback'
        unique_together = ['user', 'search_query', 'product_name']

    @classmethod
    def get_product_ratings(cls):
        """Get average ratings for products"""
        return cls.objects.values('product_name', 'product_brand')\
                         .annotate(avg_rating=models.Avg('rating'),
                                 total_reviews=models.Count('id'))\
                         .order_by('-avg_rating')


class CollaborativeRecommender:
    """Simple collaborative filtering for product recommendations"""

    def __init__(self):
        self.user_item_matrix = {}
        self.item_similarity = {}

    def update_user_preferences(self, user_id, product_name, rating):
        """Update user-item matrix with new rating"""
        if user_id not in self.user_item_matrix:
            self.user_item_matrix[user_id] = {}

        self.user_item_matrix[user_id][product_name] = rating

        # Recalculate similarities when matrix changes
        self._calculate_item_similarities()

    def get_similar_products(self, product_name, limit=5):
        """Get products similar to the given product"""
        if product_name not in self.item_similarity:
            return []

        similar_items = self.item_similarity[product_name]
        return sorted(similar_items.items(), key=lambda x: x[1], reverse=True)[:limit]

    def get_user_recommendations(self, user_id, limit=5):
        """Get personalized recommendations for user"""
        if user_id not in self.user_item_matrix:
            return []

        user_ratings = self.user_item_matrix[user_id]
        recommendations = {}

        # Simple collaborative filtering
        for product, rating in user_ratings.items():
            if product in self.item_similarity:
                for similar_product, similarity in self.item_similarity[product].items():
                    if similar_product not in user_ratings:  # Not already rated
                        if similar_product not in recommendations:
                            recommendations[similar_product] = 0
                        recommendations[similar_product] += rating * similarity

        return sorted(recommendations.items(), key=lambda x: x[1], reverse=True)[:limit]

    def _calculate_item_similarities(self):
        """Calculate cosine similarity between items"""
        # Simple implementation - in production, use more sophisticated methods
        products = set()
        for user_ratings in self.user_item_matrix.values():
            products.update(user_ratings.keys())

        self.item_similarity = {}
        products_list = list(products)

        for i, product1 in enumerate(products_list):
            self.item_similarity[product1] = {}
            for j, product2 in enumerate(products_list):
                if i != j:
                    similarity = self._cosine_similarity(product1, product2)
                    if similarity > 0:
                        self.item_similarity[product1][product2] = similarity

    def _cosine_similarity(self, product1, product2):
        """Calculate cosine similarity between two products"""
        # Simple text-based similarity for now
        # In production, use more sophisticated features
        users_who_rated_both = []

        for user_id, ratings in self.user_item_matrix.items():
            if product1 in ratings and product2 in ratings:
                users_who_rated_both.append(user_id)

        if len(users_who_rated_both) < 2:
            return 0

        # Calculate similarity based on rating patterns
        ratings1 = [self.user_item_matrix[user][product1] for user in users_who_rated_both]
        ratings2 = [self.user_item_matrix[user][product2] for user in users_who_rated_both]

        # Cosine similarity
        dot_product = sum(r1 * r2 for r1, r2 in zip(ratings1, ratings2))
        norm1 = sum(r ** 2 for r in ratings1) ** 0.5
        norm2 = sum(r ** 2 for r in ratings2) ** 0.5

        return dot_product / (norm1 * norm2) if norm1 and norm2 else 0