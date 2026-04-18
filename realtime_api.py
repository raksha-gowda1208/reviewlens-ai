import time
import random
import pandas as pd
from datetime import datetime
import threading
import queue

class ReviewStreamSimulator:
    """Simulate real-time review feed"""
    
    def __init__(self, sample_reviews=None):
        self.sample_reviews = sample_reviews or []
        self.is_streaming = False
        self.review_queue = queue.Queue()
        self.callbacks = []
        
    def add_sample_reviews(self, reviews_df):
        """Load sample reviews for streaming"""
        self.sample_reviews = reviews_df.to_dict('records')
    
    def start_streaming(self, interval_seconds=2):
        """Start simulating real-time review feed"""
        self.is_streaming = True
        
        def stream_generator():
            idx = 0
            while self.is_streaming:
                if self.sample_reviews:
                    review = self.sample_reviews[idx % len(self.sample_reviews)].copy()
                    review['timestamp'] = datetime.now().isoformat()
                    review['stream_id'] = f"stream_{int(time.time())}_{idx}"
                    
                    self.review_queue.put(review)
                    for callback in self.callbacks:
                        callback(review)
                    
                    idx += 1
                    time.sleep(interval_seconds)
                else:
                    review = self.generate_random_review()
                    self.review_queue.put(review)
                    for callback in self.callbacks:
                        callback(review)
                    time.sleep(interval_seconds)
        
        self.stream_thread = threading.Thread(target=stream_generator, daemon=True)
        self.stream_thread.start()
    
    def stop_streaming(self):
        """Stop the real-time feed"""
        self.is_streaming = False
    
    def get_next_review(self, timeout=None):
        """Get next review from the stream"""
        try:
            return self.review_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def get_all_pending(self):
        """Get all pending reviews in queue"""
        reviews = []
        while not self.review_queue.empty():
            reviews.append(self.review_queue.get())
        return reviews
    
    def generate_random_review(self):
        """Generate a random review for testing"""
        templates = [
            "The {feature} is {sentiment}!",
            "I love the {feature}, but the {negative_feature} is terrible.",
            "{feature} could be better.",
            "Best {feature} ever! Highly recommend.",
            "Worst {feature} I've ever used. Waste of money."
        ]
        
        features = ['battery', 'price', 'quality', 'delivery', 'service']
        sentiments = ['amazing', 'great', 'poor', 'terrible', 'excellent']
        negative_features = ['battery life', 'customer service', 'packaging']
        
        template = random.choice(templates)
        review_text = template.format(
            feature=random.choice(features),
            sentiment=random.choice(sentiments),
            negative_feature=random.choice(negative_features)
        )
        
        return {
            'review_text': review_text,
            'product_name': random.choice(['Product A', 'Product B', 'Product C']),
            'timestamp': datetime.now().isoformat(),
            'stream_id': f"gen_{int(time.time())}"
        }
    
    def get_stream_stats(self):
        """Get statistics about the current stream"""
        return {
            'is_active': self.is_streaming,
            'queue_size': self.review_queue.qsize(),
            'total_samples': len(self.sample_reviews)
        }