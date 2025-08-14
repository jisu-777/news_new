"""
중복 제거 및 데이터 정리 유틸리티
"""
from typing import List, Dict, Any
import pandas as pd


def remove_duplicate_links(news_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    링크 기준으로 중복 뉴스 제거
    
    Args:
        news_items: 뉴스 아이템 리스트
        
    Returns:
        List[Dict[str, Any]]: 중복 제거된 뉴스 아이템 리스트
    """
    if not news_items:
        return []
    
    # 링크 기준으로 중복 제거 (마지막 항목 유지)
    seen_links = set()
    unique_items = []
    
    for item in reversed(news_items):  # 역순으로 처리하여 최신 항목 우선
        link = item.get('link', '')
        if link and link not in seen_links:
            seen_links.add(link)
            unique_items.append(item)
    
    # 원래 순서로 복원
    return list(reversed(unique_items))


def sort_by_pubdate(news_items: List[Dict[str, Any]], reverse: bool = True) -> List[Dict[str, Any]]:
    """
    발행시각 기준으로 정렬
    
    Args:
        news_items: 뉴스 아이템 리스트
        reverse: True면 내림차순(최신순), False면 오름차순
        
    Returns:
        List[Dict[str, Any]]: 정렬된 뉴스 아이템 리스트
    """
    if not news_items:
        return []
    
    # pubDate가 있는 항목만 필터링
    valid_items = [item for item in news_items if item.get('pubDate')]
    
    # pubDate 기준으로 정렬
    sorted_items = sorted(
        valid_items,
        key=lambda x: x.get('pubDate', ''),
        reverse=reverse
    )
    
    # pubDate가 없는 항목은 맨 뒤에 추가
    invalid_items = [item for item in news_items if not item.get('pubDate')]
    sorted_items.extend(invalid_items)
    
    return sorted_items


def clean_news_data(news_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    뉴스 데이터 정리 (중복 제거 + 정렬)
    
    Args:
        news_items: 원본 뉴스 아이템 리스트
        
    Returns:
        List[Dict[str, Any]]: 정리된 뉴스 아이템 리스트
    """
    if not news_items:
        return []
    
    # 중복 제거
    unique_items = remove_duplicate_links(news_items)
    
    # 발행시각 기준 내림차순 정렬
    sorted_items = sort_by_pubdate(unique_items, reverse=True)
    
    return sorted_items


def get_matched_keywords(title: str, description: str, keywords: List[str]) -> List[str]:
    """
    제목과 요약에서 매칭된 키워드 추출
    
    Args:
        title: 뉴스 제목
        description: 뉴스 요약
        keywords: 검색 키워드 리스트
        
    Returns:
        List[str]: 매칭된 키워드 리스트
    """
    if not keywords:
        return []
    
    text = f"{title} {description}".lower()
    matched = []
    
    for keyword in keywords:
        if keyword.lower() in text:
            matched.append(keyword)
    
    return matched[:5]  # 최대 5개까지만 반환


def format_keywords_display(matched_keywords: List[str]) -> str:
    """
    매칭된 키워드를 화면 표시용으로 포맷팅
    
    Args:
        matched_keywords: 매칭된 키워드 리스트
        
    Returns:
        str: 포맷팅된 키워드 문자열
    """
    if not matched_keywords:
        return ""
    
    if len(matched_keywords) <= 3:
        return ", ".join(matched_keywords)
    else:
        return ", ".join(matched_keywords[:3]) + f" 외 {len(matched_keywords) - 3}개"
