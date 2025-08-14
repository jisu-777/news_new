#!/usr/bin/env python3
"""
뉴스 선별 및 중복 제거 기능 테스트 예시 (지면뉴스 우선)
"""

import os
from services.gpt_judger import GPTNewsFilter

def test_integrated_news_filter():
    """통합 뉴스 선별 및 중복 제거 기능 테스트"""
    
    # 환경변수 확인
    if not os.getenv('OPENAI_API_KEY'):
        print("OPENAI_API_KEY 환경변수를 설정해주세요.")
        return
    
    # 뉴스 선별기 초기화
    filter = GPTNewsFilter()
    
    # 테스트용 뉴스 데이터 (중복 기사 포함)
    test_news = [
        {
            'title': '삼성전자, AI 반도체 시장 진출 선언',
            'description': '삼성전자가 AI 반도체 시장에 본격 진출한다고 발표했다. HBM 메모리와 AI 연산 칩 개발에 집중할 계획이다.',
            'domain': 'economy.hankyung.com',
            'source_name': '한국경제'
        },
        {
            'title': '삼성전자, AI 반도체 시장 진출 선언',  # 중복 기사
            'description': '삼성전자가 AI 반도체 시장 진출을 공식 발표했다. HBM 메모리와 AI 칩 개발에 집중한다.',
            'domain': 'chosun.com',
            'source_name': '조선일보'
        },
        {
            'title': 'BTS 지민, 새 앨범 발매 예고',
            'description': 'BTS 지민이 솔로 앨범 발매를 예고했다. 팬들의 기대감이 높아지고 있다.',
            'domain': 'entertain.naver.com',
            'source_name': '네이버 엔터테인먼트'
        },
        {
            'title': '카드사, 포인트 정책 변경 발표',
            'description': '주요 카드사들이 포인트 적립 정책을 변경한다고 발표했다. 소비자들의 불만이 제기되고 있다.',
            'domain': 'finance.naver.com',
            'source_name': '네이버 금융'
        },
        {
            'title': '글로벌 금융위기 우려 확산',
            'description': '미국 금리 인상과 중국 부동산 위기로 글로벌 금융시장의 불안감이 확산되고 있다. 한국 경제에도 영향이 예상된다.',
            'domain': 'economy.chosun.com',
            'source_name': '조선일보'
        },
        {
            'title': '글로벌 금융위기 우려 확산',  # 중복 기사
            'description': '미국 금리 인상과 중국 부동산 위기로 글로벌 금융시장 불안감 확산. 한국 경제 영향 예상.',
            'domain': 'hankyung.com',
            'source_name': '한국경제'
        }
    ]
    
    print("=== 통합 뉴스 선별 및 중복 제거 테스트 시작 ===\n")
    
    # 단일 뉴스 테스트
    print("1. 단일 뉴스 통합 판별 테스트:")
    for i, news in enumerate(test_news[:2], 1):
        print(f"\n--- 뉴스 {i} ---")
        print(f"제목: {news['title']}")
        print(f"요약: {news['description']}")
        print(f"언론사: {news['source_name']}")
        
        result = filter.judge_single_news(
            news['title'], 
            news['description'], 
            news['domain'], 
            news['source_name']
        )
        
        if result:
            print(f"지면가능성: {result['print_score']:.2f}")
            print(f"실용성: {result['utility_score']:.2f}")
            print(f"종합점수: {result['total_score']:.2f}")
            print(f"포함 여부: {'예' if result['include'] else '아니오'}")
            print(f"이유: {result['reason']}")
        else:
            print("판별 실패")
    
    # 통합 선별 및 중복 제거 테스트
    print(f"\n\n2. 통합 선별 및 중복 제거 테스트 (임계값: 0.7):")
    filtered_news = filter.filter_and_dedupe_news(test_news, threshold=0.7)
    
    print(f"\n총 {len(test_news)}개 중 {len(filtered_news)}개가 선별 기준을 통과하고 중복이 제거되었습니다.")
    
    for i, news in enumerate(filtered_news, 1):
        print(f"\n--- 선별된 뉴스 {i} ---")
        print(f"제목: {news['title']}")
        print(f"언론사: {news['source_name']}")
        print(f"지면가능성: {news['judgment_result']['print_score']:.2f}")
        print(f"실용성: {news['judgment_result']['utility_score']:.2f}")
        print(f"종합점수: {news['judgment_result']['total_score']:.2f}")
        print(f"이유: {news['judgment_result']['reason']}")
    
    # 중복 제거 결과 분석
    print(f"\n\n3. 중복 제거 결과 분석:")
    original_titles = [news['title'] for news in test_news]
    filtered_titles = [news['title'] for news in filtered_news]
    
    print(f"원본 뉴스 수: {len(original_titles)}")
    print(f"선별 후 뉴스 수: {len(filtered_titles)}")
    print(f"중복 제거된 뉴스 수: {len(original_titles) - len(filtered_titles)}")
    
    # 중복이 제거된 기사들 확인
    duplicate_titles = []
    for title in original_titles:
        if original_titles.count(title) > 1 and title not in duplicate_titles:
            duplicate_titles.append(title)
    
    if duplicate_titles:
        print(f"\n중복 제거된 기사 제목:")
        for title in duplicate_titles:
            print(f"- {title}")
            
            # 각 중복 기사들의 점수 비교
            duplicates = [news for news in test_news if news['title'] == title]
            print(f"  중복 기사 수: {len(duplicates)}")
            
            for dup in duplicates:
                if 'judgment_result' in dup:
                    print(f"  - {dup['source_name']}: 지면={dup['judgment_result']['print_score']:.2f}, 종합={dup['judgment_result']['total_score']:.2f}")

def test_title_normalization():
    """제목 정규화 테스트"""
    print("\n\n4. 제목 정규화 테스트:")
    
    test_titles = [
        "삼성전자, AI 반도체 시장 진출 선언",
        "삼성전자 AI 반도체 시장 진출 선언",  # 쉼표 제거
        "삼성전자  AI  반도체  시장  진출  선언",  # 공백 증가
        "삼성전자! AI 반도체 시장 진출 선언!",  # 특수문자 추가
        "삼성전자, AI 반도체 시장 진출 선언",  # 원본과 동일
    ]
    
    filter = GPTNewsFilter()
    
    for i, title in enumerate(test_titles):
        normalized = filter._normalize_title(title)
        print(f"원본: '{title}'")
        print(f"정규화: '{normalized}'")
        print(f"---")

if __name__ == "__main__":
    test_integrated_news_filter()
    test_title_normalization()
