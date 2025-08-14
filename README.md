# 📰 회계법인용 뉴스 수집/필터링 앱

재무/세무/거버넌스/산업/기업 동향 중심의 뉴스를 수집하고 필터링하는 Streamlit 기반 웹 애플리케이션입니다.

## 🎯 주요 기능

- **네이버 뉴스 API 연동**: 실시간 뉴스 검색 및 수집
- **스마트 필터링**: 허용된 언론사, 날짜 윈도우, 비업무 키워드 자동 제외
- **GPT 지면판별**: AI를 활용한 지면뉴스 가능성 점수화 (옵션)
- **AI 뉴스 선별**: 실용성, 객관성, 지면뉴스 우선순위를 통합한 자동 뉴스 필터링 및 중복 제거
- **직관적인 UI**: 카테고리별 키워드 선택 및 결과 카드 뷰
- **데이터 내보내기**: CSV 다운로드 및 DataFrame 미리보기

## 🚀 설치 및 실행

### 1. 저장소 클론
```bash
git clone <repository-url>
cd news_new
```

### 2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 환경변수 설정
`.env` 파일을 생성하고 필요한 API 키를 설정하세요:

```bash
cp env.example .env
```

`.env` 파일 편집:
```env
NAVER_CLIENT_ID=your_naver_client_id_here
NAVER_CLIENT_SECRET=your_naver_client_secret_here
OPENAI_API_KEY=your_openai_api_key_here  # GPT 기능 사용시
```

### 5. 앱 실행
```bash
streamlit run app.py
```

## 🔑 API 키 발급 방법

### 네이버 뉴스 API
1. [네이버 개발자 센터](https://developers.naver.com/apps/#/list) 접속
2. 애플리케이션 등록
3. "뉴스 검색" API 선택
4. Client ID와 Client Secret 발급

### OpenAI API (GPT 기능 사용시)
1. [OpenAI Platform](https://platform.openai.com/api-keys) 접속
2. API 키 생성
3. 발급된 키를 환경변수에 설정

## 📖 사용법

### 1. 카테고리 선택
- **Group1**: 뉴스 카테고리 선택 (주요기업, 산업동향, 경제 등)
- **Group2**: 해당 카테고리의 세부 키워드 자동 로드

### 2. 검색 설정
- **키워드 개수 제한**: 사용할 키워드 수 조절
- **검색 기간**: 기본값은 전일 10시~당일 10시 (월요일은 금요일 10시~)
- **페이지 수**: 키워드당 검색할 최대 페이지 수

### 3. GPT 지면판별 (옵션)
- **활성화**: 지면뉴스 가능성을 AI로 판별
- **임계값**: 0.0~1.0 사이의 점수 설정 (기본값: 0.7)
- **비용**: GPT-3.5-turbo 기준 뉴스당 약 $0.0002

### 4. AI 뉴스 선별 및 중복 제거 (옵션)
- **활성화**: 실용성, 객관성, 지면뉴스 우선순위를 통합한 자동 뉴스 필터링
- **선별 기준**: 기업 경영 전략, 재무관리, 위기관리 등 실질적 도움 제공
- **제외 기준**: 개인 관련, 홍보성, 사회적 이슈, 단순 사건사고 등
- **중복 제거**: 동일 기사 중 지면뉴스 우선 선택 (지면 60%, 실용성 30%, 언론사 10%)
- **점수**: 0.0~1.0 사이의 종합 점수 (기본 임계값: 0.7)

### 5. 결과 확인
- **카드 뷰**: 제목, 요약, 발행시각, 언론사, 매칭 키워드 표시
- **페이지네이션**: 결과가 많을 때 페이지별 탐색
- **CSV 다운로드**: 검색 결과를 엑셀에서 확인

## 🏗️ 프로젝트 구조

```
news_new/
├── app.py                 # 메인 앱 진입점
├── constants.py           # 상수 및 설정 정의
├── filters.py             # 필터링 로직
├── services/
│   ├── naver_api.py      # 네이버 뉴스 API 서비스
│   └── gpt_judger.py     # GPT 통합 판별 및 뉴스 선별/중복제거 서비스
├── ui/
│   ├── sidebar.py         # 사이드바 컴포넌트
│   └── cards.py           # 뉴스 카드 렌더러
├── utils/
│   ├── time_window.py     # 날짜 윈도우 계산
│   └── dedupe.py          # 중복 제거 유틸리티
├── requirements.txt       # Python 의존성
├── env.example           # 환경변수 예시
└── README.md             # 이 파일
```

## ⚙️ 설정 옵션

### 허용된 언론사
- 조선일보, 중앙일보, 동아일보, 조선비즈
- 매거진한경, 한국경제, 매일경제, 연합뉴스
- 파이낸셜뉴스, 데일리팜, IT조선, 머니투데이
- 비즈니스포스트, 이데일리, 아시아경제
- 뉴스핌, 뉴시스, 헤럴드경제, 더벨

### 제외되는 키워드
- 스포츠: 야구, 축구, 농구, 배구, 골프, 테니스, e스포츠
- 연예: 연예인, 아이돌, 배우, 가수, 예능, 방송가, 드라마, 영화

## 🔧 커스터마이징

### 새로운 카테고리 추가
`constants.py`의 `GROUP_DEFS`와 `KEYWORD_DEFS`에 추가:

```python
"새카테고리": [
    "키워드1", "키워드2", "키워드3"
]
```

### 새로운 언론사 추가
`constants.py`의 `ALLOWED_SOURCES`에 추가:

```python
"언론사명": "도메인.com"
```

## 🐛 문제 해결

### 환경변수 오류
```
ValueError: NAVER_CLIENT_ID와 NAVER_CLIENT_SECRET 환경변수가 필요합니다.
```
- `.env` 파일이 올바르게 생성되었는지 확인
- 환경변수 이름이 정확한지 확인

### API 호출 오류
```
API 호출 실패: 401 - Unauthorized
```
- API 키가 올바른지 확인
- API 사용량 한도 확인

### GPT 오류
```
GPT 판별 오류: Invalid API key
```
- OpenAI API 키가 올바른지 확인
- API 키 잔액 확인

### 뉴스 선별 오류
```
GPT 선별 판별 오류: [오류 내용]
```
- OpenAI API 키가 올바른지 확인
- API 키 잔액 확인
- 프롬프트 응답 파싱 오류 시 raw_response 확인

## 📝 라이선스

이 프로젝트는 회계법인 내부 업무용으로 개발되었습니다.

## 🤝 기여

버그 리포트나 기능 제안은 이슈로 등록해주세요.

---

**개발자**: AI Assistant  
**버전**: 1.0.0  
**최종 업데이트**: 2024년
