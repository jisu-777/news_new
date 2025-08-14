"""
뉴스 결과 카드 렌더러 및 로드모어 기능
"""
import streamlit as st
import pandas as pd
from typing import List, Dict, Any
from utils.time_window import format_datetime_for_display
from utils.dedupe import get_matched_keywords, format_keywords_display


def render_news_cards(news_items: List[Dict[str, Any]], 
                     selected_groups: List[str],
                     items_per_page: int = 10) -> None:
    """
    뉴스 결과를 카드 형태로 렌더링
    
    Args:
        news_items: 뉴스 아이템 리스트
        selected_groups: 선택된 카테고리 리스트
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
        render_single_news_card(item, selected_groups, start_idx + i + 1)
    
    # 페이지네이션 컨트롤
    render_pagination_controls(total_pages, total_count, items_per_page)
    
    # 로드모어 버튼
    if end_idx < total_count:
        render_load_more_button()


def render_single_news_card(item: Dict[str, Any], selected_groups: List[str], item_number: int) -> None:
    """
    단일 뉴스 카드 렌더링
    
    Args:
        item: 뉴스 아이템
        selected_groups: 선택된 카테고리 리스트
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
        
        # 매칭된 카테고리
        matched_categories = []
        for group in selected_groups:
            if group in title or group in description:
                matched_categories.append(group)
        
        if matched_categories:
            categories_str = ", ".join(matched_categories)
            st.write(f"🏷️ **매칭 카테고리:** {categories_str}")
        else:
            # 매칭되지 않으면 전체 카테고리 표시
            categories_str = ", ".join(selected_groups)
            st.write(f"🏷️ **검색 카테고리:** {categories_str}")
        
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


def categorize_news(news_items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    뉴스를 카테고리별로 자동 분류
    
    Args:
        news_items: 뉴스 아이템 리스트
        
    Returns:
        Dict[str, List[Dict[str, Any]]]: 카테고리별로 분류된 뉴스
    """
    categories = {
        "회계법인": [],
        "공인회계사회": [],
        "세제·정책": [],
        "주요 기업": [],
        "산업 동향": [],
        "금융": [],
        "경제": [],
        "기타": []
    }
    
    # 키워드 기반 카테고리 분류
    for item in news_items:
        title = item.get('title', '').lower()
        description = item.get('description', '').lower()
        content = f"{title} {description}"
        
        # 회계법인 관련
        if any(keyword in content for keyword in ['pwc', '삼일', '삼정', 'kpmg', 'ey', 'deloitte']):
            categories["회계법인"].append(item)
        # 공인회계사회 관련
        elif any(keyword in content for keyword in ['공인회계사회', '회계감독', '회계기준', '감사']):
            categories["공인회계사회"].append(item)
        # 세제·정책 관련
        elif any(keyword in content for keyword in ['세제', '정책', '법인세', '금투세', '분리과세', '과세', '세금']):
            categories["세제·정책"].append(item)
        # 주요 기업 관련
        elif any(keyword in content for keyword in ['삼성', 'lg', 'sk', '현대', '네이버', '카카오', '포스코', '롯데', '한화']):
            categories["주요 기업"].append(item)
        # 산업 동향 관련
        elif any(keyword in content for keyword in ['ai', '반도체', '배터리', '자동차', '조선', '제약', '바이오', '문화', '컨텐츠']):
            categories["산업 동향"].append(item)
        # 금융 관련
        elif any(keyword in content for keyword in ['금융', '보험', '펀드', '투자', '자산', '유언', '신탁', '달러', '코인']):
            categories["금융"].append(item)
        # 경제 관련
        elif any(keyword in content for keyword in ['경제', '어음', '부도', '미국', '우선주의', '동맹']):
            categories["경제"].append(item)
        else:
            categories["기타"].append(item)
    
    # 빈 카테고리 제거
    return {k: v for k, v in categories.items() if v}


def render_categorized_results(news_items: List[Dict[str, Any]]) -> None:
    """
    카테고리별로 분류된 뉴스 결과 표시
    
    Args:
        news_items: 뉴스 아이템 리스트
    """
    if not news_items:
        return
    
    # 카테고리별 분류
    categorized_news = categorize_news(news_items)
    
    st.markdown("---")
    st.subheader("📊 카테고리별 뉴스 분류")
    
    # 전체 요약
    total_count = len(news_items)
    st.info(f"📰 총 {total_count:,}건의 뉴스를 {len(categorized_news)}개 카테고리로 분류했습니다.")
    
    # 카테고리별 표시
    for category, items in categorized_news.items():
        if not items:
            continue
            
        with st.expander(f"🔖 {category} ({len(items):,}건)", expanded=True):
            # 카테고리별 요약
            st.write(f"**{category}** 관련 뉴스 {len(items):,}건")
            
            # 뉴스 목록
            for i, item in enumerate(items[:10], 1):  # 최대 10개만 표시
                title = item.get('title', '').replace('<b>', '').replace('</b>', '')
                source = item.get('source_name', '')
                pubdate = item.get('pubDate', '')
                
                st.write(f"{i}. **{title}**")
                st.write(f"   📰 {source} | 📅 {pubdate}")
                
                if i < len(items) and i < 10:
                    st.write("---")
            
            # 더 많은 결과가 있는 경우
            if len(items) > 10:
                st.write(f"... 외 {len(items) - 10}건 더")


def render_enhanced_results_summary(news_items: List[Dict[str, Any]], 
                                  selected_groups: List[str], 
                                  keywords: List[str],
                                  start_time, 
                                  end_time,
                                  use_gpt: bool,
                                  threshold: float) -> None:
    """
    향상된 검색 결과 요약 표시 (카테고리별 분류 포함)
    
    Args:
        news_items: 뉴스 아이템 리스트
        selected_groups: 선택된 Group1 리스트
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
        groups_str = ", ".join(selected_groups)
        st.write(f"**검색 카테고리:** {groups_str}")
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
    
    # 카테고리별 분류 결과 표시
    render_categorized_results(news_items)


def render_dataframe_preview(news_items: List[Dict[str, Any]], selected_groups: List[str]) -> None:
    """
    결과 DataFrame 미리보기 및 CSV 다운로드
    
    Args:
        news_items: 뉴스 아이템 리스트
        selected_groups: 선택된 카테고리 리스트
    """
    if not news_items:
        return
    
    st.markdown("---")
    st.subheader("📋 데이터 미리보기")
    
    # DataFrame 생성
    df_data = []
    for item in news_items:
        # 매칭된 카테고리 찾기
        matched_categories = []
        for group in selected_groups:
            if group in item.get('title', '') or group in item.get('description', ''):
                matched_categories.append(group)
        
        # 카테고리가 매칭되지 않으면 전체 카테고리 표시
        if not matched_categories:
            matched_categories = selected_groups
        
        df_data.append({
            '카테고리': ', '.join(matched_categories),
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
    
    # CSV 다운로드 (한글 깨짐 방지)
    # UTF-8 BOM을 추가하여 Excel에서 한글이 제대로 표시되도록 함
    csv_data = df.to_csv(index=False, encoding='utf-8-sig')
    
    # 파일명에 현재 시간 추가
    timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
    filename = f"뉴스검색결과_{timestamp}.csv"
    
    # 두 가지 다운로드 옵션 제공
    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button(
            label="📥 CSV 다운로드 (Excel 호환)",
            data=csv_data,
            file_name=filename,
            mime="text/csv",
            use_container_width=True,
            help="UTF-8 BOM 인코딩으로 Excel에서 한글이 제대로 표시됩니다"
        )
    
    with col2:
        # Excel에서 더 안전하게 열 수 있는 방법 안내
        st.info("💡 **Excel에서 열기**: '데이터' → '텍스트/CSV' 선택 후 인코딩을 '65001: 유니코드(UTF-8)'로 설정")
    
    # 추가 안내
    st.info("💡 **CSV 다운로드 팁**: Excel에서 열 때 한글이 깨진다면 '데이터' → '텍스트/CSV'로 열어보세요.")
