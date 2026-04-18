import re
from textblob import TextBlob

# Feature keywords mapping
FEATURE_KEYWORDS = {
    'battery': ['battery', 'charge', 'power', 'drain', 'battery life', 'charging', 'backup'],
    'price': ['price', 'cost', 'money', 'value', 'expensive', 'cheap', 'worth', 'affordable'],
    'quality': ['quality', 'build', 'material', 'durable', 'sturdy', 'solid', 'premium'],
    'delivery': ['delivery', 'shipping', 'packaging', 'arrived', 'shipped', 'courier', 'package'],
    'service': ['service', 'support', 'customer service', 'help', 'assistance', 'response', 'refund'],
    'camera': ['camera', 'photo', 'picture', 'image', 'lens', 'shot', 'selfie'],
    'display': ['screen', 'display', 'touch', 'cracked', 'glass', 'panel', 'resolution'],
    'software': ['software', 'app', 'update', 'bug', 'crash', 'interface', 'ui', 'os']
}

# Sarcasm patterns
SARCASTIC_PATTERNS = [
    r'great.*just great', r'oh.*wonderful', r'just what i needed',
    r'best.*ever.*not', r'love.*but.*hate', r'fantastic.*disappointed',
    r'perfect.*broken', r'excellent.*waste'
]

def extract_features_with_confidence(text):
    """Extract features with confidence scores per feature"""
    text_lower = text.lower()
    features_found = []
    feature_confidences = {}
    
    for feature, keywords in FEATURE_KEYWORDS.items():
        confidence = 0
        for keyword in keywords:
            if keyword in text_lower:
                confidence += 0.3
        confidence = min(confidence, 0.95)
        
        if confidence > 0.2:
            features_found.append(feature)
            feature_confidences[feature] = confidence
    
    return list(set(features_found)), feature_confidences

def extract_features(df):
    """Extract features with per-feature confidence scores"""
    features_list = []
    feature_confidences_list = []
    sentiments = []
    confidence_scores = []
    sarcasm_flags = []
    
    for idx, row in df.iterrows():
        review = str(row['review_text'])
        
        # Extract features with confidence
        features, feat_conf = extract_features_with_confidence(review)
        features_list.append(features)
        feature_confidences_list.append(feat_conf)
        
        # Overall sentiment with TextBlob
        blob = TextBlob(review)
        polarity = blob.sentiment.polarity
        confidence = min(abs(polarity) + 0.3, 0.95)
        
        if polarity > 0.1:
            sentiment = 'positive'
        elif polarity < -0.1:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        sentiments.append(sentiment)
        confidence_scores.append(confidence)
        
        # Sarcasm detection
        sarcasm_score, is_sarcastic = detect_sarcasm_enhanced(review)
        sarcasm_flags.append(is_sarcastic)
    
    df['features'] = features_list
    df['feature_confidences'] = feature_confidences_list
    df['sentiment'] = sentiments
    df['confidence'] = confidence_scores
    df['is_sarcastic'] = sarcasm_flags
    
    return df

def analyze_feature_sentiment_with_confidence(text, features):
    """Analyze sentiment for each extracted feature with confidence"""
    feature_sentiments = {}
    
    for feature in features:
        keywords = FEATURE_KEYWORDS.get(feature, [feature])
        
        # Find sentences containing feature keywords
        sentences = re.split(r'[.!?]+', text)
        relevant_sentences = []
        
        for sentence in sentences:
            if any(kw in sentence.lower() for kw in keywords):
                relevant_sentences.append(sentence)
        
        if relevant_sentences:
            combined_text = ' '.join(relevant_sentences)
            blob = TextBlob(combined_text)
            polarity = blob.sentiment.polarity
            confidence = min(abs(polarity) + 0.3, 0.95)
            
            if polarity > 0.1:
                sentiment = 'positive'
            elif polarity < -0.1:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
        else:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            confidence = min(abs(polarity) + 0.2, 0.8)
            
            if polarity > 0.1:
                sentiment = 'positive'
            elif polarity < -0.1:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
        
        feature_sentiments[feature] = {
            'sentiment': sentiment,
            'confidence': confidence
        }
    
    return feature_sentiments

def detect_sarcasm_enhanced(text):
    """Enhanced sarcasm detection with confidence score"""
    text_lower = text.lower()
    sarcasm_score = 0
    
    # Check sarcasm patterns
    for pattern in SARCASTIC_PATTERNS:
        if re.search(pattern, text_lower):
            sarcasm_score += 0.4
    
    # Check for contradiction (positive word + negative context)
    blob = TextBlob(text)
    words = text.split()
    
    positive_words = ['great', 'amazing', 'awesome', 'perfect', 'excellent', 'love', 'best']
    negative_words = ['bad', 'poor', 'terrible', 'awful', 'worst', 'hate', 'broken']
    
    pos_count = sum(1 for w in words if w.lower() in positive_words)
    neg_count = sum(1 for w in words if w.lower() in negative_words)
    
    if pos_count > 0 and neg_count > 0 and blob.sentiment.polarity < 0:
        sarcasm_score += 0.5
    
    # Check for excessive punctuation
    if text.count('!') > 2 or text.count('?') > 2:
        if blob.sentiment.polarity < 0:
            sarcasm_score += 0.2
    
    return min(sarcasm_score, 0.95), sarcasm_score > 0.4