import re
from datetime import datetime, timedelta
import json

def parse_schedule_request(text: str) -> dict:
    """
    自然言語からスケジュール情報を抽出
    
    例:
    - "明日の10時に会議"
    - "来週の月曜日15:00にミーティング"
    - "3日後の14時30分に打ち合わせ"
    """
    result = {
        "title": "",
        "datetime": None,
        "description": ""
    }
    
    # 時刻パターン
    time_patterns = [
        r'(\d{1,2}):(\d{2})',  # 10:30
        r'(\d{1,2})時(\d{1,2})分',  # 10時30分
        r'(\d{1,2})時',  # 10時
    ]
    
    # 日付パターン
    date_patterns = {
        '今日': 0,
        '明日': 1,
        '明後日': 2,
        '来週': 7,
    }
    
    # 曜日パターン
    weekdays = {
        '月': 0, '火': 1, '水': 2, '木': 3, '金': 4, '土': 5, '日': 6
    }
    
    # 基準時刻
    now = datetime.now()
    target_date = now.date()
    target_time = None
    
    # 時刻の抽出
    for pattern in time_patterns:
        match = re.search(pattern, text)
        if match:
            hour = int(match.group(1))
            minute = int(match.group(2)) if len(match.groups()) > 1 else 0
            target_time = datetime.strptime(f"{hour:02d}:{minute:02d}", "%H:%M").time()
            break
    
    # 日付の抽出
    for keyword, days in date_patterns.items():
        if keyword in text:
            target_date = (now + timedelta(days=days)).date()
            break
    
    # "X日後" パターン
    days_later_match = re.search(r'(\d+)日後', text)
    if days_later_match:
        days = int(days_later_match.group(1))
        target_date = (now + timedelta(days=days)).date()
    
    # 曜日指定
    for day_name, day_num in weekdays.items():
        if f'{day_name}曜' in text or f'{day_name}曜日' in text:
            days_ahead = (day_num - now.weekday() + 7) % 7
            if days_ahead == 0:
                days_ahead = 7  # 来週の同じ曜日
            target_date = (now + timedelta(days=days_ahead)).date()
            break
    
    # 日時の組み合わせ
    if target_time:
        result["datetime"] = datetime.combine(target_date, target_time)
    else:
        # 時刻が指定されていない場合は9:00をデフォルトに
        result["datetime"] = datetime.combine(target_date, datetime.strptime("09:00", "%H:%M").time())
    
    # タイトルの抽出（「に」の後の部分）
    title_match = re.search(r'に(.+)', text)
    if title_match:
        result["title"] = title_match.group(1).strip()
    else:
        result["title"] = text.strip()
    
    return result

def format_schedule_list(schedules) -> str:
    """スケジュールリストを整形"""
    if not schedules:
        return "現在、予定はありません。"
    
    result = "📅 **今後の予定**\n\n"
    for schedule in schedules:
        dt = schedule.scheduled_datetime
        result += f"- **{dt.strftime('%m/%d(%a) %H:%M')}**: {schedule.title}\n"
        if schedule.description:
            result += f"  _{schedule.description}_\n"
    
    return result

def is_schedule_command(text: str) -> bool:
    """スケジュール関連のコマンドかどうか判定"""
    schedule_keywords = [
        '予定', 'スケジュール', '予約', '会議', 'ミーティング',
        '打ち合わせ', 'アポ', 'イベント', 'タスク',
        '入れて', '追加', '登録', '確認', '教えて'
    ]
    
    return any(keyword in text for keyword in schedule_keywords)