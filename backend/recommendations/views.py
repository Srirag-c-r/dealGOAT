from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import RequirementQuery, ProductResult
from .serializers import RequirementQuerySerializer, ProductResultSerializer
from .llm_service import LLMService
from .scrapers import ProductSearcher
from .sidba_engine import SIDBAEngine


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def find_products(request):
    """
    Find products based on user requirements.
    
    POST /api/recommendations/find-products/
    {
        "requirements": "I need a laptop with best battery, gaming, ₹80k budget"
    }
    """
    try:
        print("[DEBUG] Received requirements:", request.data.get('requirements', ''))
        requirements_text = request.data.get('requirements', '').strip()
        
        if not requirements_text:
            return Response(
                {'error': 'Requirements text is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(requirements_text) < 10:
            return Response(
                {'error': 'Please provide more detailed requirements (at least 10 characters)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Initialize services
        llm_service = LLMService()
        product_searcher = ProductSearcher()
        sidba_engine = SIDBAEngine()
        
        # NEW: Initialize semantic matcher and partial scorer
        from .semantic_matcher import SemanticMatcher
        from .partial_match_scorer import PartialMatchScorer
        
        semantic_matcher = SemanticMatcher()
        partial_scorer = PartialMatchScorer()
        
        # Step 1: Parse requirements with LLM
        parsed_requirements = llm_service.parse_requirements(requirements_text)
        print("[DEBUG] Parsed requirements:", parsed_requirements)
        # Step 1.2: Expand requirements semantically (fix "Literal Blindness")
        print("[SEMANTIC] Expanding vague requirements to concrete specs...")
        expanded_requirements = semantic_matcher.expand_requirements(parsed_requirements)
        print("[DEBUG] Expanded requirements:", expanded_requirements)
        # Log what was inferred
        if expanded_requirements.get('_inferred_ram'):
            print(f"[SEMANTIC] Inferred minimum RAM: {expanded_requirements.get('ram_needed_gb')}GB")
        if expanded_requirements.get('_inferred_storage'):
            print(f"[SEMANTIC] Inferred minimum storage: {expanded_requirements.get('storage_needed_gb')}GB")
        # Step 1.5: Process intent with SIDBA (Intent Decomposition, Trade-offs, Persona)
        enriched_requirements = sidba_engine.process_intent(requirements_text, expanded_requirements)
        print("[DEBUG] Enriched requirements:", enriched_requirements)
        # Step 2: Generate search queries
        search_queries = llm_service.generate_search_queries(parsed_requirements)
        print("[DEBUG] Search queries:", search_queries)
        # Step 3: Search for products (use original parsed_requirements, not enriched, to avoid breaking filters)
        # The enriched requirements have extra SIDBA fields that the scraper doesn't expect
        all_products = product_searcher.search(search_queries, parsed_requirements)
        print(f"[VIEWS DEBUG] Found {len(all_products)} products from search: {[p.get('name') for p in all_products]}")
        
        if not all_products:
            # Check if there are conflicts that might explain why no products found
            conflicts = enriched_requirements.get('conflicts') or []
            if conflicts:
                high_severity_conflicts = [c for c in conflicts if c.get('severity') == 'high']
                if high_severity_conflicts:
                    return Response({
                        'error': 'No products found matching your requirements.',
                        'conflict_warning': enriched_requirements.get('tradeoff_explanation'),
                        'suggestion': 'Your requirements may conflict with current market reality. Try adjusting your priorities.'
                    }, status=status.HTTP_404_NOT_FOUND)
            
            return Response(
                {'error': 'No products found. Try different requirements.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Step 3.5: Enhance products with live prices and discount info (if available)
        # This happens before ranking so discounts can influence ranking
        if all_products:
            try:
                from .dynamic_product_manager import DynamicProductManager
                dynamic_manager = DynamicProductManager()
                
                # Update top products with live prices (sample to avoid rate limiting)
                products_to_update = all_products[:3]  # Update first 3 products
                for i, product in enumerate(products_to_update):
                    try:
                        updated = dynamic_manager.update_product_with_live_data(product)
                        all_products[i] = updated
                        # Add discount badge if on discount
                        if updated.get('discount_info', {}).get('is_discount'):
                            print(f"[VIEWS DEBUG] Product {updated.get('name')} is on {updated['discount_info']['discount_percent']}% discount!")
                    except Exception as e:
                        print(f"[VIEWS DEBUG] Error updating product price: {e}")
                        continue
            except Exception as e:
                print(f"[VIEWS DEBUG] Dynamic price updates not available: {e}")
        
        # === NEW ADVANCED FILTERING PIPELINE ===
        
        # Import validators
        from .constraint_validator import ConstraintValidator
        from .spec_verifier import SpecVerifier
        from .availability_checker import AvailabilityChecker
        
        constraint_validator = ConstraintValidator()
        spec_verifier = SpecVerifier()
        availability_checker = AvailabilityChecker()
        
        print(f"[FILTERING] Starting with {len(all_products)} products")
        
        # STAGE 1: Hard Constraint Filtering (Budget, Negative Constraints, Min Specs)
        print("[FILTERING] Stage 1: Hard Constraints")
        constraint_filtered = []
        constraint_violations_summary = []
        
        for product in all_products:
            is_valid, violations = constraint_validator.validate_product(product, parsed_requirements)
            if is_valid:
                constraint_filtered.append(product)
            else:
                constraint_violations_summary.append({
                    'product': product.get('name', 'Unknown'),
                    'violations': violations
                })
        print(f"[DEBUG] After constraint filtering: {len(constraint_filtered)} products remain. Violations: {constraint_violations_summary}")
        
        print(f"[FILTERING] After constraints: {len(constraint_filtered)} products (rejected {len(all_products) - len(constraint_filtered)})")
        
        if not constraint_filtered:
            # All products violated constraints - return error with explanation
            return Response({
                'error': 'No products match your hard requirements',
                'violations': constraint_violations_summary[:3],  # Show top 3 violations
                'suggestion': 'Try relaxing your budget or removing some constraints'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # STAGE 2: Spec Verification (Credibility Scoring)
        print("[FILTERING] Stage 2: Spec Verification")
        verified_products = []
        
        for product in constraint_filtered:
            verification = spec_verifier.verify_product(product)
            product_copy = product.copy()
            product_copy['verification'] = verification
            # Only keep products with credibility >= 40 (filter out obvious spam)
            if verification['credibility_score'] >= 40:
                verified_products.append(product_copy)
            else:
                print(f"[FILTERING] Rejected spam: {product.get('name')} (credibility: {verification['credibility_score']})")
        print(f"[DEBUG] After verification: {len(verified_products)} products remain.")
        
        print(f"[FILTERING] After verification: {len(verified_products)} products")
        
        # STAGE 3: Availability Check (for top products only, to save time)
        print("[FILTERING] Stage 3: Availability Check")
        available_products = availability_checker.batch_check_availability(verified_products, max_checks=5)
        # Filter out definitely unavailable products
        available_products = availability_checker.filter_unavailable_products(available_products)
        print(f"[DEBUG] After availability check: {len(available_products)} products remain.")
        
        if not available_products:
            print("[VIEWS DEBUG] WARNING: Availability check removed all products. Returning verified products as fallback.")
            available_products = verified_products.copy()
            # Optionally, you can add a flag to the response to indicate fallback was used.
            # If you want to show a warning to the user, you can add a field in the response below.
        
        # STAGE 3.5: Semantic Spec Inference (fix missing specs)
        print("[SEMANTIC] Inferring missing specs from brand knowledge...")
        for product in available_products:
            # Infer specs from brand (e.g., ThinkPad → keyboard_travel: 1.5mm)
            inferred_product = semantic_matcher.infer_missing_specs(product)
            product.update(inferred_product)
            # Validate capability claims (e.g., "AI laptop" with 4GB RAM = spam)
            for claim in ['ai', 'gaming', 'professional', 'video editing']:
                if not semantic_matcher.validate_capability_claim(product, claim):
                    # Penalize false claims
                    if 'verification' in product:
                        product['verification']['credibility_score'] -= 20
                        product['verification']['red_flags'].append(f"False '{claim}' claim")
        print(f"[DEBUG] After semantic spec inference: {len(available_products)} products remain.")
        
        # STAGE 4: Partial Match Scoring (fix "Zero-Match Error")
        print("[PARTIAL MATCH] Calculating match percentages...")
        scored_products = []
        
        for product in available_products:
            # Calculate partial match score
            match_info = partial_scorer.calculate_match_score(
                product, enriched_requirements, semantic_matcher
            )
            product_copy = product.copy()
            product_copy['match_info'] = match_info
            product_copy['match_percentage'] = match_info['overall_percentage']
            product_copy['match_tier'] = match_info['tier']
            # Only keep products that should be shown
            if match_info['should_show']:
                scored_products.append(product_copy)
        print(f"[DEBUG] After partial match scoring: {len(scored_products)} products remain.")
        
        print(f"[PARTIAL MATCH] {len(scored_products)} products with >= 60% match")
        
        # Graceful degradation: If too few results, relax to partial matches
        perfect_and_high = [p for p in scored_products if p['match_tier'] in ['perfect_match', 'high_match']]
        
        if len(perfect_and_high) < 3:
            print(f"[FALLBACK] Only {len(perfect_and_high)} high matches, including partial matches...")
            # Include partial matches
            results_to_rank = scored_products
        else:
            # Enough high matches, only use those
            results_to_rank = perfect_and_high
        
        if not results_to_rank:
            return Response({
                'error': 'No products match your requirements',
                'suggestion': 'Try relaxing some requirements or increasing your budget',
                'debug_info': {
                    'total_products_checked': len(available_products),
                    'best_match_percentage': max([p.get('match_percentage', 0) for p in scored_products]) if scored_products else 0
                }
            }, status=status.HTTP_404_NOT_FOUND)
        
        # STAGE 5: Ranking with Enhanced Scoring
        print("[FILTERING] Stage 5: Ranking")
        ranked_products = llm_service.rank_products(enriched_requirements, results_to_rank)
        
        # Boost scores based on credibility, availability, AND partial match percentage
        for product in ranked_products:
            base_score = product.get('match_score', 50)
            
            # Partial match bonus (0-30 points based on match percentage)
            match_percentage = product.get('match_percentage', 100)
            if match_percentage >= 95:
                match_bonus = 30  # Perfect match
            elif match_percentage >= 75:
                match_bonus = 20  # High match
            else:
                match_bonus = 10  # Partial match
            
            # Credibility bonus (0-20 points)
            credibility = product.get('verification', {}).get('credibility_score', 60)
            credibility_bonus = (credibility - 60) / 2  # 80 credibility = +10 points
            
            # Availability bonus (0-10 points)
            availability = product.get('availability_info', {})
            if availability.get('status') == 'in_stock':
                availability_bonus = 10
            elif availability.get('is_available'):
                availability_bonus = 5
            else:
                availability_bonus = 0
            
            # Final score (including partial match bonus)
            product['match_score'] = min(100, base_score + match_bonus + credibility_bonus + availability_bonus)
        
        # Re-sort by final score
        ranked_products.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        
        print(f"[DEBUG] After ranking: {len(ranked_products)} products remain.")
        
        if not ranked_products:
            print("[VIEWS DEBUG] WARNING: Ranking returned no products, using verified products")
            ranked_products = verified_products[:5]
            for product in ranked_products:
                product['match_score'] = 70.0
                product['match_reasons'] = ['Matches requirements']
        
        # STAGE 5: SIDBA Enhancement
        print("[FILTERING] Stage 5: SIDBA Enhancement")
        enhanced_products = sidba_engine.enhance_product_explanations(ranked_products, enriched_requirements)
        
        print(f"[VIEWS DEBUG] Final results: {len(enhanced_products)} products")
        
        # Step 5: Save to database
        query_obj = RequirementQuery.objects.create(
            user=request.user,
            requirements_text=requirements_text,
            parsed_requirements=enriched_requirements,  # Save enriched requirements
            results=[p for p in enhanced_products]  # Save enhanced products
        )
        
        # Save individual product results
        for i, product in enumerate(enhanced_products, 1):
            # Store discount_info and other dynamic data in match_reasons JSON field
            match_reasons = product.get('match_reasons', product.get('sidba_explanations', {}).get('why_this_product', []))
            
            # Add discount info to match_reasons if available
            if product.get('discount_info'):
                if not isinstance(match_reasons, list):
                    match_reasons = []
                # Store discount info separately in a metadata field
                product_metadata = {
                    'discount_info': product.get('discount_info'),
                    'price_updated_at': product.get('price_updated_at'),
                    'live_price': product.get('live_price'),
                    'original_price': product.get('original_price'),
                    'price_changed': product.get('price_changed', False)
                }
            else:
                product_metadata = {}
            
            ProductResult.objects.create(
                query=query_obj,
                rank=i,
                product_name=product.get('name', 'Unknown'),
                brand=product.get('brand', 'Unknown'),
                price=product.get('price', product.get('live_price', 0)),  # Use live_price if available
                amazon_link=product.get('amazon_link', ''),
                flipkart_link=product.get('flipkart_link', ''),
                product_image=product.get('image', ''),
                match_score=product.get('match_score', 0),
                match_reasons={
                    'reasons': match_reasons if isinstance(match_reasons, list) else [match_reasons],
                    'metadata': product_metadata  # Store discount info here
                },
                rating=product.get('rating', 0),
                reviews_count=product.get('reviews_count', 0)
            )
        
        # Serialize and return
        serializer = RequirementQuerySerializer(query_obj)
        return Response({
            'success': True,
            'message': 'Found best products matching your needs',
            'query': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        import traceback
        print(f"Error in find_products: {str(e)}")
        traceback.print_exc()
        return Response(
            {'error': f'An error occurred: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def query_history(request):
    """Get user's search history"""
    try:
        queries = RequirementQuery.objects.filter(user=request.user)
        serializer = RequirementQuerySerializer(queries, many=True)
        return Response({
            'success': True,
            'queries': serializer.data
        })
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def query_detail(request, query_id):
    """Get detailed results for a specific query"""
    try:
        query_obj = get_object_or_404(RequirementQuery, id=query_id, user=request.user)
        serializer = RequirementQuerySerializer(query_obj)
        return Response({
            'success': True,
            'query': serializer.data
        })
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
