"""
사이드바 UI 컴포넌트
"""
import streamlit as st
from datetime import datetime, timedelta
from typing import Tuple, Optional, List
from constants import GROUP_DEFS, KEYWORD_DEFS, DEFAULT_PRINT_THRESHOLD
from utils.time_window import get_default_time_window


def render_sidebar() -> Tuple[List[str], List[str], datetime, datetime, int, int, bool, float]:
    """
    사이드바 렌더링 및 설정값 반환
    
    Returns:
        Tuple: (selected_groups, selected_keywords, start_time, end_time, max_pages, keyword_limit, use_gpt, threshold)
    """
    st.sidebar.title("🔍 뉴스 검색 설정")
    st.sidebar.markdown("**카테고리 선택 → 관련 키워드 자동 포함**")
    
    # Group1 다중선택 (카테고리)
    group1_options = list(GROUP_DEFS.keys())
    selected_groups = st.sidebar.multiselect(
        "📊 카테고리 선택",
        group1_options,
        default=group1_options[:2],  # 기본값 2개
        help="검색할 뉴스 카테고리를 하나 이상 선택하세요"
    )
    
    # Group2 키워드 자동 포함 (사용자에게 보이지 않음)
    all_keywords = []
    if selected_groups:
        for group in selected_groups:
            group2_keywords = get_group2_keywords(group)
            if isinstance(group2_keywords, list):
                all_keywords.extend(group2_keywords)
            else:
                all_keywords.append(group2_keywords)
        
        # 중복 제거
        all_keywords = list(set(all_keywords))
        
        # 키워드 개수 제한 (백엔드에서만 사용)
        keyword_limit = min(8, len(all_keywords))  # 기본값 8개로 고정
        
        # 선택된 키워드 (사용자에게는 보이지 않음)
        selected_keywords = all_keywords[:keyword_limit]
        
        # 간단한 정보만 표시
        st.sidebar.info(f"📝 **{len(selected_groups)}개 카테고리 선택됨**")
    else:
        # 그룹이 선택되지 않은 경우
        keyword_limit = 0
        selected_keywords = []
        st.sidebar.warning("⚠️ 카테고리를 하나 이상 선택해주세요")
    
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
        value=1,  # 기본값 1페이지
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
        use_container_width=True,
        key="sidebar_search_button"
    )
    
    return (
        selected_groups,
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


def show_enhanced_search_summary(selected_groups: List[str], keywords: List[str], start_time: datetime, end_time: datetime, use_gpt: bool):
    """
    향상된 검색 설정 요약 표시 (카테고리별 분류 포함)
    
    Args:
        selected_groups: 선택된 Group1 리스트
        keywords: 선택된 키워드
        start_time: 시작 시간
        end_time: 종료 시간
        use_gpt: GPT 사용 여부
    """
    st.sidebar.divider()
    st.sidebar.subheader("📋 검색 요약")
    
    groups_str = ", ".join(selected_groups)
    st.sidebar.write(f"**카테고리:** {groups_str}")
    st.sidebar.write(f"**키워드:** {len(keywords)}개 (자동 선택)")
    st.sidebar.write(f"**기간:** {start_time.strftime('%m-%d %H:%M')} ~ {end_time.strftime('%m-%d %H:%M')}")
    st.sidebar.write(f"**GPT 판별:** {'사용' if use_gpt else '미사용'}")
