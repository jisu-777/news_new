"""
네이버 뉴스 API 호출 및 데이터 처리 서비스
"""
import os
import time
import requests
from typing import List, Dict, Any, Optional
from constants import NAVER_NEWS_API_URL, NAVER_API_DELAY


class NaverNewsAPI:
    """네이버 뉴스 API 클라이언트"""
    
    def __init__(self):
        """초기화"""
        self.client_id = os.getenv('NAVER_CLIENT_ID')
        self.client_secret = os.getenv('NAVER_CLIENT_SECRET')
        
        if not self.client_id or not self.client_secret:
            raise ValueError("NAVER_CLIENT_ID와 NAVER_CLIENT_SECRET 환경변수가 필요합니다.")
        
        self.headers = {
            'X-Naver-Client-Id': self.client_id,
            'X-Naver-Client-Secret': self.client_secret
        }
    
    def search_news(self, query: str, start: int = 1, display: int = 100) -> Optional[Dict[str, Any]]:
        """
        네이버 뉴스 검색 API 호출
        
        Args:
            query: 검색 쿼리
            start: 시작 위치 (1부터 시작)
            display: 한 번에 가져올 결과 수 (최대 100)
            
        Returns:
            Optional[Dict[str, Any]]: API 응답 결과 또는 None
        """
        try:
            params = {
                'query': query,
                'display': min(display, 100),  # 최대 100개
                'start': start,
                'sort': 'sim'  # 정확도 순
            }
            
            response = requests.get(
                NAVER_NEWS_API_URL,
                headers=self.headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"API 호출 실패: {response.status_code} - {response.text}")
                return None
                
        except requests.RequestException as e:
            print(f"API 요청 오류: {e}")
            return None
        except Exception as e:
            print(f"예상치 못한 오류: {e}")
            return None
    
    def search_news_with_pagination(self, query: str, max_pages: int = 3) -> List[Dict[str, Any]]:
        """
        페이지네이션을 사용하여 여러 페이지의 뉴스 검색
        
        Args:
            query: 검색 쿼리
            max_pages: 최대 검색할 페이지 수
            
        Returns:
            List[Dict[str, Any]]: 모든 페이지의 뉴스 아이템 리스트
        """
        all_items = []
        
        for page in range(max_pages):
            start = page * 100 + 1
            
            # API 호출
            result = self.search_news(query, start=start, display=100)
            
            if result and 'items' in result:
                items = result['items']
                all_items.extend(items)
                
                # 마지막 페이지 체크
                if len(items) < 100:
                    break
            else:
                break
            
            # Rate limit 방지를 위한 지연
            if page < max_pages - 1:
                time.sleep(NAVER_API_DELAY)
        
        return all_items
    
    def search_multiple_keywords(self, keywords: List[str], max_pages_per_keyword: int = 2) -> List[Dict[str, Any]]:
        """
        여러 키워드로 뉴스 검색하고 합집합 생성
        
        Args:
            keywords: 검색할 키워드 리스트
            max_pages_per_keyword: 키워드당 최대 검색할 페이지 수
            
        Returns:
            List[Dict[str, Any]]: 모든 키워드의 검색 결과 합집합
        """
        all_results = []
        
        for i, keyword in enumerate(keywords):
            print(f"키워드 '{keyword}' 검색 중... ({i+1}/{len(keywords)})")
            
            # 키워드별 검색
            keyword_results = self.search_news_with_pagination(keyword, max_pages_per_keyword)
            all_results.extend(keyword_results)
            
            # 마지막 키워드가 아니면 지연
            if i < len(keywords) - 1:
                time.sleep(NAVER_API_DELAY)
        
        return all_results
    
    def search_by_group(self, selected_groups: List[str], keywords: List[str], max_pages_per_keyword: int = 2) -> List[Dict[str, Any]]:
        """
        선택된 그룹들 + 키워드로 검색
        
        Args:
            selected_groups: 선택된 그룹명 리스트 (예: ["주요기업", "산업동향"])
            keywords: 검색할 키워드 리스트
            max_pages_per_keyword: 키워드당 최대 검색할 페이지 수
            
        Returns:
            List[Dict[str, Any]]: 검색 결과 리스트
        """
        all_results = []
        
        # 각 그룹별로 검색
        for group in selected_groups:
            print(f"그룹 '{group}' 검색 중...")
            
            # 그룹명 + 키워드로 검색 쿼리 생성
            search_keywords = [f'"{group}" "{keyword}"' for keyword in keywords]
            
            # 해당 그룹의 검색 결과
            group_results = self.search_multiple_keywords(search_keywords, max_pages_per_keyword)
            all_results.extend(group_results)
            
            # 그룹 간 지연
            time.sleep(NAVER_API_DELAY)
        
        return all_results
    
    def get_total_count(self, query: str) -> int:
        """
        검색 결과 총 건수 조회
        
        Args:
            query: 검색 쿼리
            
        Returns:
            int: 총 검색 결과 건수
        """
        result = self.search_news(query, start=1, display=1)
        
        if result and 'total' in result:
            return result['total']
        
        return 0


def create_search_query(group_name: str, keyword: str) -> str:
    """
    검색 쿼리 생성
    
    Args:
        group_name: 그룹명
        keyword: 키워드
        
    Returns:
        str: 검색 쿼리
    """
    return f'"{group_name}" "{keyword}"'


def estimate_total_results(group_name: str, keywords: List[str]) -> int:
    """
    예상 총 검색 결과 건수 추정
    
    Args:
        group_name: 그룹명
        keywords: 키워드 리스트
        
    Returns:
        int: 예상 총 건수
    """
    try:
        api = NaverNewsAPI()
        total = 0
        
        for keyword in keywords[:3]:  # 처음 3개 키워드만 체크
            query = create_search_query(group_name, keyword)
            count = api.get_total_count(query)
            total += count
            time.sleep(NAVER_API_DELAY)
        
        # 평균 * 키워드 수로 추정
        if keywords:
            avg_count = total / min(len(keywords), 3)
            estimated_total = int(avg_count * len(keywords))
            return estimated_total
        
        return 0
        
    except Exception as e:
        print(f"총 건수 추정 실패: {e}")
        return 0
