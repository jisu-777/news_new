"""
사이드바 UI 컴포넌트
"""
import streamlit as st
from datetime import datetime, timedelta
from typing import Tuple, Optional, List
from constants import GROUP_DEFS, KEYWORD_DEFS, DEFAULT_PRINT_THRESHOLD
from utils.time_window import get_default_time_window


def render_sidebar() -> Tuple[str, List[str], datetime, datetime, int, int, bool, float]:
    """
    사이드바 렌더링 및 설정값 반환
    
    Returns:
        Tuple: (group1, selected_keywords, start_time, end_time, max_pages, keyword_limit, use_gpt, threshold)
    """
    st.sidebar.title("🔍 검색 설정")
    
    # Group1 선택
    group1_options = list(GROUP_DEFS.keys())
    selected_group1 = st.sidebar.selectbox(
        "📊 Group1 (카테고리)",
        group1_options,
        help="검색할 뉴스 카테고리를 선택하세요"
    )
    
    # Group2 키워드 선택
    group2_keywords = get_group2_keywords(selected_group1)
    if isinstance(group2_keywords, list):
        # 키워드 개수 제한
        keyword_limit = st.sidebar.slider(
            "🔑 키워드 개수 제한",
            min_value=1,
            max_value=len(group2_keywords),
            value=min(10, len(group2_keywords)),
            help="사용할 키워드 개수를 제한하세요"
        )
        
        # 제한된 키워드만 선택
        limited_keywords = group2_keywords[:keyword_limit]
        selected_keywords = st.sidebar.multiselect(
            "🎯 Group2 (키워드)",
            limited_keywords,
            default=limited_keywords[:5] if len(limited_keywords) >= 5 else limited_keywords,
            help="검색에 사용할 키워드를 선택하세요"
        )
    else:
        # 단일 키워드 그룹
        keyword_limit = 1
        selected_keywords = [group2_keywords]
    
    st.sidebar.divider()
    
    # 날짜 설정
    st.sidebar.subheader("📅 검색 기간")
    
    # 기본 시간 윈도우
    default_start, default_end = get_default_time_window()
    
    # 수동 조정 가능
    use_custom_date = st.sidebar.checkbox("수동으로 날짜 조정", value=False)
    
    if use_custom_date:
        start_time = st.sidebar.datetime_input(
            "시작 시간 (KST)",
            value=default_start,
            help="검색 시작 시간을 설정하세요"
        )
        end_time = st.sidebar.datetime_input(
            "종료 시간 (KST)",
            value=default_end,
            help="검색 종료 시간을 설정하세요"
        )
    else:
        start_time = default_start
        end_time = default_end
        st.sidebar.info(f"기본 기간: {start_time.strftime('%m-%d %H:%M')} ~ {end_time.strftime('%m-%d %H:%M')}")
    
    st.sidebar.divider()
    
    # 검색 설정
    st.sidebar.subheader("⚙️ 검색 설정")
    
    max_pages = st.sidebar.slider(
        "📄 키워드당 최대 페이지 수",
        min_value=1,
        max_value=5,
        value=2,
        help="각 키워드별로 검색할 최대 페이지 수입니다"
    )
    
    st.sidebar.divider()
    
    # GPT 지면판별 설정
    st.sidebar.subheader("🤖 지면판별 (GPT)")
    
    use_gpt = st.sidebar.checkbox(
        "GPT로 지면뉴스 판별",
        value=False,
        help="GPT를 사용하여 지면뉴스 가능성을 판별합니다 (비용 발생)"
    )
    
    if use_gpt:
        threshold = st.sidebar.slider(
            "📊 지면 가능성 임계값",
            min_value=0.0,
            max_value=1.0,
            value=DEFAULT_PRINT_THRESHOLD,
            step=0.1,
            help="이 값 이상의 점수를 받은 뉴스만 표시됩니다"
        )
        
        # 비용 추정
        if selected_keywords:
            estimated_cost = estimate_gpt_cost(len(selected_keywords))
            st.sidebar.info(f"예상 비용: ${estimated_cost}")
    else:
        threshold = DEFAULT_PRINT_THRESHOLD
    
    st.sidebar.divider()
    
    # 검색 실행 버튼
    search_button = st.sidebar.button(
        "🔍 검색 실행",
        type="primary",
        use_container_width=True
    )
    
    return (
        selected_group1,
        selected_keywords,
        start_time,
        end_time,
        max_pages,
        keyword_limit,
        use_gpt,
        threshold
    )


def get_group2_keywords(group1: str) -> List[str]:
    """
    Group1에 해당하는 Group2 키워드 반환
    
    Args:
        group1: 선택된 Group1
        
    Returns:
        List[str]: Group2 키워드 리스트
    """
    group2 = GROUP_DEFS.get(group1)
    
    if isinstance(group2, list):
        return group2
    elif isinstance(group2, str):
        return KEYWORD_DEFS.get(group2, [])
    else:
        return []


def estimate_gpt_cost(keyword_count: int) -> float:
    """
    GPT 사용 비용 추정 (간단 버전)
    
    Args:
        keyword_count: 키워드 개수
        
    Returns:
        float: 예상 비용 (USD)
    """
    # 키워드당 평균 50개 뉴스, 뉴스당 $0.0002로 추정
    estimated_news = keyword_count * 50
    cost_per_news = 0.0002
    
    return round(estimated_news * cost_per_news, 4)


def show_search_summary(group1: str, keywords: List[str], start_time: datetime, end_time: datetime, use_gpt: bool):
    """
    검색 설정 요약 표시
    
    Args:
        group1: 선택된 Group1
        keywords: 선택된 키워드
        start_time: 시작 시간
        end_time: 종료 시간
        use_gpt: GPT 사용 여부
    """
    st.sidebar.divider()
    st.sidebar.subheader("📋 검색 요약")
    
    st.sidebar.write(f"**카테고리:** {group1}")
    st.sidebar.write(f"**키워드:** {len(keywords)}개")
    st.sidebar.write(f"**기간:** {start_time.strftime('%m-%d %H:%M')} ~ {end_time.strftime('%m-%d %H:%M')}")
    st.sidebar.write(f"**GPT 판별:** {'사용' if use_gpt else '미사용'}")
    
    if keywords:
        st.sidebar.write("**선택된 키워드:**")
        for i, keyword in enumerate(keywords[:5], 1):
            st.sidebar.write(f"{i}. {keyword}")
        if len(keywords) > 5:
            st.sidebar.write(f"... 외 {len(keywords) - 5}개")
