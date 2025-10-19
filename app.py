import streamlit as st
from anthropic import Anthropic
import os
from dotenv import load_dotenv
from database import init_db, add_conversation, get_conversations, add_usage_log, get_schedules, add_schedule
from avatar_configs import get_avatar_config, get_avatar_list
from scheduler import parse_schedule_request, format_schedule_list, is_schedule_command
from usage_dashboard import show_usage_dashboard
from schedule_page import show_schedule_page
import json

# 環境変数の取得
load_dotenv()

# DBの初期化
init_db()

# Page config
st.set_page_config(
    page_title="Personal LLM Assistant",
    page_icon="🤖",
    layout="wide"
)

# Anthropicクライアントの初期化
@st.cache_resource
def get_anthropic_client():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        st.error("ANTHROPIC_API_KEY not found in .env file")
        st.stop()
    return Anthropic(api_key=api_key)

client = get_anthropic_client()

# セッション状態の初期化
if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_avatar" not in st.session_state:
    st.session_state.current_avatar = "secretary"

if "current_page" not in st.session_state:
    st.session_state.current_page = "chat"

# スライドバー設定
with st.sidebar:
    st.title("🤖 Personal LLM Assistant")
    
    # ページ選択
    st.subheader("📑 ページ")
    page = st.radio(
        "ページを選択",
        ["💬 チャット", "📊 使用量", "📅 スケジュール"],
        key="page_selector",
        label_visibility="collapsed"
    )
    
    if page == "💬 チャット":
        st.session_state.current_page = "chat"
    elif page == "📊 使用量":
        st.session_state.current_page = "usage"
    elif page == "📅 スケジュール":
        st.session_state.current_page = "schedule"
    
    st.divider()
    
    if st.session_state.current_page == "chat":
        # Avatar selection
        st.subheader("🤖 アバター選択")
        avatar_options = get_avatar_list()
        
        selected_avatar = st.selectbox(
            "話したいアバターを選択",
            options=[av[0] for av in avatar_options],
            format_func=lambda x: f"{[av[2] for av in avatar_options if av[0]==x][0]} {[av[1] for av in avatar_options if av[0]==x][0]}",
            key="avatar_selector"
        )
        
        # アバター変更ハンドリング設定
        if selected_avatar != st.session_state.current_avatar:
            st.session_state.current_avatar = selected_avatar
            # Load conversation history for selected avatar
            conversations = get_conversations(selected_avatar)
            st.session_state.messages = [
                {"role": conv.role, "content": conv.content}
                for conv in conversations
            ]
            st.rerun()
        
        # 現在表示されているアバターの状態
        current_config = get_avatar_config(st.session_state.current_avatar)
        st.markdown(f"### {current_config['icon']} {current_config['name']}")
        
        st.divider()
        
        # Quick stats
        st.subheader("📊 簡易統計")
        from database import SessionLocal, UsageLog
        from sqlalchemy import func
        
        db = SessionLocal()
        today_stats = db.query(
            func.count(UsageLog.id).label('count'),
            func.sum(UsageLog.cost).label('cost')
        ).filter(
            func.date(UsageLog.timestamp) == func.date(func.now())
        ).first()
        db.close()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("今日のリクエスト", f"{today_stats.count or 0}")
        with col2:
            st.metric("今日のコスト", f"${today_stats.cost or 0:.3f}")
        
        st.divider()
        
        # チャット履歴のクリア
        if st.button("🗑️ チャット履歴をクリア", type="secondary", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

# メイン部
if st.session_state.current_page == "usage":
    show_usage_dashboard()

elif st.session_state.current_page == "schedule":
    show_schedule_page()

else:  # チャットページ
    current_config = get_avatar_config(st.session_state.current_avatar)
    st.title(f"{current_config['icon']} {current_config['name']}")
    
    # チャットメッセージの表示
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # チャットメッセージ入力
    if prompt := st.chat_input("メッセージを入力..."):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # DB への保存
        add_conversation(st.session_state.current_avatar, "user", prompt)
        
        # ユーザーメッセージの表示
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # スケジュール関連の処理（秘書アバターの場合）
        schedule_handled = False
        if st.session_state.current_avatar == "secretary" and is_schedule_command(prompt):
            # スケジュール確認の場合
            if any(word in prompt for word in ['確認', '教えて', '見せて', '一覧', 'リスト']):
                schedules = get_schedules(limit=20)
                response_text = format_schedule_list(schedules)
                schedule_handled = True
            # スケジュール追加の場合
            elif any(word in prompt for word in ['入れて', '追加', '登録', '予約']):
                try:
                    schedule_info = parse_schedule_request(prompt)
                    if schedule_info["datetime"] and schedule_info["title"]:
                        add_schedule(
                            schedule_info["title"],
                            schedule_info["datetime"],
                            ""
                        )
                        dt_str = schedule_info["datetime"].strftime("%Y年%m月%d日 %H:%M")
                        response_text = f"✅ スケジュールを追加しました:\n\n**{schedule_info['title']}**\n📅 {dt_str}"
                        schedule_handled = True
                except Exception as e:
                    response_text = f"スケジュールの解析に失敗しました。もう一度具体的に教えてください。\n例: 「明日の10時に会議を入れて」"
                    schedule_handled = True
        
        # アシスタントの返答生成
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            if schedule_handled:
                # スケジュール処理の結果を表示
                message_placeholder.markdown(response_text)
                full_response = response_text
            else:
                # 通常のLLM応答
                full_response = ""
                
                try:
                    # API
                    api_messages = [{"role": m["role"], "content": m["content"]} 
                                  for m in st.session_state.messages]
                    
                    # スケジュール情報をコンテキストに追加（秘書の場合）
                    system_prompt = current_config["system_prompt"]
                    if st.session_state.current_avatar == "secretary":
                        schedules = get_schedules(limit=10)
                        if schedules:
                            schedule_context = "\n\n現在登録されている予定:\n"
                            for s in schedules:
                                schedule_context += f"- {s.scheduled_datetime.strftime('%m/%d %H:%M')}: {s.title}\n"
                            system_prompt += schedule_context
                    
                    # Claude API の呼び出し
                    with client.messages.stream(
                        model="claude-sonnet-4-20250514",
                        max_tokens=4096,
                        system=system_prompt,
                        messages=api_messages
                    ) as stream:
                        for text in stream.text_stream:
                            full_response += text
                            message_placeholder.markdown(full_response + "▌")
                    
                    message_placeholder.markdown(full_response)
                    
                    # 使用情報の取得
                    message = stream.get_final_message()
                    input_tokens = message.usage.input_tokens
                    output_tokens = message.usage.output_tokens
                    
                    # コスト計算
                    input_cost = float(os.getenv("CLAUDE_SONNET_4_5_INPUT_COST", 3.0))
                    output_cost = float(os.getenv("CLAUDE_SONNET_4_5_OUTPUT_COST", 15.0))
                    total_cost = (input_tokens / 1_000_000 * input_cost) + (output_tokens / 1_000_000 * output_cost)
                    
                    # 使用履歴の保存
                    add_usage_log(
                        st.session_state.current_avatar,
                        input_tokens,
                        output_tokens,
                        total_cost
                    )
                    
                except Exception as e:
                    st.error(f"エラーが発生しました: {str(e)}")
                    full_response = "申し訳ございません。エラーが発生しました。"
                    message_placeholder.markdown(full_response)
        
        # チャット履歴のアシスタントの返答の追加
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        
        # DB への保存
        add_conversation(st.session_state.current_avatar, "assistant", full_response)
        
        st.rerun()