"""
뉴스 결과 카드 렌더러 및 로드모어 기능
"""
import streamlit as st
import pandas as pd
from typing import List, Dict, Any
from utils.time_window import format_datetime_for_display
from utils.dedupe import get_matched_keywords, format_keywords_display


def render_news_cards(news_items: List[Dict[str, Any]], 
                     keywords: List[str],
                     items_per_page: int = 10) -> None:
    """
    뉴스 결과를 카드 형태로 렌더링
    
    Args:
        news_items: 뉴스 아이템 리스트
        keywords: 검색에 사용된 키워드
        items_per_page: 페이지당 표시할 아이템 수
    """
    if not news_items:
        st.warning("검색 결과가 없습니다.")
        return
    
    # 세션 상태 초기화
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 0
    
    # 총 건수 표시
    total_count = len(news_items)
    st.subheader(f"📰 검색 결과 ({total_count:,}건)")
    
    # 페이지네이션 계산
    total_pages = (total_count + items_per_page - 1) // items_per_page
    start_idx = st.session_state.current_page * items_per_page
    end_idx = min(start_idx + items_per_page, total_count)
    
    # 현재 페이지 아이템
    current_items = news_items[start_idx:end_idx]
    
    # 카드 렌더링
    for i, item in enumerate(current_items):
        render_single_news_card(item, keywords, start_idx + i + 1)
    
    # 페이지네이션 컨트롤
    render_pagination_controls(total_pages, total_count, items_per_page)
    
    # 로드모어 버튼
    if end_idx < total_count:
        render_load_more_button()


def render_single_news_card(item: Dict[str, Any], keywords: List[str], item_number: int) -> None:
    """
    단일 뉴스 카드 렌더링
    
    Args:
        item: 뉴스 아이템
        keywords: 검색 키워드
        item_number: 아이템 번호
    """
    with st.container():
        st.markdown("---")
        
        # 제목과 링크
        title = item.get('title', '').replace('<b>', '').replace('</b>', '')
        link = item.get('link', '')
        
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"**{item_number}. {title}**")
        with col2:
            if link:
                st.link_button("🔗 원문", link, use_container_width=True)
        
        # 요약
        description = item.get('description', '').replace('<b>', '').replace('</b>', '')
        if description:
            st.write(description)
        
        # 메타 정보
        col1, col2, col3 = st.columns([2, 2, 2])
        
        with col1:
            # 발행시각
            pubdate = item.get('pubDate', '')
            if pubdate:
                try:
                    from utils.time_window import parse_pubdate
                    parsed_time = parse_pubdate(pubdate)
                    if parsed_time:
                        time_str = format_datetime_for_display(parsed_time)
                        st.write(f"🕐 {time_str}")
                except:
                    st.write(f"🕐 {pubdate}")
        
        with col2:
            # 언론사
            source_name = item.get('source_name', '')
            if source_name:
                st.write(f"📰 {source_name}")
        
        with col3:
            # 도메인
            domain = item.get('domain', '')
            if domain:
                st.write(f"🌐 {domain}")
        
        # 매칭된 키워드
        matched_keywords = get_matched_keywords(title, description, keywords)
        if matched_keywords:
            keywords_str = format_keywords_display(matched_keywords)
            st.write(f"🎯 **매칭 키워드:** {keywords_str}")
        
        # GPT 지면판별 점수 (있는 경우)
        print_score = item.get('print_score')
        if print_score is not None:
            score_color = get_score_color(print_score)
            st.markdown(f"📊 **지면 가능성:** :{score_color}[{print_score:.2f}]")


def render_pagination_controls(total_pages: int, total_count: int, items_per_page: int) -> None:
    """
    페이지네이션 컨트롤 렌더링
    
    Args:
        total_pages: 총 페이지 수
        total_count: 총 아이템 수
        items_per_page: 페이지당 아이템 수
    """
    if total_pages <= 1:
        return
    
    st.markdown("---")
    
    col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
    
    with col1:
        if st.button("⏮️ 처음", use_container_width=True, key="first_page_button"):
            st.session_state.current_page = 0
            st.rerun()
    
    with col2:
        if st.button("◀️ 이전", use_container_width=True, disabled=st.session_state.current_page == 0, key="prev_page_button"):
            st.session_state.current_page = max(0, st.session_state.current_page - 1)
            st.rerun()
    
    with col3:
        current_page = st.session_state.current_page + 1
        st.write(f"**{current_page} / {total_pages}** 페이지")
        st.write(f"({total_count:,}건 중 {st.session_state.current_page * items_per_page + 1:,}-{min((st.session_state.current_page + 1) * items_per_page, total_count):,}건)")
    
    with col4:
        if st.button("다음 ▶️", use_container_width=True, disabled=st.session_state.current_page >= total_pages - 1, key="next_page_button"):
            st.session_state.current_page = min(total_pages - 1, st.session_state.current_page + 1)
            st.rerun()
    
    with col5:
        if st.button("마지막 ⏭️", use_container_width=True, key="last_page_button"):
            st.session_state.current_page = total_pages - 1
            st.rerun()


def render_load_more_button() -> None:
    """로드모어 버튼 렌더링"""
    st.markdown("---")
    
    if st.button("📖 더 보기", use_container_width=True, type="secondary", key="load_more_button"):
        st.session_state.current_page += 1
        st.rerun()


def get_score_color(score: float) -> str:
    """
    지면 가능성 점수에 따른 색상 반환
    
    Args:
        score: 지면 가능성 점수 (0.0~1.0)
        
    Returns:
        str: Streamlit 색상 코드
    """
    if score >= 0.8:
        return "green"
    elif score >= 0.6:
        return "blue"
    elif score >= 0.4:
        return "orange"
    else:
        return "red"


def render_results_summary(news_items: List[Dict[str, Any]], 
                         group1: str, 
                         keywords: List[str],
                         start_time, 
                         end_time,
                         use_gpt: bool,
                         threshold: float) -> None:
    """
    검색 결과 요약 표시
    
    Args:
        news_items: 뉴스 아이템 리스트
        group1: 선택된 Group1
        keywords: 선택된 키워드
        start_time: 시작 시간
        end_time: 종료 시간
        use_gpt: GPT 사용 여부
        threshold: 지면판별 임계값
    """
    if not news_items:
        return
    
    st.markdown("---")
    st.subheader("📊 검색 결과 요약")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**검색 카테고리:** {group1}")
        st.write(f"**사용 키워드:** {len(keywords)}개")
        st.write(f"**검색 기간:** {start_time.strftime('%m-%d %H:%M')} ~ {end_time.strftime('%m-%d %H:%M')}")
    
    with col2:
        st.write(f"**총 검색 결과:** {len(news_items):,}건")
        
        if use_gpt:
            gpt_filtered = [item for item in news_items if item.get('print_score', 0) >= threshold]
            st.write(f"**GPT 필터링 후:** {len(gpt_filtered):,}건")
            st.write(f"**지면판별 임계값:** {threshold}")
        else:
            st.write("**GPT 필터링:** 미사용")
    
    # 언론사별 분포
    source_counts = {}
    for item in news_items:
        source = item.get('source_name', '기타')
        source_counts[source] = source_counts.get(source, 0) + 1
    
    if source_counts:
        st.write("**언론사별 분포:**")
        for source, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            st.write(f"- {source}: {count:,}건")


def render_dataframe_preview(news_items: List[Dict[str, Any]]) -> None:
    """
    결과 DataFrame 미리보기 및 CSV 다운로드
    
    Args:
        news_items: 뉴스 아이템 리스트
    """
    if not news_items:
        return
    
    st.markdown("---")
    st.subheader("📋 데이터 미리보기")
    
    # DataFrame 생성
    df_data = []
    for item in news_items:
        df_data.append({
            '제목': item.get('title', '').replace('<b>', '').replace('</b>', ''),
            '요약': item.get('description', '').replace('<b>', '').replace('</b>', ''),
            '링크': item.get('link', ''),
            '발행시각': item.get('pubDate', ''),
            '언론사': item.get('source_name', ''),
            '도메인': item.get('domain', ''),
            '지면점수': item.get('print_score', '')
        })
    
    df = pd.DataFrame(df_data)
    
    # 미리보기 표시
    st.dataframe(df, use_container_width=True)
    
    # CSV 다운로드
    csv_data = df.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label="📥 CSV 다운로드",
        data=csv_data,
        file_name=f"뉴스검색결과_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        use_container_width=True
    )
