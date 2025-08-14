"""
날짜 윈도우 계산 및 pubDate 파싱 유틸리티
"""
from datetime import datetime, timedelta
from typing import Tuple, Optional
import pytz
import re


def get_default_time_window() -> Tuple[datetime, datetime]:
    """
    기본 날짜 윈도우 계산
    - 전일 오전 10:00 ~ 당일 오전 10:00 (KST)
    - 월요일은 금요일 오전 10:00 ~ 월요일 오전 10:00
    
    Returns:
        Tuple[datetime, datetime]: (시작시간, 종료시간) KST 기준
    """
    kst = pytz.timezone('Asia/Seoul')
    now = datetime.now(kst)
    
    # 오전 10시 기준으로 날짜 계산
    today_10am = now.replace(hour=10, minute=0, second=0, microsecond=0)
    
    # 오전 10시 이전이면 전일 10시부터, 이후면 당일 10시부터
    if now.hour < 10:
        end_time = today_10am
        start_time = end_time - timedelta(days=1)
    else:
        start_time = today_10am
        end_time = start_time + timedelta(days=1)
    
    # 월요일 특별 처리
    if now.weekday() == 0:  # 월요일
        start_time = end_time - timedelta(days=3)  # 금요일 10시부터
    
    return start_time, end_time


def parse_pubdate(pubdate_str: str) -> Optional[datetime]:
    """
    네이버 뉴스 API의 pubDate를 파싱하여 KST datetime으로 변환
    
    Args:
        pubdate_str: "Mon, 18 Dec 2023 01:30:00 +0900" 형태의 문자열
        
    Returns:
        Optional[datetime]: 파싱된 KST datetime, 실패시 None
    """
    try:
        # RFC 822 형식 파싱
        dt = datetime.strptime(pubdate_str, "%a, %d %b %Y %H:%M:%S %z")
        
        # UTC로 변환 후 KST로 변환
        utc_dt = dt.astimezone(pytz.UTC)
        kst = pytz.timezone('Asia/Seoul')
        kst_dt = utc_dt.astimezone(kst)
        
        return kst_dt
    except (ValueError, AttributeError):
        return None


def is_within_time_window(pubdate_str: str, start_time: datetime, end_time: datetime) -> bool:
    """
    pubDate가 지정된 시간 윈도우 내에 있는지 확인
    
    Args:
        pubdate_str: pubDate 문자열
        start_time: 시작 시간 (KST)
        end_time: 종료 시간 (KST)
        
    Returns:
        bool: 시간 윈도우 내에 있으면 True
    """
    parsed_time = parse_pubdate(pubdate_str)
    if parsed_time is None:
        return False
    
    return start_time <= parsed_time <= end_time


def format_datetime_for_display(dt: datetime) -> str:
    """
    화면 표시용 datetime 포맷팅
    
    Args:
        dt: datetime 객체
        
    Returns:
        str: "2023-12-18 10:30 (월)" 형태의 문자열
    """
    weekdays = ["월", "화", "수", "목", "금", "토", "일"]
    return f"{dt.strftime('%Y-%m-%d %H:%M')} ({weekdays[dt.weekday()]})"


def get_time_window_display(start_time: datetime, end_time: datetime) -> str:
    """
    시간 윈도우를 화면 표시용으로 포맷팅
    
    Args:
        start_time: 시작 시간
        end_time: 종료 시간
        
    Returns:
        str: "2023-12-17 10:00 ~ 2023-12-18 10:00" 형태의 문자열
    """
    return f"{start_time.strftime('%m-%d %H:%M')} ~ {end_time.strftime('%m-%d %H:%M')}"
