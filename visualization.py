import pandas as pd
import numpy as np
from datetime import datetime

def create_dashboard(df, results):
    """Generate dashboard charts"""
    charts = {}
    return charts

def generate_report(df, results):
    """Generate downloadable report"""
    report = {
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_reviews': len(df),
        'sentiment_summary': df['sentiment'].value_counts().to_dict(),
        'noise_detected': int(df['is_noise'].sum()) if 'is_noise' in df.columns else 0,
        'sarcastic_reviews': int(df['is_sarcastic'].sum()) if 'is_sarcastic' in df.columns else 0,
        'avg_confidence': df['confidence'].mean() if 'confidence' in df.columns else 0,
        'top_features': [],
        'category_insights': {},
        'per_feature_confidence': {}
    }
    
    # Top features
    all_features = []
    for features in df['features']:
        if features:
            all_features.extend(features)
    
    from collections import Counter
    feature_counts = Counter(all_features)
    report['top_features'] = feature_counts.most_common(5)
    
    # Per-feature confidence
    if 'feature_confidences' in df.columns:
        all_confidences = {}
        for conf_dict in df['feature_confidences']:
            for feature, conf in conf_dict.items():
                if feature not in all_confidences:
                    all_confidences[feature] = []
                all_confidences[feature].append(conf)
        
        for feature, confs in all_confidences.items():
            report['per_feature_confidence'][feature] = {
                'mean': np.mean(confs),
                'std': np.std(confs),
                'count': len(confs)
            }
    
    # Category insights
    if 'product_name' in df.columns:
        categories = df['product_name'].unique()
        for category in categories:
            cat_df = df[df['product_name'] == category]
            report['category_insights'][category] = {
                'review_count': len(cat_df),
                'positive_pct': (cat_df['sentiment'] == 'positive').sum() / len(cat_df) * 100,
                'negative_pct': (cat_df['sentiment'] == 'negative').sum() / len(cat_df) * 100
            }
    
    if results:
        report['emerging_issues'] = results.get('trends', {}).get('emerging_issues', [])
        report['anomalies'] = results.get('anomalies', [])
        report['systemic_issues'] = results.get('systemic', {}).get('systemic', [])
    
    return report