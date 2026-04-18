import pandas as pd
import random
from datetime import datetime, timedelta

class ReviewAPIExtractor:
    """Extract realistic reviews from various sources (simulated but realistic)"""
    
    def __init__(self):
        self.sources = ['Amazon', 'Flipkart', 'Google', 'Twitter']
        
        # Realistic review templates based on product type
        self.review_templates = {
            'phone': [
                "The {feature} is {sentiment}! Best phone I've ever used.",
                "Battery life is {sentiment}, lasts {duration} hours on a single charge.",
                "Camera quality is {sentiment}. Photos look {quality}.",
                "The display is {sentiment}. Colors are {quality} and bright.",
                "Phone heats up {intensity} while gaming.",
                "Software is {sentiment}. Has some {issue} issues.",
                "Value for money? {sentiment_opinion}. Worth every rupee.",
                "{feature} could be better. Not satisfied with the {issue}."
            ],
            'headphones': [
                "Sound quality is {sentiment}! Bass is {quality}.",
                "Battery lasts {duration} hours. {sentiment_opinion}.",
                "Comfort level is {sentiment}. Can wear for {duration} hours.",
                "Noise cancellation is {sentiment}. Works {quality}.",
                "Connectivity has {issue} issues. Keeps disconnecting.",
                "Build quality feels {quality}. {sentiment_opinion} for the price."
            ],
            'speaker': [
                "Sound quality is {sentiment}! {quality} bass and treble.",
                "Volume level is {sentiment}. Gets {intensity} loud.",
                "Battery backup is {sentiment}. Lasts {duration} hours.",
                "Bluetooth connectivity has {issue} problems.",
                "Portable and {quality}. Easy to carry around.",
                "Value for money? {sentiment_opinion}. Highly recommended."
            ],
            'laptop': [
                "Performance is {sentiment}! Handles {task} smoothly.",
                "Battery backup is {sentiment}. Lasts {duration} hours.",
                "Display quality is {sentiment}. {quality} for work.",
                "Heating issue is {intensity}. Gets hot during {task}.",
                "Build quality feels {quality}. {sentiment_opinion}.",
                "Keyboard and trackpad are {sentiment}. {quality} experience."
            ],
            'default': [
                "The {feature} is {sentiment}! Very {quality} experience.",
                "Product quality is {sentiment}. {sentiment_opinion} the purchase.",
                "Delivery was {sentiment}. Reached in {duration} days.",
                "Customer service is {sentiment}. They were {quality}.",
                "Value for money? {sentiment_opinion}. Would {recommend} recommend.",
                "Packaging was {sentiment}. Product arrived in {quality} condition."
            ]
        }
    
    def _detect_product_category(self, product_name):
        """Detect product category from name"""
        product_lower = product_name.lower()
        
        if any(word in product_lower for word in ['phone', 'mobile', 'smartphone', 'iphone', 'android', 'pixel', 'galaxy', 'oneplus', 'mi', 'redmi']):
            return 'phone'
        elif any(word in product_lower for word in ['headphone', 'earphone', 'earbud', 'airpod', 'neckband', 'headset']):
            return 'headphones'
        elif any(word in product_lower for word in ['speaker', 'soundbar', 'bluetooth speaker']):
            return 'speaker'
        elif any(word in product_lower for word in ['laptop', 'notebook', 'macbook', 'dell', 'hp', 'lenovo', 'asus', 'acer']):
            return 'laptop'
        else:
            return 'default'
    
    def _generate_realistic_review(self, product_name, source, rating):
        """Generate a realistic review based on product name and rating"""
        
        category = self._detect_product_category(product_name)
        templates = self.review_templates.get(category, self.review_templates['default'])
        
        # Sentiment based on rating
        if rating >= 4:
            sentiments = ['amazing', 'excellent', 'great', 'fantastic', 'superb', 'outstanding']
            sentiment_opinions = ['Definitely worth it', 'Highly recommended', 'Best purchase ever', 'Very satisfied']
            qualities = ['premium', 'excellent', 'top-notch', 'impressive']
            intensities = ['not much', 'barely noticeable']
            durations = [8, 10, 12, 15, 20, 24]
            tasks = ['multitasking', 'heavy usage', 'gaming', 'video editing']
            recommend = 'definitely'
            issues = ['minor', 'rare']
        elif rating == 3:
            sentiments = ['average', 'okay', 'decent', 'fair', 'reasonable']
            sentiment_opinions = ['Average value', 'Could be better', 'Okay for the price', 'Not great but not bad']
            qualities = ['decent', 'acceptable', 'fair', 'mediocre']
            intensities = ['moderately', 'noticeably']
            durations = [4, 5, 6, 7]
            tasks = ['normal use', 'regular tasks']
            recommend = 'maybe'
            issues = ['some', 'occasional']
        else:
            sentiments = ['terrible', 'poor', 'bad', 'disappointing', 'horrible', 'worst']
            sentiment_opinions = ['Complete waste of money', 'Very disappointed', 'Not recommended at all', 'Avoid this product']
            qualities = ['cheap', 'poor', 'low', 'bad']
            intensities = ['very much', 'extremely', 'severely']
            durations = [1, 2, 3]
            tasks = ['light use', 'basic tasks']
            recommend = 'not'
            issues = ['frequent', 'constant', 'major']
        
        template = random.choice(templates)
        
        # Generate review text
        review_text = template.format(
            feature=random.choice(['Battery', 'Display', 'Sound quality', 'Build quality', 'Performance', 'Camera', 'Software']),
            sentiment=random.choice(sentiments),
            quality=random.choice(qualities),
            duration=random.choice(durations),
            sentiment_opinion=random.choice(sentiment_opinions),
            intensity=random.choice(intensities),
            issue=random.choice(issues),
            task=random.choice(tasks),
            recommend=recommend
        )
        
        # Add source-specific prefix
        if source == 'Amazon':
            prefix = random.choice(["Verified Purchase: ", "⭐⭐⭐ ", "Update after 1 week: ", ""])
            review_text = prefix + review_text
        elif source == 'Flipkart':
            prefix = random.choice(["Flipkart Verified: ", "★★★★ ", "After 2 weeks of use: ", ""])
            review_text = prefix + review_text
        elif source == 'Twitter':
            review_text = f"Just bought {product_name}! {review_text[:80]}... #Review #{product_name.replace(' ', '')}"
        elif source == 'Google':
            review_text = f"⭐ {rating} star review: {review_text}"
        
        return review_text
    
    def _generate_realistic_reviews_batch(self, product_name, source, count):
        """Generate a batch of realistic reviews"""
        reviews = []
        
        # Generate rating distribution (more 4-5 stars for good products, mixed for others)
        rating_distribution = [5, 4, 4, 3, 3, 2, 1, 5, 4, 5, 4, 3, 4, 5, 2, 3, 4, 5, 1, 4]
        
        for i in range(count):
            rating = random.choice(rating_distribution)
            
            review_text = self._generate_realistic_review(product_name, source, rating)
            
            # Generate date within last 30 days
            date = datetime.now() - timedelta(days=random.randint(0, 30))
            
            # Generate time
            time_str = f"{random.randint(0, 23):02d}:{random.randint(0, 59):02d}:{random.randint(0, 59):02d}"
            
            # Region based on source
            regions = ['North', 'South', 'East', 'West']
            region = random.choice(regions)
            
            review = {
                'review_text': review_text,
                'product_name': product_name,
                'source': source,
                'rating': rating,
                'date': date.strftime('%Y-%m-%d'),
                'time': time_str,
                'datetime': date.strftime(f'%Y-%m-%d {time_str}'),
                'region': region,
                'helpful_count': random.randint(0, 50),
                'verified_purchase': random.choice([True, False])
            }
            
            reviews.append(review)
        
        return reviews
    
    def extract_from_amazon(self, product_name, count=20):
        """Extract realistic Amazon product reviews"""
        return self._generate_realistic_reviews_batch(product_name, 'Amazon', count)
    
    def extract_from_flipkart(self, product_name, count=20):
        """Extract realistic Flipkart product reviews"""
        return self._generate_realistic_reviews_batch(product_name, 'Flipkart', count)
    
    def extract_from_twitter(self, product_name, count=20):
        """Extract realistic Twitter/X reviews"""
        return self._generate_realistic_reviews_batch(product_name, 'Twitter', count)
    
    def extract_from_google(self, product_name, count=20):
        """Extract realistic Google reviews"""
        return self._generate_realistic_reviews_batch(product_name, 'Google', count)
    
    def extract_multiple_sources(self, product_name, sources, total_count=30):
        """Extract reviews from multiple sources"""
        all_reviews = []
        
        # Distribute count across sources
        per_source = max(5, total_count // len(sources))
        
        for source in sources:
            if source == 'amazon':
                reviews = self.extract_from_amazon(product_name, per_source)
            elif source == 'flipkart':
                reviews = self.extract_from_flipkart(product_name, per_source)
            elif source == 'twitter':
                reviews = self.extract_from_twitter(product_name, per_source)
            elif source == 'google':
                reviews = self.extract_from_google(product_name, per_source)
            else:
                continue
            
            all_reviews.extend(reviews)
        
        # Limit to total_count
        if len(all_reviews) > total_count:
            all_reviews = all_reviews[:total_count]
        
        return pd.DataFrame(all_reviews)
    
    def extract_from_csv_url(self, url):
        """Extract reviews from a CSV URL (for future implementation)"""
        try:
            df = pd.read_csv(url)
            return df
        except:
            return None