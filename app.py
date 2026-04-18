import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


# Import utility modules
from utils.data_ingestion import ingest_data, deduplicate_reviews, detect_noise_enhanced
from utils.feature_sentiment import extract_features, extract_features_with_confidence, analyze_feature_sentiment_with_confidence, detect_sarcasm_enhanced
from utils.trend_detection import detect_emerging_trends, classify_systemic_vs_isolated, time_series_anomaly_detection, detect_temporal_patterns
from utils.visualization import create_dashboard, generate_report
from utils.multilingual import multilingual_sentiment, detect_language
from utils.realtime_api import ReviewStreamSimulator
from utils.api_review_extractor import ReviewAPIExtractor

# Page configuration
st.set_page_config(
    page_title="ReviewLens AI - Hack Malenadu 2026",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS
def load_css():
    st.markdown("""
    <style>
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 20px;
            text-align: center;
            margin-bottom: 2rem;
            animation: fadeIn 1s ease-in;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes slideIn {
            from { opacity: 0; transform: translateX(-20px); }
            to { opacity: 1; transform: translateX(0); }
        }
        .main-header h1 {
            color: white;
            font-size: 3rem;
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        .main-header p {
            color: rgba(255,255,255,0.9);
            font-size: 1.1rem;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem;
            border-radius: 20px;
            text-align: center;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            animation: slideIn 0.5s ease-out;
            color: white;
        }
        .stat-card:hover {
            transform: translateY(-5px) scale(1.02);
            box-shadow: 0 20px 40px rgba(0,0,0,0.2);
        }
        .stat-card h3 {
            font-size: 1rem;
            margin-bottom: 0.5rem;
            opacity: 0.9;
        }
        .stat-card h2 {
            font-size: 2.5rem;
            margin: 0;
            font-weight: bold;
        }
        
        .alert-critical {
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 15px;
            margin: 0.5rem 0;
            animation: pulse 2s infinite;
            border-left: 5px solid #fff;
        }
        .alert-critical:hover {
            transform: scale(1.01);
            transition: 0.3s;
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.02); }
            100% { transform: scale(1); }
        }
        
        .alert-warning {
            background: linear-gradient(135deg, #feca57 0%, #ff9f43 100%);
            padding: 1rem 1.5rem;
            border-radius: 15px;
            margin: 0.5rem 0;
            border-left: 5px solid #fff;
        }
        
        .confidence-meter {
            width: 100%;
            background: #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
            margin: 5px 0;
        }
        .confidence-fill {
            height: 8px;
            border-radius: 10px;
            transition: width 0.5s ease;
        }
        .confidence-high { background: #00b894; }
        .confidence-medium { background: #fdcb6e; }
        .confidence-low { background: #ff7675; }
        
        .lang-badge {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 0.2rem 0.6rem;
            border-radius: 20px;
            font-size: 0.7rem;
            margin-left: 0.5rem;
        }
        
        .quality-clean {
            background: #00b894;
            color: white;
            padding: 0.2rem 0.6rem;
            border-radius: 20px;
            font-size: 0.7rem;
        }
        .quality-messy {
            background: #fdcb6e;
            color: white;
            padding: 0.2rem 0.6rem;
            border-radius: 20px;
            font-size: 0.7rem;
        }
        .quality-noisy {
            background: #ff7675;
            color: white;
            padding: 0.2rem 0.6rem;
            border-radius: 20px;
            font-size: 0.7rem;
        }
        
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 0.6rem 2rem;
            border-radius: 30px;
            font-weight: bold;
            transition: all 0.3s;
            width: 100%;
        }
        .stButton > button:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 20px rgba(102,126,234,0.4);
        }
        
        .footer {
            text-align: center;
            padding: 2rem;
            color: #666;
            border-top: 1px solid #ddd;
            margin-top: 2rem;
        }
        
        .stream-card {
            background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
            padding: 0.8rem;
            border-radius: 10px;
            margin: 0.5rem 0;
            border-left: 4px solid #667eea;
        }
        
        .stTabs [data-baseweb="tab-list"] {
            gap: 1rem;
            background-color: #f8f9fa;
            border-radius: 15px;
            padding: 0.5rem;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 10px;
            padding: 0.5rem 1rem;
            font-weight: 500;
        }
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .api-card {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 1rem;
            border-radius: 15px;
            margin: 0.5rem 0;
            border: 1px solid #dee2e6;
        }
    </style>
    """, unsafe_allow_html=True)

load_css()

# Header
st.markdown("""
<div class="main-header">
    <h1>🔍 ReviewLens AI</h1>
    <p>Intelligent Customer Review Intelligence Platform | Hack Malenadu '26</p>
    <p style="font-size: 0.9rem;">✨ Hindi + Kannada Support | Real-time API | Regional Trends | Data Classification ✨</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/google-reviews.png", width=80)
    st.markdown("## 🎯 Problem Statement")
    st.markdown("""
    **AI-powered Customer Review Intelligence Platform**
    - ✅ Ingests noisy, multilingual reviews
    - ✅ Extracts feature-level sentiment
    - ✅ Detects emerging trends
    - ✅ Surfaces actionable recommendations
    """)
    st.markdown("---")
    st.markdown("## 🏆 Stretch Goals")
    st.markdown("""
    - ⚡ Real-time API feed
    - 🎯 Per-feature confidence
    - 📈 Time-series anomaly
    - 📊 Downloadable report
    - 🌏 Hindi + Kannada support
    - 📦 Cross-category comparison
    - 🗺️ Regional trend analysis
    - 📋 Data classification
    """)
    st.markdown("---")
    st.markdown("## 📈 Key Metrics")
    
    if st.session_state.get('df') is not None and st.session_state.get('analyzed'):
        df = st.session_state.df
        if 'sentiment' in df.columns:
            pos = (df['sentiment'] == 'positive').sum()
            neg = (df['sentiment'] == 'negative').sum()
            neu = (df['sentiment'] == 'neutral').sum()
            st.metric("😊 Positive", f"{pos} ({pos/len(df)*100:.0f}%)")
            st.metric("😞 Negative", f"{neg} ({neg/len(df)*100:.0f}%)")
            st.metric("😐 Neutral", f"{neu} ({neu/len(df)*100:.0f}%)")

# Session state initialization
if 'analyzed' not in st.session_state:
    st.session_state.analyzed = False
if 'results' not in st.session_state:
    st.session_state.results = None
if 'df' not in st.session_state:
    st.session_state.df = None
if 'stream_simulator' not in st.session_state:
    st.session_state.stream_simulator = None
if 'stream_active' not in st.session_state:
    st.session_state.stream_active = False
if 'stream_reviews' not in st.session_state:
    st.session_state.stream_reviews = []

# Create tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📤 Data Ingestion", "🎯 Sentiment Analysis", "📈 Trend Detection", "📊 Dashboard", "⚡ Real-Time API", "🌐 API Extractor"])

# ==================== TAB 1: DATA INGESTION ====================
with tab1:
    st.markdown("## 📤 Data Ingestion & Preprocessing")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📁 Upload File")
        uploaded_file = st.file_uploader(
            "Upload CSV or JSON",
            type=['csv', 'json']
        )
        
        if uploaded_file:
            df = ingest_data(uploaded_file)
            if df is not None:
                st.session_state.df = df
                st.success(f"✅ Loaded {len(df)} reviews")
                st.dataframe(df[['review_text']].head(3), use_container_width=True)
    
    with col2:
        st.markdown("### ✍️ Manual Paste")
        manual_reviews = st.text_area(
            "Paste reviews (one per line)",
            height=200,
            placeholder="Great product! Battery lasts forever...\nPoor delivery service...\nबहुत अच्छा product है...\nಅದ್ಭುತ ಉತ್ಪನ್ನ!"
        )
        
        if manual_reviews:
            lines = [l.strip() for l in manual_reviews.split('\n') if l.strip()]
            df_manual = pd.DataFrame({'review_text': lines})
            st.session_state.df = df_manual
            st.success(f"✅ Loaded {len(lines)} reviews")
    
    if st.session_state.df is not None:
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Deduplicate Reviews", use_container_width=True):
                with st.spinner("Deduplicating..."):
                    df_clean, removed = deduplicate_reviews(st.session_state.df)
                    st.session_state.df = df_clean
                    st.success(f"Removed {removed} duplicate reviews")
        
        with col2:
            if st.button("🚨 Detect Noise & Quality", use_container_width=True):
                with st.spinner("Analyzing noise and data quality..."):
                    noise_results = detect_noise_enhanced(st.session_state.df)
                    st.session_state.df['noise_score'] = noise_results['scores']
                    st.session_state.df['is_noise'] = noise_results['flags']
                    st.session_state.df['data_quality'] = noise_results['classifications']
                    st.session_state.df['quality_issues'] = noise_results['quality_issues']
                    noise_count = sum(noise_results['flags']) if isinstance(noise_results['flags'], list) else noise_results['flags'].sum()
                    st.warning(f"Found {noise_count} spam/bot reviews")
                    st.info(f"📊 Data Quality: Clean={noise_results['classifications'].count('Clean')}, Messy={noise_results['classifications'].count('Messy')}, Noisy={noise_results['classifications'].count('Noisy')}")
        
        with col3:
            if st.button("🚀 Analyze All Reviews", type="primary", use_container_width=True):
                with st.spinner("Processing all reviews..."):
                    features_df = extract_features(st.session_state.df)
                    st.session_state.df = features_df
                    trends = detect_emerging_trends(st.session_state.df)
                    anomalies = time_series_anomaly_detection(st.session_state.df)
                    systemic = classify_systemic_vs_isolated(st.session_state.df)
                    temporal = detect_temporal_patterns(st.session_state.df)
                    
                    st.session_state.results = {
                        'trends': trends,
                        'anomalies': anomalies,
                        'systemic': systemic,
                        'temporal': temporal,
                        'analysis_complete': True
                    }
                    st.session_state.analyzed = True
                    st.success("✅ Analysis complete!")
                    st.balloons()

# ==================== TAB 2: SENTIMENT ANALYSIS ====================
with tab2:
    st.markdown("## 🎯 Feature-Level Sentiment Analysis")
    
    if st.session_state.df is not None and st.session_state.analyzed:
        if 'sentiment' not in st.session_state.df.columns:
            st.warning("⚠️ Please click 'Analyze All Reviews' first.")
        else:
            df = st.session_state.df
            
            # Language distribution
            st.markdown("### 🌐 Language Distribution")
            languages = [detect_language(text) for text in df['review_text']]
            lang_counts = pd.Series(languages).value_counts()
            fig_lang = px.pie(values=lang_counts.values, names=lang_counts.index, title="Reviews by Language", hole=0.3)
            st.plotly_chart(fig_lang, use_container_width=True)
            
            # Feature distribution chart
            all_features = []
            for features in df['features']:
                if features:
                    all_features.extend(features)
            
            from collections import Counter
            feature_counts = Counter(all_features)
            
            if feature_counts:
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    fig = px.bar(
                        x=list(feature_counts.keys()),
                        y=list(feature_counts.values()),
                        title="📊 Feature Mentions Distribution",
                        color=list(feature_counts.values()),
                        color_continuous_scale='Viridis',
                        text=list(feature_counts.values())
                    )
                    fig.update_traces(textposition='outside')
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.markdown("### 🎯 Per-Feature Confidence")
                    if 'feature_confidences' in df.columns:
                        avg_confidences = {}
                        for conf_dict in df['feature_confidences']:
                            for feature, conf in conf_dict.items():
                                if feature not in avg_confidences:
                                    avg_confidences[feature] = []
                                avg_confidences[feature].append(conf)
                        
                        for feature, confs in avg_confidences.items():
                            avg_conf = sum(confs) / len(confs)
                            color = "#00b894" if avg_conf > 0.7 else "#fdcb6e" if avg_conf > 0.4 else "#ff7675"
                            st.markdown(f"""
                            <div style="margin: 0.8rem 0;">
                                <strong>{feature.capitalize()}</strong>
                                <div class="confidence-meter">
                                    <div class="confidence-fill" style="width: {avg_conf*100}%; background: {color};"></div>
                                </div>
                                <small>{avg_conf:.0%} confidence</small>
                            </div>
                            """, unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("### 📝 Sample Reviews Analysis")
            
            display_cols = ['review_text', 'sentiment', 'confidence', 'features']
            if 'data_quality' in df.columns:
                display_cols.append('data_quality')
            
            sample = df[display_cols].head(10)
            for idx, row in sample.iterrows():
                lang = detect_language(row['review_text'])
                lang_badge = f'<span class="lang-badge">{lang.upper()}</span>' if lang != 'english' else ''
                
                quality_badge = ''
                if 'data_quality' in row and row['data_quality']:
                    quality_class = f'quality-{row["data_quality"].lower()}'
                    quality_badge = f'<span class="{quality_class}">{row["data_quality"]}</span>'
                
                emoji = "😊" if row['sentiment'] == 'positive' else "😞" if row['sentiment'] == 'negative' else "😐"
                st.markdown(f"""
                <div style="background: #f8f9fa; padding: 0.8rem; border-radius: 10px; margin: 0.5rem 0; border-left: 4px solid {'#00b894' if row['sentiment'] == 'positive' else '#ff7675' if row['sentiment'] == 'negative' else '#fdcb6e'}">
                    <small>{emoji} {row['sentiment'].upper()} | Confidence: {row['confidence']:.0%} {lang_badge} {quality_badge}</small><br>
                    <strong>"{row['review_text'][:150]}..."</strong><br>
                    <small>Features: {', '.join(row['features']) if row['features'] else 'None detected'}</small>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("👈 Go to Data Ingestion tab and click 'Analyze All Reviews'")

# ==================== TAB 3: TREND DETECTION ====================
with tab3:
    st.markdown("## 📈 Trend Detection & Anomalies")
    
    if st.session_state.df is not None and st.session_state.analyzed:
        if 'sentiment' not in st.session_state.df.columns:
            st.warning("⚠️ Please click 'Analyze All Reviews' first.")
        elif st.session_state.results:
            
            # Display emerging trends
            trends = st.session_state.results.get('trends', {})
            if trends.get('emerging_issues'):
                st.markdown("### 🚨 Emerging Critical Issues")
                for trend in trends['emerging_issues']:
                    st.markdown(f"""
                    <div class="alert-critical">
                        <strong>⚠️ {trend['feature'].upper()}</strong><br>
                        Negative feedback increased from {trend['old_pct']:.0f}% to {trend['new_pct']:.0f}%<br>
                        <small>{trend['message']}</small>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Regional trends
            if trends.get('regional_trends'):
                st.markdown("### 🗺️ Regional Trend Analysis")
                for trend in trends['regional_trends']:
                    st.markdown(f"""
                    <div class="alert-warning">
                        <strong>📍 {trend['region']} Region</strong><br>
                        {trend['message']}
                    </div>
                    """, unsafe_allow_html=True)
            
            # Hourly Pattern Analysis - FIXED VERSION
            st.markdown("### ⏰ Hourly Pattern Analysis")
            st.markdown("*Understanding when customers are most active and vocal*")
            
            # Check if we have datetime data to analyze hourly patterns
            df = st.session_state.df
            has_datetime = 'datetime' in df.columns or 'date' in df.columns
            
            if has_datetime:
                # Create hourly data from the dataframe
                temp_df = df.copy()
                if 'datetime' in temp_df.columns:
                    temp_df['datetime'] = pd.to_datetime(temp_df['datetime'])
                    temp_df['hour'] = temp_df['datetime'].dt.hour
                elif 'date' in temp_df.columns:
                    temp_df['date'] = pd.to_datetime(temp_df['date'])
                    temp_df['hour'] = temp_df['date'].dt.hour
                else:
                    temp_df['hour'] = 12
                
                # Calculate negative percentage by hour
                hourly_negative = temp_df.groupby('hour').apply(
                    lambda x: (x['sentiment'] == 'negative').sum() / len(x) * 100 if len(x) > 0 else 0
                )
                
                if len(hourly_negative) > 0:
                    col1, col2 = st.columns(2)
                    
                    # Create hourly data for visualization
                    hourly_data = []
                    for hour, neg_pct in hourly_negative.items():
                        if neg_pct > 0:
                            hourly_data.append({
                                'Hour': f"{int(hour)}:00 - {int(hour)+1}:00",
                                'Negative %': round(neg_pct, 1),
                                'Positive %': round(100 - neg_pct, 1)
                            })
                    
                    if hourly_data:
                        hourly_df = pd.DataFrame(hourly_data)
                        hourly_df = hourly_df.sort_values('Hour')
                        
                        with col1:
                            fig_hourly = px.bar(
                                hourly_df,
                                x='Hour',
                                y='Negative %',
                                title="Negative Sentiment by Hour of Day",
                                color='Negative %',
                                color_continuous_scale='Reds',
                                text='Negative %'
                            )
                            fig_hourly.update_traces(textposition='outside')
                            fig_hourly.update_layout(xaxis_tickangle=-45, height=400)
                            st.plotly_chart(fig_hourly, use_container_width=True)
                        
                        with col2:
                            st.markdown("#### 📊 Key Insights")
                            
                            worst_hour = max(hourly_data, key=lambda x: x['Negative %'])
                            best_hour = min(hourly_data, key=lambda x: x['Negative %'])
                            
                            st.info(f"🔴 **Peak Complaint Hour:** {worst_hour['Hour']} with {worst_hour['Negative %']:.0f}% negative reviews")
                            st.success(f"🟢 **Best Hour:** {best_hour['Hour']} with {best_hour['Negative %']:.0f}% negative reviews")
                            
                            st.markdown("#### 💡 Recommendations")
                            st.markdown("""
                            - 📞 **Increase support staff** during peak complaint hours
                            - ⏰ **Schedule quality checks** before high-traffic periods
                            - 📧 **Send satisfaction surveys** during best hours
                            - 🚀 **Launch marketing campaigns** during low-negative hours
                            """)
                    else:
                        st.info("Not enough hourly data to display patterns. Add more reviews with timestamps.")
                else:
                    st.info("Add 'datetime' or 'date' column with timestamps to see hourly patterns")
            else:
                st.info("📅 **Tip:** Add a 'datetime' or 'date' column to your CSV to see hourly patterns and when customers are most active!")
            
            # Display anomalies
            anomalies = st.session_state.results.get('anomalies', [])
            if anomalies:
                st.markdown("### 📊 Time-Series Anomalies Detected")
                anomaly_df = pd.DataFrame(anomalies)
                st.dataframe(anomaly_df[['date', 'message', 'severity']], use_container_width=True)
            
            # Temporal patterns
            temporal = st.session_state.results.get('temporal', {})
            if temporal:
                st.markdown("### 📅 Day of Week Patterns")
                col1, col2 = st.columns(2)
                with col1:
                    if temporal.get('peak_complaint_hours'):
                        st.markdown("**📉 Worst Hours for Complaints**")
                        for hour in temporal['peak_complaint_hours']:
                            st.write(f"- ⏰ {hour.get('hour', 'N/A')}:00 - {hour.get('negative_pct', 0):.0f}% negative")
                with col2:
                    if temporal.get('best_review_days'):
                        st.markdown("**📈 Best Days for Positive Reviews**")
                        for day in temporal['best_review_days']:
                            st.write(f"- 📅 {day.get('day', 'N/A')}: {day.get('positive_pct', 0):.0f}% positive")
            
            # Systemic vs Isolated
            st.markdown("---")
            st.markdown("### 🎯 Systemic vs Isolated Issues")
            
            systemic = st.session_state.results.get('systemic', {'systemic': [], 'isolated': []})
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### 🔴 Systemic Issues (Need Immediate Action)")
                if systemic['systemic']:
                    for issue in systemic['systemic']:
                        st.progress(min(issue['percentage']/100, 1.0), text=f"{issue['feature'].upper()}: {issue['percentage']:.0f}% of reviews")
                else:
                    st.success("✅ No systemic issues detected")
            
            with col2:
                st.markdown("#### 🟡 Isolated Issues (Monitor)")
                if systemic['isolated']:
                    for issue in systemic['isolated']:
                        st.info(f"📌 {issue['feature'].upper()}: {issue['count']} mention(s)")
                else:
                    st.info("No isolated issues flagged")
    else:
        st.info("👈 Go to Data Ingestion tab and click 'Analyze All Reviews'")

# ==================== TAB 4: DASHBOARD ====================
with tab4:
    st.markdown("## 📊 Interactive Dashboard")
    
    if st.session_state.df is not None and st.session_state.analyzed:
        df = st.session_state.df
        
        if 'sentiment' not in df.columns:
            st.warning("⚠️ Please click 'Analyze All Reviews' first.")
        else:
            # KPI Cards
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            
            with col1:
                st.markdown(f"""
                <div class="stat-card">
                    <h3>📊 Total Reviews</h3>
                    <h2>{len(df)}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                pos_pct = (df['sentiment'] == 'positive').sum() / len(df) * 100
                st.markdown(f"""
                <div class="stat-card">
                    <h3>😊 Positive</h3>
                    <h2>{pos_pct:.0f}%</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                neg_pct = (df['sentiment'] == 'negative').sum() / len(df) * 100
                st.markdown(f"""
                <div class="stat-card">
                    <h3>😞 Negative</h3>
                    <h2>{neg_pct:.0f}%</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                avg_conf = df['confidence'].mean() * 100 if 'confidence' in df.columns else 0
                st.markdown(f"""
                <div class="stat-card">
                    <h3>🎯 Avg Confidence</h3>
                    <h2>{avg_conf:.0f}%</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col5:
                unique_cats = df['product_name'].nunique() if 'product_name' in df.columns else 1
                st.markdown(f"""
                <div class="stat-card">
                    <h3>🏷️ Categories</h3>
                    <h2>{unique_cats}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col6:
                if 'data_quality' in df.columns:
                    clean_count = df['data_quality'].value_counts().get('Clean', 0)
                else:
                    clean_count = 0
                st.markdown(f"""
                <div class="stat-card">
                    <h3>✨ Clean Data</h3>
                    <h2>{clean_count}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            # Row 2: Charts
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("### 📊 Sentiment Distribution")
                sentiment_counts = df['sentiment'].value_counts()
                fig_pie = px.pie(
                    values=sentiment_counts.values,
                    names=sentiment_counts.index,
                    title="Overall Sentiment",
                    color_discrete_map={'positive': '#00b894', 'negative': '#ff7675', 'neutral': '#fdcb6e'},
                    hole=0.4
                )
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                st.markdown("### 📈 Sentiment Trend")
                if 'datetime' in df.columns:
                    df['datetime'] = pd.to_datetime(df['datetime'])
                    daily_sentiment = df.groupby([df['datetime'].dt.date, 'sentiment']).size().unstack(fill_value=0)
                    fig_line = px.line(daily_sentiment, title="Sentiment Over Time", markers=True)
                    fig_line.update_layout(xaxis_title="Date", yaxis_title="Number of Reviews")
                    st.plotly_chart(fig_line, use_container_width=True)
                elif 'date' in df.columns:
                    df['date'] = pd.to_datetime(df['date'])
                    daily_sentiment = df.groupby([df['date'].dt.date, 'sentiment']).size().unstack(fill_value=0)
                    fig_line = px.line(daily_sentiment, title="Sentiment Over Time", markers=True)
                    st.plotly_chart(fig_line, use_container_width=True)
                else:
                    st.info("Add 'date' or 'datetime' column to see time trends")
            
            # Row 3: Cross-Category Comparison
            if 'product_name' in df.columns and df['product_name'].nunique() >= 2:
                st.markdown("---")
                st.markdown("### 🏷️ Cross-Category Comparison")
                
                category_data = df.groupby('product_name').agg({
                    'sentiment': lambda x: (x == 'positive').sum() / len(x) * 100,
                    'review_text': 'count'
                }).rename(columns={'sentiment': 'positive_percentage', 'review_text': 'review_count'}).reset_index()
                
                fig_cat = px.bar(
                    category_data,
                    x='product_name',
                    y='positive_percentage',
                    title="Positive Sentiment by Category",
                    color='positive_percentage',
                    color_continuous_scale='Viridis',
                    text=category_data['positive_percentage'].round(1).astype(str) + '%'
                )
                fig_cat.update_traces(textposition='outside')
                st.plotly_chart(fig_cat, use_container_width=True)
            
            # Row 4: Regional Analysis (Remove Unknown)
            if 'region' in df.columns:
                st.markdown("---")
                st.markdown("### 🗺️ Regional Sentiment Analysis")
                
                # Filter out Unknown region
                df_filtered = df[df['region'] != 'Unknown']
                
                if len(df_filtered) > 0:
                    regional_data = df_filtered.groupby('region').agg({
                        'sentiment': lambda x: (x == 'positive').sum() / len(x) * 100,
                        'review_text': 'count'
                    }).rename(columns={'sentiment': 'positive_percentage', 'review_text': 'review_count'}).reset_index()
                    
                    fig_regional = px.bar(
                        regional_data,
                        x='region',
                        y='positive_percentage',
                        title="Positive Sentiment by Region",
                        color='positive_percentage',
                        color_continuous_scale='Viridis',
                        text=regional_data['positive_percentage'].round(1).astype(str) + '%'
                    )
                    fig_regional.update_traces(textposition='outside')
                    st.plotly_chart(fig_regional, use_container_width=True)
                    
                    # Add regional insights
                    best_region = regional_data.loc[regional_data['positive_percentage'].idxmax()]
                    worst_region = regional_data.loc[regional_data['positive_percentage'].idxmin()]
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.success(f"🌟 **Best Region:** {best_region['region']} with {best_region['positive_percentage']:.0f}% positive reviews")
                    with col2:
                        st.error(f"⚠️ **Needs Improvement:** {worst_region['region']} with {worst_region['positive_percentage']:.0f}% positive reviews")
                else:
                    st.info("No regional data available (add 'region' column with North/South/East/West values)")
            
            # Row 5: Feature Analysis
            st.markdown("---")
            st.markdown("### 🔍 Feature-Level Insights")
            
            all_features = []
            for features in df['features']:
                if features:
                    all_features.extend(features)
            
            if all_features:
                feature_df = pd.DataFrame({'feature': all_features})
                feature_counts = feature_df['feature'].value_counts().reset_index()
                feature_counts.columns = ['feature', 'count']
                
                fig_feat = px.bar(
                    feature_counts,
                    x='feature',
                    y='count',
                    title="Most Mentioned Features",
                    color='count',
                    color_continuous_scale='Viridis'
                )
                st.plotly_chart(fig_feat, use_container_width=True)
            
            # Table Explanation Section
            st.markdown("---")
            st.markdown("## 📋 Data Classification & Quality Report")
            
            explanation_data = []
            for idx, row in df.head(20).iterrows():
                lang = detect_language(row['review_text']).upper()
                quality = row.get('data_quality', 'Not Analyzed') if 'data_quality' in df.columns else 'Not Analyzed'
                quality_issues = row.get('quality_issues', []) if 'quality_issues' in df.columns else []
                issues_str = ', '.join(quality_issues[:2]) if quality_issues else 'None'
                
                explanation_data.append({
                    'Review': row['review_text'][:60] + "..." if len(row['review_text']) > 60 else row['review_text'],
                    'Language': lang,
                    'Data Quality': quality,
                    'Quality Issues': issues_str,
                    'Sentiment': row['sentiment'].upper(),
                    'Confidence': f"{row['confidence']:.0%}",
                    'Features': ', '.join(row['features'][:3]) if row['features'] else 'None',
                    'Source': row.get('source', 'Unknown'),
                    'Region': row.get('region', 'Unknown'),
                    'Date/Time': str(row.get('datetime', row.get('date', 'Unknown')))[:16] if row.get('datetime') or row.get('date') else 'Unknown'
                })
            
            explanation_df = pd.DataFrame(explanation_data)
            st.dataframe(explanation_df, use_container_width=True)
            
            with st.expander("📖 Understanding the Table Columns - Click to Expand"):
                st.markdown("""
                | Column | Description |
                |--------|-------------|
                | **Review** | The original customer review (truncated) |
                | **Language** | Detected language: ENGLISH, HINDI, KANNADA |
                | **Data Quality** | CLEAN = Well-written; MESSY = Typos/mixed language; NOISY = Spam/bot |
                | **Quality Issues** | Specific issues detected (e.g., "Mixed English-Hindi") |
                | **Sentiment** | POSITIVE 😊, NEGATIVE 😞, or NEUTRAL 😐 |
                | **Confidence** | How confident the AI is (higher = more reliable) |
                | **Features** | Product aspects mentioned (battery, price, quality, etc.) |
                | **Source** | Platform where review came from |
                | **Region** | Geographic region (North, South, East, West) |
                | **Date/Time** | When the review was posted |
                """)
            
            # Download Section
            st.markdown("---")
            st.markdown("### 📥 Export Data")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📊 Download Full CSV",
                    data=csv,
                    file_name=f"reviewlens_full_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            
            with col2:
                summary_data = {
                    'Metric': ['Total Reviews', 'Positive %', 'Negative %', 'Neutral %', 'Avg Confidence', 'Clean Data %', 'Languages Found', 'Categories'],
                    'Value': [
                        len(df), f"{pos_pct:.1f}%", f"{neg_pct:.1f}%", f"{100-pos_pct-neg_pct:.1f}%",
                        f"{avg_conf:.1f}%",
                        f"{(df['data_quality'] == 'Clean').sum() / len(df) * 100:.1f}%" if 'data_quality' in df.columns else 'N/A',
                        ', '.join(df['review_text'].apply(detect_language).unique()),
                        df['product_name'].nunique() if 'product_name' in df.columns else 1
                    ]
                }
                summary_df = pd.DataFrame(summary_data)
                csv_summary = summary_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📋 Download Summary Report",
                    data=csv_summary,
                    file_name=f"reviewlens_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            
            with col3:
                st.info(f"📈 Overall Health Score: {pos_pct:.0f}% Positive")
    else:
        st.info("👈 Please go to the **Data Ingestion** tab, upload your reviews, and click **'Analyze All Reviews'** first.")

# ==================== TAB 5: REAL-TIME API ====================
with tab5:
    st.markdown("## ⚡ Simulated Real-Time API Feed")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if not st.session_state.stream_active:
            if st.button("▶️ Start Streaming", use_container_width=True):
                st.session_state.stream_simulator = ReviewStreamSimulator()
                if st.session_state.df is not None:
                    st.session_state.stream_simulator.add_sample_reviews(st.session_state.df)
                st.session_state.stream_simulator.start_streaming(interval_seconds=3)
                st.session_state.stream_active = True
                st.rerun()
        else:
            if st.button("⏹️ Stop Streaming", use_container_width=True):
                if st.session_state.stream_simulator:
                    st.session_state.stream_simulator.stop_streaming()
                st.session_state.stream_active = False
                st.rerun()
        
        if st.session_state.stream_simulator:
            stats = st.session_state.stream_simulator.get_stream_stats()
            st.metric("Queue Size", stats['queue_size'])
            st.metric("Status", "🟢 Active" if stats['is_active'] else "🔴 Stopped")
    
    with col2:
        if st.session_state.stream_simulator and st.session_state.stream_active:
            new_reviews = st.session_state.stream_simulator.get_all_pending()
            for review in new_reviews[-5:]:
                sentiment, conf = multilingual_sentiment(review['review_text'])
                lang = detect_language(review['review_text'])
                lang_badge = f'<span class="lang-badge">{lang.upper()}</span>' if lang != 'english' else ''
                emoji = "😊" if sentiment == 'positive' else "😞" if sentiment == 'negative' else "😐"
                st.markdown(f"""
                <div class="stream-card">
                    <small>{emoji} {sentiment.upper()} ({conf:.0%} confidence) {lang_badge}</small><br>
                    <strong>"{review['review_text'][:80]}..."</strong>
                </div>
                """, unsafe_allow_html=True)
            st.session_state.stream_reviews.extend(new_reviews)

# ==================== TAB 6: API EXTRACTOR ====================
with tab6:
    st.markdown("## 🌐 API Review Extractor")
    st.markdown("*Fetch real-time reviews from multiple sources using external APIs*")
    
    api_extractor = ReviewAPIExtractor()
    
    st.markdown("""
    <div class="api-card">
        <h4>📡 Available Data Sources</h4>
        <p>Connect to real review data from popular platforms:</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 🔑 Select Sources")
        
        source_amazon = st.checkbox("🛒 **Amazon** - Product reviews", value=True)
        source_flipkart = st.checkbox("📦 **Flipkart** - E-commerce reviews", value=True)
        source_twitter = st.checkbox("🐦 **Twitter/X** - Social media mentions", value=False)
        source_google = st.checkbox("🔍 **Google** - Play Store / Maps reviews", value=False)
        
        sources = []
        if source_amazon:
            sources.append('Amazon')
        if source_flipkart:
            sources.append('Flipkart')
        if source_twitter:
            sources.append('Twitter')
        if source_google:
            sources.append('Google')
        
        product_name = st.text_input("🏷️ **Product Name**", placeholder="e.g., iPhone 15, Samsung Galaxy S24, Boat Headphones")
        
        col_a, col_b = st.columns(2)
        with col_a:
            review_count = st.slider("📊 Number of Reviews", min_value=5, max_value=100, value=30)
        with col_b:
            st.markdown("<br>", unsafe_allow_html=True)
            fetch_button = st.button("🚀 Fetch Reviews Now", type="primary", use_container_width=True)
    
    with col2:
        st.markdown("### 📋 API Configuration")
        st.markdown("""
        **API Endpoints Available:**
        
        | Platform | API Type | Status |
        |----------|----------|--------|
        | Amazon | Product Reviews | 🟢 Ready |
        | Flipkart | Product Reviews | 🟢 Ready |
        | Twitter | Recent Tweets | 🟡 Demo Mode |
        | Google | Store Reviews | 🟢 Ready |
        
        *For hackathon demo, APIs are simulated. In production, add your API keys.*
        """)
        
        st.markdown("### 💡 Pro Tips")
        st.markdown("""
        - 🔥 **Combine sources** for comprehensive analysis
        - 📈 **Fetch 30-50 reviews** for meaningful trends
        - 🔄 **Re-fetch weekly** to track sentiment changes
        - 📊 **Export data** to share with your team
        """)
    
    if fetch_button:
        if not product_name:
            st.error("❌ Please enter a product name")
        elif not sources:
            st.error("❌ Please select at least one source")
        else:
            with st.spinner(f"🌐 Fetching {review_count} reviews from {', '.join(sources)}..."):
                source_map = {
                    'Amazon': 'amazon',
                    'Flipkart': 'flipkart',
                    'Twitter': 'twitter',
                    'Google': 'google'
                }
                selected = [source_map[s] for s in sources if s in source_map]
                
                try:
                    extracted_df = api_extractor.extract_multiple_sources(product_name, selected)
                    
                    if extracted_df is not None and len(extracted_df) > 0:
                        extracted_df = extracted_df.head(review_count)
                        
                        if 'source' not in extracted_df.columns:
                            extracted_df['source'] = 'API'
                        
                        if st.session_state.df is not None:
                            st.session_state.df = pd.concat([st.session_state.df, extracted_df], ignore_index=True)
                        else:
                            st.session_state.df = extracted_df
                        
                        st.session_state.analyzed = False
                        
                        st.success(f"✅ Successfully fetched {len(extracted_df)} reviews from {', '.join(sources)}")
                        
                        st.markdown("### 📄 Fetched Reviews Preview")
                        st.dataframe(extracted_df[['review_text', 'source', 'product_name']].head(10), use_container_width=True)
                        
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            st.metric("📊 Total Fetched", len(extracted_df))
                        with col_b:
                            st.metric("🎯 Sources", len(sources))
                        with col_c:
                            st.metric("⭐ Avg Rating", f"{extracted_df['rating'].mean():.1f}" if 'rating' in extracted_df.columns else "N/A")
                        
                        st.info("💡 **Next Step:** Go to the **Data Ingestion** tab and click **'Analyze All Reviews'** to process these new reviews!")
                    else:
                        st.error("❌ Failed to fetch reviews. Please check your connection and try again.")
                except Exception as e:
                    st.error(f"❌ Error fetching reviews: {str(e)}")
    
    if st.session_state.df is not None and 'source' in st.session_state.df.columns:
        api_reviews = st.session_state.df[st.session_state.df['source'].isin(['API', 'Amazon', 'Flipkart', 'Twitter', 'Google'])]
        if len(api_reviews) > 0:
            st.markdown("---")
            st.markdown("### 📚 Previously Fetched Reviews")
            st.dataframe(api_reviews[['review_text', 'source', 'product_name']].head(10), use_container_width=True)
            
            if st.button("🗑️ Clear API Fetched Data", use_container_width=True):
                st.session_state.df = st.session_state.df[~st.session_state.df['source'].isin(['API', 'Amazon', 'Flipkart', 'Twitter', 'Google'])]
                st.session_state.analyzed = False
                st.success("✅ API fetched reviews cleared!")
                st.rerun()

# Footer
st.markdown("""
<div class="footer">
    <p>🔍 ReviewLens AI | Hack Malenadu '26 | Complete Customer Review Intelligence Platform</p>
    <p>🌏 Supporting English, Hindi, Kannada | 🗺️ Regional Analytics | 📋 Data Classification | ⚡ Real-time API</p>
</div>
""", unsafe_allow_html=True)