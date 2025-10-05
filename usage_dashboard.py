import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from sqlalchemy import func
from database import SessionLocal, UsageLog
import os

def show_usage_dashboard():
    """使用量ダッシュボードの表示"""
    st.title("📊 API使用量ダッシュボード")
    
    db = SessionLocal()
    
    # 全体統計の取得
    total_stats = db.query(
        func.sum(UsageLog.input_tokens).label('total_input'),
        func.sum(UsageLog.output_tokens).label('total_output'),
        func.sum(UsageLog.cost).label('total_cost'),
        func.count(UsageLog.id).label('total_requests')
    ).first()
    
    # メトリクス表示
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "総リクエスト数",
            f"{total_stats.total_requests or 0:,}"
        )
    
    with col2:
        total_tokens = (total_stats.total_input or 0) + (total_stats.total_output or 0)
        st.metric(
            "総トークン数",
            f"{total_tokens:,}"
        )
    
    with col3:
        st.metric(
            "入力トークン",
            f"{total_stats.total_input or 0:,}"
        )
    
    with col4:
        st.metric(
            "出力トークン",
            f"{total_stats.total_output or 0:,}"
        )
    
    # コスト表示
    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        total_cost = total_stats.total_cost or 0
        st.metric(
            "💰 総コスト (USD)",
            f"${total_cost:.4f}",
            delta=f"約 ¥{total_cost * 150:.2f} (¥150/USD換算)"
        )
    
    with col2:
        if total_stats.total_requests and total_stats.total_requests > 0:
            avg_cost = total_cost / total_stats.total_requests
            st.metric(
                "平均コスト/リクエスト",
                f"${avg_cost:.4f}"
            )
    
    st.divider()
    
    # 期間別の使用量
    st.subheader("📈 使用量の推移")
    
    # 過去30日のデータ取得
    thirty_days_ago = datetime.now() - timedelta(days=30)
    usage_data = db.query(UsageLog).filter(
        UsageLog.timestamp >= thirty_days_ago
    ).all()
    
    if usage_data:
        # DataFrameに変換
        df = pd.DataFrame([{
            'date': log.timestamp.date(),
            'avatar_type': log.avatar_type,
            'input_tokens': log.input_tokens,
            'output_tokens': log.output_tokens,
            'cost': log.cost
        } for log in usage_data])
        
        # 日別集計
        daily_df = df.groupby('date').agg({
            'input_tokens': 'sum',
            'output_tokens': 'sum',
            'cost': 'sum'
        }).reset_index()
        
        # トークン使用量の推移グラフ
        fig_tokens = go.Figure()
        fig_tokens.add_trace(go.Scatter(
            x=daily_df['date'],
            y=daily_df['input_tokens'],
            name='入力トークン',
            mode='lines+markers',
            line=dict(color='#87CEEB')
        ))
        fig_tokens.add_trace(go.Scatter(
            x=daily_df['date'],
            y=daily_df['output_tokens'],
            name='出力トークン',
            mode='lines+markers',
            line=dict(color='#FFB6C1')
        ))
        fig_tokens.update_layout(
            title='日別トークン使用量',
            xaxis_title='日付',
            yaxis_title='トークン数',
            hovermode='x unified'
        )
        st.plotly_chart(fig_tokens, use_container_width=True)
        
        # コストの推移グラフ
        fig_cost = px.bar(
            daily_df,
            x='date',
            y='cost',
            title='日別コスト推移',
            labels={'cost': 'コスト (USD)', 'date': '日付'}
        )
        fig_cost.update_traces(marker_color='#98FB98')
        st.plotly_chart(fig_cost, use_container_width=True)
        
        # アバター別の使用量
        st.subheader("🤖 アバター別使用統計")
        
        avatar_stats = df.groupby('avatar_type').agg({
            'input_tokens': 'sum',
            'output_tokens': 'sum',
            'cost': 'sum'
        }).reset_index()
        
        # アバター名のマッピング
        avatar_names = {
            'mental_support': '🌸 メンタルサポート',
            'tech_advisor': '💻 技術アドバイザー',
            'secretary': '📋 秘書'
        }
        avatar_stats['avatar_name'] = avatar_stats['avatar_type'].map(avatar_names)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # トークン数の円グラフ
            avatar_stats['total_tokens'] = avatar_stats['input_tokens'] + avatar_stats['output_tokens']
            fig_pie_tokens = px.pie(
                avatar_stats,
                values='total_tokens',
                names='avatar_name',
                title='アバター別トークン使用割合'
            )
            st.plotly_chart(fig_pie_tokens, use_container_width=True)
        
        with col2:
            # コストの円グラフ
            fig_pie_cost = px.pie(
                avatar_stats,
                values='cost',
                names='avatar_name',
                title='アバター別コスト割合'
            )
            st.plotly_chart(fig_pie_cost, use_container_width=True)
        
        # 詳細テーブル
        st.subheader("📋 詳細データ")
        display_stats = avatar_stats[['avatar_name', 'input_tokens', 'output_tokens', 'cost']].copy()
        display_stats.columns = ['アバター', '入力トークン', '出力トークン', 'コスト (USD)']
        display_stats['コスト (USD)'] = display_stats['コスト (USD)'].apply(lambda x: f"${x:.4f}")
        st.dataframe(display_stats, use_container_width=True, hide_index=True)
        
    else:
        st.info("まだ使用データがありません。チャットを開始すると統計が表示されます。")
    
    db.close()