import re
from textblob import TextBlob

# Hindi keywords
HINDI_POSITIVE_KEYWORDS = [
    'बहुत अच्छा', 'शानदार', 'बेहतरीन', 'कमाल', 'वाह', 'सुपर', 
    'बढ़िया', 'लाजवाब', 'जबरदस्त', 'मस्त', 'अच्छा लगा', 'बेस्ट'
]

HINDI_NEGATIVE_KEYWORDS = [
    'खराब', 'बेकार', 'घटिया', 'निराश', 'गंदा', 'बेईमानी',
    'ठगा', 'पैसे बर्बाद', 'फालतू', 'बेकार है', 'नहीं लेना चाहिए'
]

# Kannada keywords
KANNADA_POSITIVE_KEYWORDS = [
    'ಅದ್ಭುತ', 'ಶಾನಂದ', 'ಚೆನ್ನಾಗಿದೆ', 'ಉತ್ತಮ', 'ಬೆಸ್ಟ್',
    'ಖುಷಿ ಆಯ್ತು', 'ಸೂಪರ್', 'ನೈಸ್', 'ಗ್ರೇಟ್'
]

KANNADA_NEGATIVE_KEYWORDS = [
    'ಕೆಟ್ಟದು', 'ಬೇಕಾರ್', 'ವೇಸ್ಟ್', 'ನಿರಾಶೆ', 'ಮೋಸ',
    'ಹಣ ವ್ಯರ್ಥ', 'ಚೆನ್ನಾಗಿಲ್ಲ', 'ಸರಿಯಿಲ್ಲ'
]

def detect_language(text):
    """Detect language: English, Hindi, or Kannada"""
    devanagari_pattern = re.compile(r'[\u0900-\u097F]')
    kannada_pattern = re.compile(r'[\u0C80-\u0CFF]')
    
    if devanagari_pattern.search(text):
        return 'hindi'
    elif kannada_pattern.search(text):
        return 'kannada'
    return 'english'

def analyze_hindi_sentiment(text):
    """Hindi sentiment analysis"""
    text_lower = text.lower()
    
    positive_score = 0
    negative_score = 0
    
    for word in HINDI_POSITIVE_KEYWORDS:
        if word in text:
            positive_score += 1
    
    for word in HINDI_NEGATIVE_KEYWORDS:
        if word in text:
            negative_score += 1
    
    if positive_score > negative_score:
        return 'positive', 0.6 + (positive_score * 0.1)
    elif negative_score > positive_score:
        return 'negative', 0.6 + (negative_score * 0.1)
    else:
        return 'neutral', 0.5

def analyze_kannada_sentiment(text):
    """Kannada sentiment analysis"""
    text_lower = text.lower()
    
    positive_score = 0
    negative_score = 0
    
    for word in KANNADA_POSITIVE_KEYWORDS:
        if word in text:
            positive_score += 1
    
    for word in KANNADA_NEGATIVE_KEYWORDS:
        if word in text:
            negative_score += 1
    
    if positive_score > negative_score:
        return 'positive', 0.6 + (positive_score * 0.1)
    elif negative_score > positive_score:
        return 'negative', 0.6 + (negative_score * 0.1)
    else:
        return 'neutral', 0.5

def multilingual_sentiment(text):
    """Main function for multilingual sentiment analysis"""
    lang = detect_language(text)
    
    if lang == 'hindi':
        return analyze_hindi_sentiment(text)
    elif lang == 'kannada':
        return analyze_kannada_sentiment(text)
    else:
        # Use TextBlob for English
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        confidence = min(abs(polarity) + 0.3, 0.95)
        
        if polarity > 0.1:
            return 'positive', confidence
        elif polarity < -0.1:
            return 'negative', confidence
        else:
            return 'neutral', confidence