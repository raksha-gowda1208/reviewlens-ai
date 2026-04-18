import pandas as pd
import json
import re
from fuzzywuzzy import fuzz
from collections import Counter
import hashlib
from datetime import datetime

def ingest_data(file):
    """Ingest CSV or JSON file"""
    try:
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.name.endswith('.json'):
            data = json.load(file)
            df = pd.DataFrame(data)
        else:
            return None
        
        if 'review_text' not in df.columns:
            text_cols = df.select_dtypes(include=['object']).columns
            if len(text_cols) > 0:
                df = df.rename(columns={text_cols[0]: 'review_text'})
        
        if 'product_name' not in df.columns:
            df['product_name'] = 'General Product'
        
        if 'date' not in df.columns:
            df['date'] = datetime.now().strftime('%Y-%m-%d')
        
        return df
    except Exception as e:
        print(f"Error: {e}")
        return None

def deduplicate_reviews(df, threshold=85):
    """Remove near-duplicate reviews"""
    original_count = len(df)
    to_remove = set()
    
    texts = df['review_text'].tolist()
    
    for i in range(len(texts)):
        if i in to_remove:
            continue
        for j in range(i+1, len(texts)):
            if j in to_remove:
                continue
            try:
                similarity = fuzz.ratio(texts[i].lower(), texts[j].lower())
                if similarity > threshold:
                    to_remove.add(j)
            except:
                continue
    
    df_clean = df.drop(index=list(to_remove)).reset_index(drop=True)
    removed_count = original_count - len(df_clean)
    
    return df_clean, removed_count

def detect_noise_enhanced(df):
    """Enhanced noise detection with classification"""
    import re
    noise_scores = []
    noise_flags = []
    classifications = []
    quality_issues = []
    
    bot_patterns = [
        r'click.*link', r'visit.*website', r'buy.*now',
        r'http[s]?://', r'www\.', r'@', r'#ad', r'sponsored'
    ]
    
    for review in df['review_text']:
        score = 0
        review_lower = review.lower()
        
        for pattern in bot_patterns:
            if re.search(pattern, review_lower):
                score += 30
        
        if len(review.strip()) < 10:
            score += 20
        
        if review.isupper():
            score += 10
        
        if score >= 50:
            classification = 'Noisy'
        elif score >= 25:
            classification = 'Messy'
        else:
            classification = 'Clean'
        
        classifications.append(classification)
        quality_issues.append([])
        noise_scores.append(min(score, 100))
        noise_flags.append(score > 50)
    
    return {
        'scores': noise_scores,
        'flags': noise_flags,
        'classifications': classifications,
        'quality_issues': quality_issues
    }