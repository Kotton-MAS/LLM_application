import streamlit as st
from datetime import datetime, timedelta
from database import SessionLocal, Schedule, add_schedule
import pandas as pd

def show_schedule_page():
    """スケジュール管理ページの表示"""
    st.title("📅 スケジュール管理")
    
    tab1, tab2 = st.tabs(["📋 予定一覧", "➕ 新規追加"])
    
    db = SessionLocal()
    
    with tab1:
        # フィルター
        col1, col2 = st.columns([3, 1])
        with col1:
            show_completed = st.checkbox("完了済みも表示", value=False)
        with col2:
            if st.button("🔄 更新", use_container_width=True):
                st.rerun()
        
        # スケジュール取得
        query = db.query(Schedule)
        if not show_completed:
            query = query.filter(Schedule.completed == 0)
        
        schedules = query.order_by(Schedule.scheduled_datetime).all()
        
        if schedules:
            st.subheader(f"📌 予定: {len(schedules)}件")
            
            # 今日、明日、それ以降に分類
            now = datetime.now()
            today_end = now.replace(hour=23, minute=59, second=59)
            tomorrow_end = (now + timedelta(days=1)).replace(hour=23, minute=59, second=59)
            
            today_schedules = [s for s in schedules if s.scheduled_datetime <= today_end]
            tomorrow_schedules = [s for s in schedules if today_end < s.scheduled_datetime <= tomorrow_end]
            later_schedules = [s for s in schedules if s.scheduled_datetime > tomorrow_end]
            
            # 今日の予定
            if today_schedules:
                st.markdown("### 🔴 今日の予定")
                for schedule in today_schedules:
                    display_schedule_card(schedule, db)
                st.divider()
            
            # 明日の予定
            if tomorrow_schedules:
                st.markdown("### 🟡 明日の予定")
                for schedule in tomorrow_schedules:
                    display_schedule_card(schedule, db)
                st.divider()
            
            # それ以降の予定
            if later_schedules:
                st.markdown("### 🟢 今後の予定")
                for schedule in later_schedules:
                    display_schedule_card(schedule, db)
        else:
            st.info("📭 予定がありません")
    
    with tab2:
        st.subheader("新しい予定を追加")
        
        with st.form("add_schedule_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                schedule_date = st.date_input(
                    "日付",
                    value=datetime.now().date(),
                    min_value=datetime.now().date()
                )
            
            with col2:
                schedule_time = st.time_input(
                    "時刻",
                    value=datetime.now().replace(minute=0, second=0, microsecond=0).time()
                )
            
            title = st.text_input("タイトル", placeholder="例: チーム会議")
            description = st.text_area("詳細（任意）", placeholder="議題、場所などを記入")
            
            submitted = st.form_submit_button("➕ 追加", use_container_width=True, type="primary")
            
            if submitted:
                if title:
                    scheduled_datetime = datetime.combine(schedule_date, schedule_time)
                    add_schedule(title, scheduled_datetime, description)
                    st.success(f"✅ 予定を追加しました: {title}")
                    st.rerun()
                else:
                    st.error("タイトルを入力してください")
    
    db.close()

def display_schedule_card(schedule, db):
    """スケジュールカードの表示"""
    col1, col2, col3 = st.columns([6, 2, 1])
    
    with col1:
        # 時刻とタイトル
        time_str = schedule.scheduled_datetime.strftime("%H:%M")
        date_str = schedule.scheduled_datetime.strftime("%m/%d (%a)")
        
        if schedule.completed:
            st.markdown(f"~~**{time_str}** - {date_str} | {schedule.title}~~")
        else:
            st.markdown(f"**{time_str}** - {date_str} | {schedule.title}")
        
        # 詳細
        if schedule.description:
            st.caption(schedule.description)
    
    with col2:
        # 完了ボタン
        if not schedule.completed:
            if st.button("✓ 完了", key=f"complete_{schedule.id}", use_container_width=True):
                schedule.completed = 1
                db.commit()
                st.rerun()
    
    with col3:
        # 削除ボタン
        if st.button("🗑️", key=f"delete_{schedule.id}", use_container_width=True):
            db.delete(schedule)
            db.commit()
            st.rerun()
    
    st.divider()