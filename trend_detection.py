import pandas as pd
import numpy as np
from collections import Counter
from datetime import datetime, timedelta

def detect_emerging_trends(df, window_size=50):
    """Detect emerging issues and praise trends"""
    trends = {
        'emerging_issues': [],
        'praise_trends': [],
        'hourly_trends': [],
        'regional_trends': []
    }
    
    if len(df) < window_size * 2:
        window_size = max(len(df) // 3, 10)
    
    recent_df = df.tail(window_size)
    previous_df = df.head(len(df) - window_size).tail(window_size) if len(df) > window_size else df.head(window_size)
    
    all_features = set()
    for features in df['features']:
        all_features.update(features)
    
    for feature in all_features:
        recent_feature_reviews = recent_df[recent_df['features'].apply(lambda x: feature in x if x else False)]
        previous_feature_reviews = previous_df[previous_df['features'].apply(lambda x: feature in x if x else False)]
        
        if len(recent_feature_reviews) > 3:
            recent_negative_pct = (recent_feature_reviews['sentiment'] == 'negative').sum() / len(recent_feature_reviews) * 100
            previous_negative_pct = (previous_feature_reviews['sentiment'] == 'negative').sum() / len(previous_feature_reviews) * 100 if len(previous_feature_reviews) > 0 else recent_negative_pct
            
            if recent_negative_pct - previous_negative_pct > 15:
                trends['emerging_issues'].append({
                    'feature': feature,
                    'old_pct': previous_negative_pct,
                    'new_pct': recent_negative_pct,
                    'percentage_change': recent_negative_pct - previous_negative_pct,
                    'message': f"{feature.capitalize()} complaints increased from {previous_negative_pct:.0f}% to {recent_negative_pct:.0f}%"
                })
            
            if previous_negative_pct - recent_negative_pct > 15:
                trends['praise_trends'].append({
                    'feature': feature,
                    'old_pct': previous_negative_pct,
                    'new_pct': recent_negative_pct,
                    'message': f"{feature.capitalize()} satisfaction improved significantly"
                })
    
    # Hourly trend detection
    if 'datetime' in df.columns:
        df['datetime'] = pd.to_datetime(df['datetime'])
        df['hour'] = df['datetime'].dt.hour
        hourly_sentiment = df.groupby('hour')['sentiment'].apply(lambda x: (x == 'positive').sum() / len(x) * 100)
        
        for hour, pos_pct in hourly_sentiment.items():
            if pos_pct < 30:
                trends['hourly_trends'].append({
                    'hour': hour,
                    'positive_pct': pos_pct,
                    'message': f"Low positive sentiment ({pos_pct:.0f}%) during {hour}:00 - {hour+1}:00"
                })
    
    # Regional trend detection
    if 'region' in df.columns:
        regional_sentiment = df.groupby('region')['sentiment'].apply(lambda x: (x == 'negative').sum() / len(x) * 100)
        
        for region, neg_pct in regional_sentiment.items():
            if neg_pct > 40:
                trends['regional_trends'].append({
                    'region': region,
                    'negative_pct': neg_pct,
                    'message': f"High negative sentiment ({neg_pct:.0f}%) in {region} region"
                })
    
    return trends

def time_series_anomaly_detection(df):
    """Detect anomalies in sentiment time series"""
    anomalies = []
    
    if 'datetime' not in df.columns and 'date' not in df.columns:
        return anomalies
    
    if 'datetime' in df.columns:
        df['datetime'] = pd.to_datetime(df['datetime'])
        df['date_only'] = df['datetime'].dt.date
    else:
        df['date'] = pd.to_datetime(df['date'])
        df['date_only'] = df['date'].dt.date
    
    sentiment_map = {'positive': 1, 'neutral': 0, 'negative': -1}
    df['sentiment_score'] = df['sentiment'].map(sentiment_map)
    
    daily_data = df.groupby('date_only').agg({
        'sentiment_score': 'mean',
        'review_text': 'count'
    }).rename(columns={'review_text': 'volume'})
    
    if len(daily_data) < 5:
        return anomalies
    
    sentiment_values = daily_data['sentiment_score'].values
    mean_sentiment = np.mean(sentiment_values)
    std_sentiment = np.std(sentiment_values)
    
    for date, row in daily_data.iterrows():
        z_score = (row['sentiment_score'] - mean_sentiment) / std_sentiment if std_sentiment > 0 else 0
        
        if abs(z_score) > 2.0:
            anomalies.append({
                'date': str(date),
                'sentiment_score': row['sentiment_score'],
                'z_score': z_score,
                'severity': 'high' if abs(z_score) > 3 else 'medium',
                'message': f"Sentiment anomaly on {date}: score {row['sentiment_score']:.2f} (z-score: {z_score:.2f})"
            })
    
    return anomalies

def classify_systemic_vs_isolated(df, systemic_threshold=10):
    """Classify issues as systemic or isolated"""
    results = {
        'systemic': [],
        'isolated': []
    }
    
    feature_mentions = {}
    
    for idx, row in df.iterrows():
        if row['features']:
            for feature in row['features']:
                if feature not in feature_mentions:
                    feature_mentions[feature] = {'positive': 0, 'negative': 0, 'neutral': 0, 'total': 0}
                feature_mentions[feature][row['sentiment']] += 1
                feature_mentions[feature]['total'] += 1
    
    total_reviews = len(df)
    
    for feature, counts in feature_mentions.items():
        mention_pct = (counts['total'] / total_reviews) * 100
        negative_pct = (counts['negative'] / counts['total']) * 100 if counts['total'] > 0 else 0
        
        issue_data = {
            'feature': feature,
            'count': counts['total'],
            'percentage': mention_pct,
            'negative_pct': negative_pct,
            'confidence': min(negative_pct / 100 + 0.2, 0.95)
        }
        
        if mention_pct > systemic_threshold and negative_pct > 40:
            results['systemic'].append(issue_data)
        elif counts['total'] <= 2:
            results['isolated'].append(issue_data)
    
    results['systemic'] = sorted(results['systemic'], key=lambda x: x['negative_pct'], reverse=True)
    
    return results

def detect_temporal_patterns(df):
    """Detect patterns based on time of day, day of week"""
    patterns = {
        'peak_complaint_hours': [],
        'best_review_days': []
    }
    
    if 'datetime' in df.columns:
        df['datetime'] = pd.to_datetime(df['datetime'])
        df['hour'] = df['datetime'].dt.hour
        df['day_of_week'] = df['datetime'].dt.day_name()
        
        # Peak complaint hours
        hourly_neg = df.groupby('hour').apply(lambda x: (x['sentiment'] == 'negative').sum() / len(x) * 100)
        peak_hours = hourly_neg[hourly_neg > hourly_neg.mean() + hourly_neg.std()].sort_values(ascending=False).head(3)
        
        for hour, neg_pct in peak_hours.items():
            patterns['peak_complaint_hours'].append({
                'hour': hour,
                'negative_pct': neg_pct
            })
        
        # Best review days
        daily_pos = df.groupby('day_of_week').apply(lambda x: (x['sentiment'] == 'positive').sum() / len(x) * 100)
        best_days = daily_pos[daily_pos > daily_pos.mean()].sort_values(ascending=False).head(3)
        
        for day, pos_pct in best_days.items():
            patterns['best_review_days'].append({
                'day': day,
                'positive_pct': pos_pct
            })
    
    return patterns