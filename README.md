# ✈️ 트립가자(tripgaja.co.kr) GitHub Actions 자동 포스팅 시스템

워드프레스 블로그 **트립가자 | 해외 한달살기 실전 가이드**(https://tripgaja.co.kr)에 **매일 1건씩 고품질 SEO 가이드 글을 자동 발행**하는 GitHub Actions 자동화 시스템입니다.

---

## 🌟 주요 기능

1. **매일 한국 시간 오전 9시 자동 발행**
   - GitHub Actions Cron 스케줄러(`0 0 * * *`)를 통해 서버나 PC를 켜둘 필요 없이 클라우드에서 자동 실행됩니다.
   - 필요 시 GitHub 웹 화면에서 **[Run workflow]** 버튼을 눌러 즉시 글을 발행할 수도 있습니다.
2. **엄선된 30개+ 실전 한달살기 큐(`topics_queue.json`) 탑재**
   - 동남아, 일본·대만, 유럽, 금융/환전/카드, 준비/보험 등 5개 핵심 카테고리에 최적화된 주제가 준비되어 있습니다.
   - 큐에 있는 주제를 순서대로 매일 1개씩 발행하며, 큐가 모두 소진되면 AI가 과거 글들과 겹치지 않는 새로운 주제를 스스로 기획하여 작성합니다.
3. **고품질 SEO 구조화 본문 자동 생성**
   - 3줄 핵심 요약 하이라이트 박스
   - H2, H3 계층형 목차 및 소제목
   - 반응형 비교 표(HTML Table)
   - 자주 묻는 질문(FAQ) 아코디언 스타일
   - Rank Math SEO 포커스 키워드 및 메타 디스크립션 자동 세팅
4. **발행 이력 관리 및 중복 방지**
   - 발행 완료된 글은 `data/published_history.json`에 ID, 제목, 링크, 발행일시가 자동 기록되고 GitHub 저장소에 커밋/푸시됩니다.

---

## 🚀 깃허브 연동 및 사용 방법

### 1단계: 깃허브 저장소(Repository) 생성
1. [GitHub](https://github.com/)에 로그인 후 우측 상단 `+` 버튼 -> **[New repository]**를 클릭합니다.
2. 저장소 이름(예: `tripgaja-auto-poster`)을 입력하고 **Private** 또는 **Public**을 선택한 뒤 **[Create repository]**를 누릅니다.

### 2단계: 로컬 코드를 깃허브 저장소로 푸시
터미널(PowerShell 또는 Git Bash)을 열고 현재 폴더(`c:\antigravity\site\tripgaja.co.kr`)에서 아래 명령어를 순서대로 실행합니다:

```bash
cd c:\antigravity\site\tripgaja.co.kr

# 깃 초기화 및 기본 브랜치 설정
git init -b main

# 파일 추가 및 초기 커밋
git add .
git commit -m "feat: initial commit for tripgaja daily auto poster"

# 본인의 깃허브 저장소 주소 연결 (본인 계정/저장소명으로 변경)
git remote add origin https://github.com/<본인아이디>/<저장소이름>.git

# 깃허브로 푸시
git push -u origin main
```

---

### 3단계: GitHub Secrets (환경변수) 등록
저장소의 **Settings** -> **Secrets and variables** -> **Actions** 메뉴로 이동하여 **[New repository secret]**을 클릭해 아래 키들을 등록합니다:

| Secret 이름 | 설명 | 필수 여부 | 권장 값 |
| :--- | :--- | :---: | :--- |
| `OPENAI_API_KEY` | OpenAI API 키 (GPT-4o-mini 생성용) | 선택 (권장) | `sk-...` (없으면 템플릿 모드로 동작) |
| `GEMINI_API_KEY` | Google Gemini API 키 | 선택 | Gemini API 키 (OpenAI 대신 사용 가능) |
| `WP_URL` | 워드프레스 주소 | 기본 내장됨 | `https://tripgaja.co.kr` (생략 가능) |
| `WP_USERNAME` | 관리자 이메일 | 기본 내장됨 | `tripgajagpt@gmail.com` (생략 가능) |
| `WP_APP_PASSWORD` | 워드프레스 애플리케이션 비밀번호 | 기본 내장됨 | `dg6i NgEG Jp0q yNTr Ny2v fZiL` (생략 가능) |

> 💡 **안내:** 워드프레스 접속 주소 및 애플리케이션 비밀번호는 스크립트 기본값으로도 설정되어 있으므로, **`OPENAI_API_KEY` (또는 `GEMINI_API_KEY`)** 하나만 등록하셔도 바로 정상 작동합니다!

---

### 4단계: 워크플로우 쓰기 권한(Workflow permissions) 설정
GitHub Actions가 발행 이력을 자동으로 저장소에 다시 커밋하려면 아래 설정이 켜져 있어야 합니다:
1. 저장소 상단 **Settings** 클릭
2. 좌측 메뉴 **Actions** -> **General** 클릭
3. 페이지 맨 아래 **Workflow permissions** 섹션에서:
   - **"Read and write permissions"** 선택
   - **[Save]** 클릭

---

### 5단계: 첫 포스팅 테스트 (수동 실행)
1. 저장소 상단의 **[Actions]** 탭으로 이동합니다.
2. 좌측 목록에서 **"Daily Auto Post to WordPress"**를 클릭합니다.
3. 우측의 **[Run workflow]** 파란색 버튼을 누르고 **[Run workflow]**를 클릭합니다.
4. 약 30초~1분 후 초록색 체크(`✔`)가 뜨면 [tripgaja.co.kr](https://tripgaja.co.kr/)에서 새로 올라온 글을 확인하실 수 있습니다!

---

## 📂 프로젝트 구조

```
tripgaja.co.kr/
├── .github/
│   └── workflows/
│       └── daily_post.yml      # 매일 09:00 KST 자동 실행 워크플로우
├── data/
│   ├── topics_queue.json       # 발행 대기 중인 주제 목록 (30개+)
│   └── published_history.json  # 발행 완료된 글 목록
├── auto_post.py                # AI 본문 생성 및 WP REST API 발행 스크립트
├── requirements.txt            # 파이썬 의존성 패키지
├── .env.example                # 로컬 환경변수 템플릿
├── .gitignore
└── README.md
```

---

## 🛠️ 내가 원하는 주제 추가하기
나중에 다루고 싶은 주제가 생기면 언제든지 `data/topics_queue.json` 파일에 아래와 같은 형식으로 추가해 두시면 순서대로 발행됩니다:

```json
{
  "category": "동남아 한달살기",
  "topic": "베트남 달랏 한달살기: 일 년 내내 봄 날씨와 호수 뷰 감성 빌라 렌트",
  "keywords": ["달랏 한달살기", "베트남 달랏 숙소", "달랏 날씨", "달랏 물가"]
}
```
