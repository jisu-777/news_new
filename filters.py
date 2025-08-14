"""
뉴스 필터링 및 정렬 로직
"""
from typing import List, Dict, Any
from datetime import datetime
from constants import ALLOWED_SOURCES, NEGATIVE_KEYWORDS
from utils.time_window import is_within_time_window


def filter_by_allowed_sources(news_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    허용된 언론사 도메인만 필터링
    
    Args:
        news_items: 뉴스 아이템 리스트
        
    Returns:
        List[Dict[str, Any]]: 필터링된 뉴스 아이템 리스트
    """
    if not news_items:
        return []
    
    allowed_domains = set(ALLOWED_SOURCES.values())
    filtered_items = []
    
    for item in news_items:
        link = item.get('link', '')
        if not link:
            continue
            
        # 도메인 추출
        domain = extract_domain(link)
        if domain and any(allowed_domain in domain for allowed_domain in allowed_domains):
            filtered_items.append(item)
    
    return filtered_items


def filter_by_time_window(news_items: List[Dict[str, Any]], 
                         start_time: datetime, 
                         end_time: datetime) -> List[Dict[str, Any]]:
    """
    지정된 시간 윈도우 내의 뉴스만 필터링
    
    Args:
        news_items: 뉴스 아이템 리스트
        start_time: 시작 시간 (KST)
        end_time: 종료 시간 (KST)
        
    Returns:
        List[Dict[str, Any]]: 필터링된 뉴스 아이템 리스트
    """
    if not news_items:
        return []
    
    filtered_items = []
    
    for item in news_items:
        pubdate = item.get('pubDate', '')
        if not pubdate:
            continue
            
        if is_within_time_window(pubdate, start_time, end_time):
            filtered_items.append(item)
    
    return filtered_items


def filter_by_negative_keywords(news_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    비업무 분야 키워드가 포함된 뉴스 제외
    
    Args:
        news_items: 뉴스 아이템 리스트
        
    Returns:
        List[Dict[str, Any]]: 필터링된 뉴스 아이템 리스트
    """
    if not news_items:
        return []
    
    filtered_items = []
    
    for item in news_items:
        title = item.get('title', '').lower()
        description = item.get('description', '').lower()
        
        # 비업무 키워드 체크
        has_negative_keyword = False
        for keyword in NEGATIVE_KEYWORDS:
            if keyword.lower() in title or keyword.lower() in description:
                has_negative_keyword = True
                break
        
        if not has_negative_keyword:
            filtered_items.append(item)
    
    return filtered_items


def extract_domain(url: str) -> str:
    """
    URL에서 도메인 추출
    
    Args:
        url: URL 문자열
        
    Returns:
        str: 추출된 도메인
    """
    try:
        # http:// 또는 https:// 제거
        if url.startswith('http'):
            url = url.split('://', 1)[1]
        
        # 첫 번째 '/' 이전까지가 도메인
        domain = url.split('/', 1)[0]
        
        # www. 제거
        if domain.startswith('www.'):
            domain = domain[4:]
            
        return domain
    except (IndexError, AttributeError):
        return ""


def get_source_name(link: str) -> str:
    """
    링크에서 언론사명 추출
    
    Args:
        link: 뉴스 링크
        
    Returns:
        str: 언론사명
    """
    domain = extract_domain(link)
    
    # 도메인으로 언론사명 찾기
    for source_name, source_domain in ALLOWED_SOURCES.items():
        if source_domain in domain:
            return source_name
    
    return domain  # 매칭되지 않으면 도메인 반환


def apply_all_filters(news_items: List[Dict[str, Any]], 
                     start_time: datetime, 
                     end_time: datetime) -> List[Dict[str, Any]]:
    """
    모든 필터 적용
    
    Args:
        news_items: 원본 뉴스 아이템 리스트
        start_time: 시작 시간
        end_time: 종료 시간
        
    Returns:
        List[Dict[str, Any]]: 모든 필터가 적용된 뉴스 아이템 리스트
    """
    if not news_items:
        return []
    
    # 1. 허용된 언론사만 필터링
    filtered_by_source = filter_by_allowed_sources(news_items)
    
    # 2. 시간 윈도우 필터링
    filtered_by_time = filter_by_time_window(filtered_by_source, start_time, end_time)
    
    # 3. 비업무 키워드 필터링
    filtered_by_keywords = filter_by_negative_keywords(filtered_by_time)
    
    return filtered_by_keywords


def add_source_info(news_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    뉴스 아이템에 언론사 정보 추가
    
    Args:
        news_items: 뉴스 아이템 리스트
        
    Returns:
        List[Dict[str, Any]]: 언론사 정보가 추가된 뉴스 아이템 리스트
    """
    for item in news_items:
        link = item.get('link', '')
        item['source_name'] = get_source_name(link)
        item['domain'] = extract_domain(link)
    
    return news_items
