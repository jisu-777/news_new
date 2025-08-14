"""
회계법인용 뉴스 수집/필터링 앱
"""
import streamlit as st
import os
from typing import List, Dict, Any
from constants import DEFAULT_ITEMS_PER_PAGE
from services.naver_api import NaverNewsAPI
from services.gpt_judger import GPTPrintJudger
from filters import apply_all_filters, add_source_info
from utils.dedupe import clean_news_data
from ui.sidebar import render_sidebar, show_search_summary
from ui.cards import (
    render_news_cards, 
    render_results_summary, 
    render_dataframe_preview
)


def main():
    """메인 앱 함수"""
    # 페이지 설정
    st.set_page_config(
        page_title="회계법인 뉴스 수집기",
        page_icon="📰",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 헤더
    st.title("📰 회계법인용 뉴스 수집/필터링 앱")
    st.markdown("**재무/세무/거버넌스/산업/기업 동향 중심의 뉴스 수집 도구**")
    
    # 사이드바 렌더링
    (
        selected_group1,
        selected_keywords,
        start_time,
        end_time,
        max_pages,
        keyword_limit,
        use_gpt,
        threshold
    ) = render_sidebar()
    
    # 검색 요약 표시
    show_search_summary(selected_group1, selected_keywords, start_time, end_time, use_gpt)
    
    # 검색 실행 버튼 체크
    if st.sidebar.button("🔍 검색 실행", type="primary", use_container_width=True):
        # 검색 실행
        with st.spinner("뉴스를 검색하고 있습니다..."):
            news_results = execute_news_search(
                selected_group1, 
                selected_keywords, 
                start_time, 
                end_time, 
                max_pages, 
                use_gpt, 
                threshold
            )
            
            # 세션 상태에 결과 저장
            st.session_state.news_results = news_results
            st.session_state.search_params = {
                'group1': selected_group1,
                'keywords': selected_keywords,
                'start_time': start_time,
                'end_time': end_time,
                'use_gpt': use_gpt,
                'threshold': threshold
            }
    
    # 이전 검색 결과가 있으면 표시
    if 'news_results' in st.session_state and st.session_state.news_results:
        display_search_results(
            st.session_state.news_results,
            st.session_state.search_params
        )


def execute_news_search(group1: str, keywords: List[str], start_time, end_time, 
                       max_pages: int, use_gpt: bool, threshold: float) -> List[Dict[str, Any]]:
    """
    뉴스 검색 실행
    
    Args:
        group1: 선택된 Group1
        keywords: 선택된 키워드
        start_time: 시작 시간
        end_time: 종료 시간
        max_pages: 키워드당 최대 페이지 수
        use_gpt: GPT 사용 여부
        threshold: 지면판별 임계값
        
    Returns:
        List[Dict[str, Any]]: 검색된 뉴스 아이템 리스트
    """
    try:
        # 1. 네이버 뉴스 API 검색
        st.info(f"🔍 '{group1}' 카테고리로 {len(keywords)}개 키워드 검색 중...")
        
        naver_api = NaverNewsAPI()
        raw_results = naver_api.search_by_group(group1, keywords, max_pages)
        
        if not raw_results:
            st.warning("검색 결과가 없습니다.")
            return []
        
        st.success(f"✅ {len(raw_results):,}건의 뉴스를 검색했습니다.")
        
        # 2. 필터링 적용
        st.info("🔍 필터링 적용 중...")
        
        # 허용된 언론사, 시간 윈도우, 비업무 키워드 필터링
        filtered_results = apply_all_filters(raw_results, start_time, end_time)
        
        if not filtered_results:
            st.warning("필터링 후 결과가 없습니다.")
            return []
        
        st.success(f"✅ 필터링 후 {len(filtered_results):,}건의 뉴스가 남았습니다.")
        
        # 3. 언론사 정보 추가
        filtered_results = add_source_info(filtered_results)
        
        # 4. 중복 제거 및 정렬
        st.info("🔄 중복 제거 및 정렬 중...")
        cleaned_results = clean_news_data(filtered_results)
        
        st.success(f"✅ 최종 {len(cleaned_results):,}건의 뉴스를 정리했습니다.")
        
        # 5. GPT 지면판별 (옵션)
        if use_gpt and cleaned_results:
            st.info("🤖 GPT로 지면뉴스 판별 중...")
            
            try:
                gpt_judger = GPTPrintJudger()
                
                # 배치 처리로 지면판별
                judged_results = gpt_judger.judge_multiple_news(
                    cleaned_results, 
                    threshold=threshold,
                    batch_size=5
                )
                
                if judged_results:
                    st.success(f"✅ GPT 필터링 후 {len(judged_results):,}건의 뉴스가 남았습니다.")
                    return judged_results
                else:
                    st.warning("GPT 필터링 후 결과가 없습니다.")
                    return []
                    
            except Exception as e:
                st.error(f"GPT 지면판별 중 오류가 발생했습니다: {e}")
                st.info("GPT 없이 원본 결과를 반환합니다.")
                return cleaned_results
        
        return cleaned_results
        
    except Exception as e:
        st.error(f"뉴스 검색 중 오류가 발생했습니다: {e}")
        return []


def display_search_results(news_results: List[Dict[str, Any]], search_params: Dict[str, Any]):
    """
    검색 결과 표시
    
    Args:
        news_results: 뉴스 결과 리스트
        search_params: 검색 파라미터
    """
    if not news_results:
        st.warning("표시할 검색 결과가 없습니다.")
        return
    
    # 결과 요약
    render_results_summary(
        news_results,
        search_params['group1'],
        search_params['keywords'],
        search_params['start_time'],
        search_params['end_time'],
        search_params['use_gpt'],
        search_params['threshold']
    )
    
    # 뉴스 카드 표시
    render_news_cards(
        news_results,
        search_params['keywords'],
        DEFAULT_ITEMS_PER_PAGE
    )
    
    # DataFrame 미리보기 및 CSV 다운로드
    render_dataframe_preview(news_results)


def check_environment():
    """환경변수 체크"""
    required_vars = ['NAVER_CLIENT_ID', 'NAVER_CLIENT_SECRET']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        st.error(f"⚠️ 다음 환경변수가 설정되지 않았습니다: {', '.join(missing_vars)}")
        st.info("📝 .env 파일을 생성하고 필요한 환경변수를 설정해주세요.")
        return False
    
    return True


if __name__ == "__main__":
    # 환경변수 체크
    if check_environment():
        main()
    else:
        st.stop()
