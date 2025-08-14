"""
GPT를 사용한 지면뉴스 판별 서비스
"""
import os
import time
from typing import List, Dict, Any, Optional
from openai import OpenAI
from constants import GPT_MODEL, DEFAULT_PRINT_THRESHOLD


class GPTPrintJudger:
    """GPT를 사용한 지면뉴스 판별기"""
    
    def __init__(self):
        """초기화"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY 환경변수가 필요합니다.")
        
        self.client = OpenAI(api_key=api_key)
        self.model = GPT_MODEL
    
    def create_judgment_prompt(self, title: str, description: str, domain: str, source_name: str) -> str:
        """
        지면판별을 위한 프롬프트 생성
        
        Args:
            title: 뉴스 제목
            description: 뉴스 요약
            domain: 도메인
            source_name: 언론사명
            
        Returns:
            str: GPT 프롬프트
        """
        prompt = f"""
다음 뉴스가 지면(인쇄판) 기사일 가능성을 0.0~1.0 사이의 숫자로 평가해주세요.

뉴스 정보:
- 제목: {title}
- 요약: {description}
- 도메인: {domain}
- 언론사: {source_name}

지면 기사의 특징:
- 신문 지면에 실리는 기사
- 온라인 전용이 아닌 인쇄물 기사
- 종이 신문에 게재되는 기사
- 온라인과 지면에 동시 게재되는 기사도 포함

평가 기준:
- 0.0: 온라인 전용 기사일 가능성 높음
- 0.5: 지면과 온라인 동시 게재 가능성
- 1.0: 지면 전용 기사일 가능성 높음

답변은 반드시 0.0~1.0 사이의 숫자만 출력하세요.
"""
        return prompt.strip()
    
    def judge_single_news(self, title: str, description: str, domain: str, source_name: str) -> Optional[float]:
        """
        단일 뉴스의 지면 가능성 판별
        
        Args:
            title: 뉴스 제목
            description: 뉴스 요약
            domain: 도메인
            source_name: 언론사명
            
        Returns:
            Optional[float]: 지면 가능성 점수 (0.0~1.0) 또는 None
        """
        try:
            prompt = self.create_judgment_prompt(title, description, domain, source_name)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "당신은 뉴스 기사의 지면 게재 가능성을 판단하는 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=10
            )
            
            # 응답에서 숫자 추출
            content = response.choices[0].message.content.strip()
            
            # 숫자만 추출 (0.0~1.0 형태)
            try:
                score = float(content)
                if 0.0 <= score <= 1.0:
                    return score
                else:
                    print(f"점수 범위 오류: {score}")
                    return None
            except ValueError:
                print(f"점수 파싱 실패: {content}")
                return None
                
        except Exception as e:
            print(f"GPT 판별 오류: {e}")
            return None
    
    def judge_multiple_news(self, news_items: List[Dict[str, Any]], 
                           threshold: float = DEFAULT_PRINT_THRESHOLD,
                           batch_size: int = 5) -> List[Dict[str, Any]]:
        """
        여러 뉴스의 지면 가능성 일괄 판별
        
        Args:
            news_items: 뉴스 아이템 리스트
            threshold: 지면 가능성 임계값
            batch_size: 배치 크기
            
        Returns:
            List[Dict[str, Any]]: 지면 가능성이 threshold 이상인 뉴스만 필터링된 리스트
        """
        if not news_items:
            return []
        
        judged_items = []
        
        # 배치 단위로 처리
        for i in range(0, len(news_items), batch_size):
            batch = news_items[i:i + batch_size]
            
            for item in batch:
                title = item.get('title', '')
                description = item.get('description', '')
                domain = item.get('domain', '')
                source_name = item.get('source_name', '')
                
                # 지면 가능성 판별
                print_score = self.judge_single_news(title, description, domain, source_name)
                
                if print_score is not None:
                    item['print_score'] = print_score
                    
                    # 임계값 이상인 경우만 포함
                    if print_score >= threshold:
                        judged_items.append(item)
                
                # Rate limit 방지를 위한 지연
                time.sleep(0.1)
        
        return judged_items
    
    def judge_news_sequential(self, news_items: List[Dict[str, Any]], 
                             threshold: float = DEFAULT_PRINT_THRESHOLD) -> List[Dict[str, Any]]:
        """
        순차적으로 뉴스 지면 가능성 판별 (비용 절감용)
        
        Args:
            news_items: 뉴스 아이템 리스트
            threshold: 지면 가능성 임계값
            
        Returns:
            List[Dict[str, Any]]: 지면 가능성이 threshold 이상인 뉴스만 필터링된 리스트
        """
        if not news_items:
            return []
        
        judged_items = []
        
        for i, item in enumerate(news_items):
            title = item.get('title', '')
            description = item.get('description', '')
            domain = item.get('domain', '')
            source_name = item.get('source_name', '')
            
            # 지면 가능성 판별
            print_score = self.judge_single_news(title, description, domain, source_name)
            
            if print_score is not None:
                item['print_score'] = print_score
                
                # 임계값 이상인 경우만 포함
                if print_score >= threshold:
                    judged_items.append(item)
            
            # 진행률 표시
            if (i + 1) % 10 == 0:
                print(f"지면판별 진행률: {i + 1}/{len(news_items)}")
            
            # Rate limit 방지를 위한 지연
            time.sleep(0.1)
        
        return judged_items


class GPTNewsFilter:
    """GPT를 사용한 뉴스 선별 판별기 - 실용성, 객관성, 지면뉴스 우선순위 통합"""
    
    def __init__(self):
        """초기화"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY 환경변수가 필요합니다.")
        
        self.client = OpenAI(api_key=api_key)
        self.model = GPT_MODEL
    
    def create_integrated_prompt(self, title: str, description: str, domain: str, source_name: str) -> str:
        """
        지면뉴스 판별과 뉴스 선별을 통합한 프롬프트 생성
        
        Args:
            title: 뉴스 제목
            description: 뉴스 요약
            domain: 도메인
            source_name: 언론사명
            
        Returns:
            str: GPT 프롬프트
        """
        prompt = f"""
다음 뉴스에 대해 지면뉴스 가능성과 실용성을 종합적으로 판단해주세요.

뉴스 정보:
- 제목: {title}
- 요약: {description}
- 도메인: {domain}
- 언론사: {source_name}

판단 기준:

1. 지면뉴스 가능성 (0.0~1.0):
- 0.0: 온라인 전용 기사
- 0.5: 지면과 온라인 동시 게재 가능성
- 1.0: 지면 전용 기사 가능성 높음

2. 실용성 및 객관성 (0.0~1.0):
- 포함할 기사: 기업 경영 전략, 재무관리, 위기관리 등 실질적 도움 제공
- 제외할 기사: 개인 관련, 홍보성, 사회적 이슈, 단순 사건사고 등

3. 종합 점수 (0.0~1.0):
- 지면뉴스 + 실용성 + 객관성을 종합한 최종 점수

판단 결과를 다음 형식으로 출력하세요:
지면가능성: [0.0~1.0]
실용성: [0.0~1.0]
종합점수: [0.0~1.0]
포함여부: [예/아니오]
이유: [판단 이유 간단 설명]
"""
        return prompt.strip()
    
    def judge_single_news(self, title: str, description: str, domain: str, source_name: str) -> Optional[Dict[str, Any]]:
        """
        단일 뉴스의 통합 판별 (지면뉴스 + 선별)
        
        Args:
            title: 뉴스 제목
            description: 뉴스 요약
            domain: 도메인
            source_name: 언론사명
            
        Returns:
            Optional[Dict[str, Any]]: 통합 판별 결과 또는 None
        """
        try:
            prompt = self.create_integrated_prompt(title, description, domain, source_name)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "당신은 뉴스의 지면 가능성과 실용성을 종합적으로 판단하는 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=200
            )
            
            content = response.choices[0].message.content.strip()
            
            # 응답 파싱
            result = self._parse_integrated_response(content)
            return result
                
        except Exception as e:
            print(f"GPT 통합 판별 오류: {e}")
            return None
    
    def _parse_integrated_response(self, content: str) -> Dict[str, Any]:
        """
        GPT 응답을 파싱하여 구조화된 결과로 변환
        
        Args:
            content: GPT 응답 내용
            
        Returns:
            Dict[str, Any]: 파싱된 결과
        """
        try:
            lines = content.split('\n')
            result = {
                'print_score': 0.0,      # 지면뉴스 가능성
                'utility_score': 0.0,    # 실용성 점수
                'total_score': 0.0,      # 종합 점수
                'include': False,        # 포함 여부
                'reason': '',            # 판단 이유
                'raw_response': content  # 원본 응답
            }
            
            for line in lines:
                line = line.strip()
                if line.startswith('지면가능성:'):
                    score_text = line.replace('지면가능성:', '').strip()
                    try:
                        score = float(score_text)
                        if 0.0 <= score <= 1.0:
                            result['print_score'] = score
                    except ValueError:
                        pass
                elif line.startswith('실용성:'):
                    score_text = line.replace('실용성:', '').strip()
                    try:
                        score = float(score_text)
                        if 0.0 <= score <= 1.0:
                            result['utility_score'] = score
                    except ValueError:
                        pass
                elif line.startswith('종합점수:'):
                    score_text = line.replace('종합점수:', '').strip()
                    try:
                        score = float(score_text)
                        if 0.0 <= score <= 1.0:
                            result['total_score'] = score
                    except ValueError:
                        pass
                elif line.startswith('포함여부:'):
                    include_text = line.replace('포함여부:', '').strip()
                    result['include'] = '예' in include_text or '포함' in include_text
                elif line.startswith('이유:'):
                    reason = line.replace('이유:', '').strip()
                    result['reason'] = reason
            
            return result
            
        except Exception as e:
            print(f"응답 파싱 오류: {e}")
            return {
                'print_score': 0.0,
                'utility_score': 0.0,
                'total_score': 0.0,
                'include': False,
                'reason': '파싱 실패',
                'raw_response': content
            }
    
    def filter_and_dedupe_news(self, news_items: List[Dict[str, Any]], 
                              threshold: float = 0.7,
                              batch_size: int = 5) -> List[Dict[str, Any]]:
        """
        뉴스 선별 및 중복 제거 (지면뉴스 우선)
        
        Args:
            news_items: 뉴스 아이템 리스트
            threshold: 선별 점수 임계값
            batch_size: 배치 크기
            
        Returns:
            List[Dict[str, Any]]: 선별 및 중복 제거된 뉴스 리스트
        """
        if not news_items:
            return []
        
        # 1단계: GPT 판별
        judged_items = []
        
        # 배치 단위로 처리
        for i in range(0, len(news_items), batch_size):
            batch = news_items[i:i + batch_size]
            
            for item in batch:
                title = item.get('title', '')
                description = item.get('description', '')
                domain = item.get('domain', '')
                source_name = item.get('source_name', '')
                
                # 통합 판별
                judgment_result = self.judge_single_news(title, description, domain, source_name)
                
                if judgment_result:
                    # 원본 아이템에 판별 결과 추가
                    item['judgment_result'] = judgment_result
                    
                    # 임계값 이상이고 포함 대상인 경우만 추가
                    if judgment_result['total_score'] >= threshold and judgment_result['include']:
                        judged_items.append(item)
                
                # Rate limit 방지를 위한 지연
                time.sleep(0.1)
        
        # 2단계: 중복 제거 (지면뉴스 우선)
        deduped_items = self._dedupe_with_print_priority(judged_items)
        
        return deduped_items
    
    def _dedupe_with_print_priority(self, news_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        지면뉴스 우선으로 중복 제거
        
        Args:
            news_items: 판별된 뉴스 아이템 리스트
            
        Returns:
            List[Dict[str, Any]]: 중복 제거된 뉴스 리스트
        """
        if not news_items:
            return []
        
        # 제목 기준으로 그룹화
        title_groups = {}
        
        for item in news_items:
            title = item.get('title', '').strip()
            if not title:
                continue
            
            # 제목 정규화 (특수문자, 공백 등 제거)
            normalized_title = self._normalize_title(title)
            
            if normalized_title not in title_groups:
                title_groups[normalized_title] = []
            
            title_groups[normalized_title].append(item)
        
        # 각 그룹에서 최적의 뉴스 선택 (지면뉴스 우선)
        deduped_items = []
        
        for normalized_title, group in title_groups.items():
            if len(group) == 1:
                # 중복이 없는 경우
                deduped_items.append(group[0])
            else:
                # 중복이 있는 경우 지면뉴스 우선 선택
                best_item = self._select_best_from_group(group)
                deduped_items.append(best_item)
        
        return deduped_items
    
    def _normalize_title(self, title: str) -> str:
        """
        제목 정규화 (중복 판별용)
        
        Args:
            title: 원본 제목
            
        Returns:
            str: 정규화된 제목
        """
        import re
        
        # 특수문자 제거, 공백 정규화, 소문자 변환
        normalized = re.sub(r'[^\w\s]', '', title)
        normalized = re.sub(r'\s+', ' ', normalized)
        normalized = normalized.strip().lower()
        
        return normalized
    
    def _select_best_from_group(self, group: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        그룹에서 최적의 뉴스 선택 (지면뉴스 우선)
        
        Args:
            group: 동일 제목의 뉴스 그룹
            
        Returns:
            Dict[str, Any]: 최적의 뉴스 아이템
        """
        if not group:
            return {}
        
        # 1순위: 지면뉴스 점수 (높은 순)
        # 2순위: 종합 점수 (높은 순)
        # 3순위: 언론사 신뢰도 (상위 언론사 우선)
        
        # 언론사 신뢰도 점수 (상위 언론사일수록 높은 점수)
        source_priority = {
            '조선일보': 10, '중앙일보': 9, '동아일보': 8, '조선비즈': 7,
            '매거진한경': 6, '한국경제': 5, '매일경제': 4, '연합뉴스': 3,
            '파이낸셜뉴스': 2, '머니투데이': 1
        }
        
        best_item = group[0]
        best_score = -1
        
        for item in group:
            judgment = item.get('judgment_result', {})
            print_score = judgment.get('print_score', 0.0)
            total_score = judgment.get('total_score', 0.0)
            source_name = item.get('source_name', '')
            
            # 종합 점수 계산 (지면뉴스 60%, 실용성 30%, 언론사 10%)
            source_score = source_priority.get(source_name, 0) / 10.0
            combined_score = (print_score * 0.6) + (total_score * 0.3) + (source_score * 0.1)
            
            if combined_score > best_score:
                best_score = combined_score
                best_item = item
        
        return best_item
    
    def filter_multiple_news(self, news_items: List[Dict[str, Any]], 
                            threshold: float = 0.7,
                            batch_size: int = 5) -> List[Dict[str, Any]]:
        """
        여러 뉴스의 선별 판별 일괄 처리 (기존 호환성 유지)
        
        Args:
            news_items: 뉴스 아이템 리스트
            threshold: 선별 점수 임계값
            batch_size: 배치 크기
            
        Returns:
            List[Dict[str, Any]]: 선별 기준을 통과한 뉴스만 필터링된 리스트
        """
        return self.filter_and_dedupe_news(news_items, threshold, batch_size)
    
    def filter_news_sequential(self, news_items: List[Dict[str, Any]], 
                              threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        순차적으로 뉴스 선별 판별 (비용 절감용)
        
        Args:
            news_items: 뉴스 아이템 리스트
            threshold: 선별 점수 임계값
            
        Returns:
            List[Dict[str, Any]]: 선별 기준을 통과한 뉴스만 필터링된 리스트
        """
        if not news_items:
            return []
        
        judged_items = []
        
        for i, item in enumerate(news_items):
            title = item.get('title', '')
            description = item.get('description', '')
            domain = item.get('domain', '')
            source_name = item.get('source_name', '')
            
            # 통합 판별
            judgment_result = self.judge_single_news(title, description, domain, source_name)
            
            if judgment_result:
                # 원본 아이템에 판별 결과 추가
                item['judgment_result'] = judgment_result
                
                # 임계값 이상이고 포함 대상인 경우만 추가
                if judgment_result['total_score'] >= threshold and judgment_result['include']:
                    judged_items.append(item)
            
            # 진행률 표시
            if (i + 1) % 10 == 0:
                print(f"뉴스 선별 진행률: {i + 1}/{len(news_items)}")
            
            # Rate limit 방지를 위한 지연
            time.sleep(0.1)
        
        # 중복 제거
        deduped_items = self._dedupe_with_print_priority(judged_items)
        
        return deduped_items


def estimate_gpt_cost(news_count: int, model: str = GPT_MODEL) -> float:
    """
    GPT 사용 비용 추정
    
    Args:
        news_count: 뉴스 개수
        model: 사용할 모델
        
    Returns:
        float: 예상 비용 (USD)
    """
    # GPT-3.5-turbo 기준 (1000 tokens당 $0.001)
    cost_per_1k_tokens = 0.001
    
    # 뉴스당 평균 토큰 수 (제목 + 요약 + 프롬프트)
    avg_tokens_per_news = 200
    
    # 총 예상 토큰 수
    total_tokens = news_count * avg_tokens_per_news
    
    # 비용 계산
    estimated_cost = (total_tokens / 1000) * cost_per_1k_tokens
    
    return round(estimated_cost, 4)
