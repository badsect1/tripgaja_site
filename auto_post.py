#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
트립가자(tripgaja.co.kr) GitHub Actions 매일 1회 자동 포스팅 스크립트
해외 한달살기 실전 가이드 블로그 자동화
"""

import os
import sys
import json
import re
import datetime
import requests
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# 설정 (환경변수 또는 기본값)
# ==========================================
WP_URL = os.getenv("WP_URL", "https://tripgaja.co.kr").rstrip("/")
WP_USERNAME = os.getenv("WP_USERNAME", "tripgajagpt@gmail.com")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD", "dg6i NgEG Jp0q yNTr Ny2v fZiL")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
AI_PROVIDER = os.getenv("AI_PROVIDER", "auto").lower()

CATEGORY_MAP = {
    "동남아 한달살기": 4,
    "일본·대만 한달살기": 5,
    "유럽 한달살기": 6,
    "환전·카드·생활비": 7,
    "준비·보험·짐싸기": 8,
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
QUEUE_FILE = os.path.join(DATA_DIR, "topics_queue.json")
HISTORY_FILE = os.path.join(DATA_DIR, "published_history.json")


def load_json(path, default=None):
    if not os.path.exists(path):
        return default if default is not None else []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[!] JSON 파일 로드 실패 ({path}): {e}")
        return default if default is not None else []


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_next_topic():
    queue = load_json(QUEUE_FILE, [])
    history = load_json(HISTORY_FILE, [])

    if queue:
        topic_item = queue.pop(0)
        save_json(QUEUE_FILE, queue)
        print(f"[+] 큐에서 주제 추출: {topic_item.get('topic')}")
        return topic_item

    # 큐가 비어있을 경우 AI로 새 주제 자동 생성
    print("[*] 큐가 비어있어 새로운 주제를 자동 생성합니다...")
    published_titles = [h.get("title", "") for h in history[-20:]]
    new_topic = generate_dynamic_topic(published_titles)
    return new_topic


def generate_dynamic_topic(recent_titles):
    prompt = f"""
너는 '트립가자(해외 한달살기 실전 가이드)' 블로그의 전문 에디터야.
다음은 최근 발행된 글 제목들이야:
{json.dumps(recent_titles, ensure_ascii=False, indent=2)}

위 목록과 중복되지 않는 '해외 한달살기' 세부 주제를 1개 기획해줘.
카테고리는 반드시 다음 중 하나여야 해:
1) 동남아 한달살기
2) 일본·대만 한달살기
3) 유럽 한달살기
4) 환전·카드·생활비
5) 준비·보험·짐싸기

반드시 다음 JSON 형식으로만 응답해:
{{
  "category": "선택한 카테고리명",
  "topic": "도시명 또는 핵심 키워드가 포함된 구체적이고 매력적인 주제",
  "keywords": ["핵심키워드1", "키워드2", "키워드3"]
}}
"""
    res = call_ai(prompt, system_prompt="JSON으로만 응답하는 여행 콘텐츠 플래너")
    try:
        clean_res = re.sub(r"```json\s*", "", res)
        clean_res = re.sub(r"```", "", clean_res).strip()
        data = json.loads(clean_res)
        return data
    except Exception:
        return {
            "category": "동남아 한달살기",
            "topic": "태국 치앙마이 워케이션 코워킹 스페이스 BEST 5 및 월 이용료 비교",
            "keywords": ["치앙마이 코워킹", "치앙마이 워케이션", "치앙마이 디지털노마드 카페"]
        }


def call_ai(prompt, system_prompt=""):
    # 1. OpenAI 호출 시도
    if (AI_PROVIDER in ("auto", "openai")) and OPENAI_API_KEY:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt or "You are a professional travel blogger."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[!] OpenAI API 호출 오류: {e}")

    # 2. Gemini 호출 시도
    if (AI_PROVIDER in ("auto", "gemini")) and GEMINI_API_KEY:
        try:
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = model.generate_content(full_prompt)
            return response.text.strip()
        except Exception as e:
            print(f"[!] Gemini API 호출 오류: {e}")

    # 3. API 키가 없을 때 기본 템플릿 반환
    print("[!] 유효한 AI API Key가 없습니다. 기본 템플릿 생성기로 대체합니다.")
    return None


def generate_article_content(topic_item):
    topic = topic_item.get("topic")
    category = topic_item.get("category", "동남아 한달살기")
    keywords = topic_item.get("keywords", ["해외 한달살기"])

    prompt = f"""
너는 네이버/구글 검색 상위 노출에 최적화된 고품질 여행 실전 가이드 블로그 전문 작가야.
블로그 명: '트립가자 | 해외 한달살기 실전 가이드' (스타일: biz.postincome.co.kr 처럼 깔끔하고 실용적인 정보성 글)

주제: {topic}
카테고리: {category}
핵심 키워드: {', '.join(keywords)}

[작성 지침]
1. 제목(title): 클릭률(CTR)과 검색 최적화가 높은 매력적인 제목 (숫자, 꿀팁, 실전 비교 등 포함)
2. 슬러그(slug): 영문 소문자와 하이픈(-)으로 구성된 간결한 URL 슬러그 (예: fukuoka-monthly-mansion-stay)
3. 본문(content_html):
   - 전체 분량: 공백 제외 2,000자 내외의 충실한 실전 가이드
   - 반드시 깔끔한 HTML 태그(<p>, <h2>, <h3>, <ul>, <li>, <table>, <blockquote> 등)로 작성
   - 최상단 요약 박스: <div style="background:#f8fafc; border-left:4px solid #2563eb; padding:16px; border-radius:6px; margin-bottom:24px;"> 에 3줄 핵심 요약 포함
   - 목차(H2 태그 기반) 안내
   - 본문 H2 4~5개, 각 H2 아래 H3 서브 섹션 포함
   - 본문 중간에 '실제 체류 비용 비교' 또는 '장단점 비교'를 나타내는 반응형 깔끔한 HTML <table> 표 1개 반드시 삽입
   - 현지 경험자의 실제 조언(팁 박스) 포함
   - 하단에 '자주 묻는 질문(FAQ)' 3가지 Q&A 형식으로 작성
   - 마무리 요약 및 체크리스트 정리
4. 포커스 키워드(focus_keyword): Rank Math SEO용 대표 키워드 1개
5. 메타 디스크립션(meta_description): 검색엔진 결과에 표시될 130~150자 매력적인 요약문
6. 태그(tags): 관련 검색어 태그 5개 (문자열 배열)

반드시 아래 JSON 포맷으로만 응답해줘. 코드블록 없이 순수 JSON만 출력:
{{
  "title": "게시글 제목",
  "slug": "url-slug-in-english",
  "focus_keyword": "대표키워드",
  "meta_description": "메타 설명 140자 내외",
  "tags": ["태그1", "태그2", "태그3", "태그4", "태그5"],
  "content_html": "<div style=...>...본문 전체 HTML...</div>"
}}
"""
    system_prompt = "너는 해외 한달살기 실전 가이드 웹진의 수석 에디터이며, 완벽한 SEO HTML과 JSON 형식을 출력한다."
    ai_response = call_ai(prompt, system_prompt)

    if ai_response:
        try:
            clean_res = re.sub(r"^```json\s*", "", ai_response)
            clean_res = re.sub(r"\s*```$", "", clean_res).strip()
            article = json.loads(clean_res)
            return article
        except Exception as e:
            print(f"[!] AI 응답 JSON 파싱 실패 ({e}). 템플릿 모드로 전환합니다.")

    # Fallback Template Generator
    return generate_fallback_article(topic_item)


def generate_fallback_article(topic_item):
    topic = topic_item.get("topic")
    category = topic_item.get("category", "동남아 한달살기")
    keywords = topic_item.get("keywords", ["해외 한달살기"])
    primary_kw = keywords[0] if keywords else "해외 한달살기"
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", topic.lower()).strip("-")[:40] or "overseas-monthly-stay"

    html = f"""<div class="entry-content">
<div style="background:#f8fafc; border-left:4px solid #2563eb; padding:18px; border-radius:6px; margin-bottom:28px;">
<p style="margin:0; font-weight:bold; color:#1e3a8a; font-size:16px;">💡 실전 한달살기 핵심 요약</p>
<ul style="margin:10px 0 0 0; padding-left:20px; color:#334155; line-height:1.7;">
<li><strong>목적:</strong> {topic} 실전 가이드와 필수 점검 사항 완벽 정리</li>
<li><strong>핵심 포인트:</strong> 현지 숙소 선택 기준, 월 생활비 절약 팁, 교통 및 안전 수칙</li>
<li><strong>추천 대상:</strong> 단기 여행을 넘어 여유로운 로컬 라이프를 경험하고 싶은 여행자</li>
</ul>
</div>

<p>해외 한달살기는 관광지만 스쳐 지나가는 패키지 여행과 달리, 현지의 아침 시장을 거닐고 동네 단골 카페를 만들며 '살아보는' 특별한 경험입니다. 하지만 철저한 준비 없이 떠나면 예상치 못한 생활비 지출과 낯선 인프라로 인해 고생하기 쉽습니다.</p>
<p>이번 실전 가이드에서는 <strong>{topic}</strong>의 핵심 정보와 후회 없는 체류를 위한 꿀팁을 하나씩 짚어드립니다.</p>

<h2>1. 최적의 체류 지역 및 숙소 유형 비교</h2>
<p>한달살기의 만족도를 결정하는 가장 중요한 요소는 바로 '숙소의 위치'입니다. 편의점, 대형 마트, 대중교통 접근성이 뛰어난 지역을 선정해야 생활 피로도를 최소화할 수 있습니다.</p>

<table style="width:100%; border-collapse:collapse; margin:20px 0; font-size:14px; text-align:left;">
<thead>
<tr style="background:#f1f5f9; border-bottom:2px solid #cbd5e1;">
<th style="padding:12px; border:1px solid #e2e8f0;">숙소 형태</th>
<th style="padding:12px; border:1px solid #e2e8f0;">월 평균 예상 비용</th>
<th style="padding:12px; border:1px solid #e2e8f0;">장점</th>
<th style="padding:12px; border:1px solid #e2e8f0;">주의점</th>
</tr>
</thead>
<tbody>
<tr>
<td style="padding:12px; border:1px solid #e2e8f0;"><strong>서비스 아파트 / 레지던스</strong></td>
<td style="padding:12px; border:1px solid #e2e8f0;">80만 ~ 150만원</td>
<td style="padding:12px; border:1px solid #e2e8f0;">주 1~2회 청소, 수영장/헬스장 완비, 보안 우수</td>
<td style="padding:12px; border:1px solid #e2e8f0;">전기세/수도세 별도 청구 여부 사전 확인 필요</td>
</tr>
<tr style="background:#f8fafc;">
<td style="padding:12px; border:1px solid #e2e8f0;"><strong>에어비앤비 (단기임대)</strong></td>
<td style="padding:12px; border:1px solid #e2e8f0;">70만 ~ 130만원</td>
<td style="padding:12px; border:1px solid #e2e8f0;">취사 시설 완비, 현지 감성 주택 거주 가능</td>
<td style="padding:12px; border:1px solid #e2e8f0;">인터넷 와이파이 속도 편차, 호스트 소통 중요</td>
</tr>
<tr>
<td style="padding:12px; border:1px solid #e2e8f0;"><strong>현지 장기 렌트 콘도</strong></td>
<td style="padding:12px; border:1px solid #e2e8f0;">50만 ~ 90만원</td>
<td style="padding:12px; border:1px solid #e2e8f0;">가장 저렴한 월세, 장기 체류에 최적</td>
<td style="padding:12px; border:1px solid #e2e8f0;">보증금 반환 조건 및 최소 계약기간 확인 필수</td>
</tr>
</tbody>
</table>

<h2>2. 현지 한 달 예상 생활비 구조와 절약 노하우</h2>
<p>한달살기 예산은 크게 <strong>고정비(숙소, 항공권, 여행자보험)</strong>와 <strong>변동비(식비, 교통비, 여가비)</strong>로 나뉩니다. 로컬 식당과 대형 슈퍼마켓(취사)을 적절히 병행하면 국내 생활비와 비슷하거나 오히려 더 알뜰하게 지낼 수 있습니다.</p>
<ul>
<li><strong>식비 관리:</strong> 아침은 숙소에서 가볍게 토스트와 과일로 해결하고, 점심은 가성비 좋은 로컬 식당, 저녁은 분위기 있는 레스토랑을 방문하는 패턴을 추천합니다.</li>
<li><strong>교통 수단:</strong> 그랩(Grab)이나 볼트(Bolt) 같은 호출 앱 이용 시 시간대별 프로모션 코드를 적극 활용하고, 지하철/트램 정기권이 있는 도시는 30일 패스를 구입하는 것이 훨씬 경제적입니다.</li>
<li><strong>환전 및 결제:</strong> 현지 결제는 수수료가 없는 트래블로그나 트래블월렛 카드를 사용하고, 비상용 현금은 현지 ATM에서 1~2회에 몰아서 인출하세요.</li>
</ul>

<h2>3. 체류 전 반드시 체크해야 할 필수 준비물</h2>
<p>현지에서도 대부분의 물품을 구매할 수 있지만, 한국에서 챙겨가야 삶의 질이 수직 상승하는 품목들이 있습니다.</p>
<ol>
<li><strong>샤워기 헤드 & 비타민 필터:</strong> 수질 환경이 다른 해외에서는 석회수나 노후 배관으로 인한 피부 트러블이 흔하므로 여분 필터 3~4개를 챙기세요.</li>
<li><strong>상비약 키트:</strong> 현지 약국 약은 성분이 강할 수 있으므로 소화제, 지사제, 종합감기약, 알레르기 비염약, 밴드는 한국에서 복용하던 약으로 구비합니다.</li>
<li><strong>멀티탭 & 어댑터:</strong> 디지털 기기(노트북, 스마트폰, 보조배터리 등) 충전을 위해 3~4구 멀티탭 1개는 필수입니다.</li>
</ol>

<h2>4. 자주 묻는 질문 (FAQ)</h2>
<div style="margin-top:16px;">
<div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:14px; margin-bottom:12px;">
<p style="margin:0; font-weight:bold; color:#0f172a;">Q. 언어 소통이 서툴러도 혼자 한달살기가 가능한가요?</p>
<p style="margin:6px 0 0 0; color:#475569;">A. 파파고, 구글 번역기와 구글 맵만 능숙하게 다룰 줄 안다면 언어 장벽은 전혀 문제가 되지 않습니다. 현지 상점이나 숙소 호스트와도 번역 앱으로 충분히 원활하게 소통할 수 있습니다.</p>
</div>
<div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:14px; margin-bottom:12px;">
<p style="margin:0; font-weight:bold; color:#0f172a;">Q. 여행자보험은 꼭 가입해야 하나요?</p>
<p style="margin:6px 0 0 0; color:#475569;">A. 반드시 가입해야 합니다. 장기 체류 중 예기치 못한 식중독, 사고, 휴대품 도난/파손 사고가 발생했을 때 해외 병원비는 매우 고액입니다. 해외의료비와 휴대품 손해 담보가 든든한 플랜을 선택하세요.</p>
</div>
</div>

<h2>5. 마치며: 나만의 한달살기를 완성하는 법</h2>
<p>{topic} 준비는 서두르지 않고 차근차근 계획을 세우는 것부터 시작됩니다. 완벽한 계획보다는 현지에서의 유연한 태도가 더욱 풍요로운 여행을 만들어줍니다. 오늘 정리해 드린 체크리스트를 바탕으로 설레는 한달살기 여정을 시작해 보세요!</p>
</div>"""

    return {
        "title": topic,
        "slug": slug,
        "focus_keyword": primary_kw,
        "meta_description": f"{topic}의 숙소 선택 가이드, 월 생활비 예산, 교통편, 필수 준비물 체크리스트까지 직접 경험한 노하우를 바탕으로 알기 쉽게 정리해 드립니다.",
        "tags": keywords + ["해외한달살기", "한달살기경비", "트립가자"],
        "content_html": html
    }


def get_or_create_tag(tag_name):
    url = f"{WP_URL}/wp-json/wp/v2/tags"
    auth = (WP_USERNAME, WP_APP_PASSWORD)
    try:
        # 태그 검색
        r = requests.get(url, params={"search": tag_name}, auth=auth, timeout=10)
        if r.status_code == 200:
            results = r.json()
            for t in results:
                if t.get("name") == tag_name:
                    return t.get("id")

        # 태그 신규 생성
        create_res = requests.post(url, json={"name": tag_name}, auth=auth, timeout=10)
        if create_res.status_code in (200, 201):
            return create_res.json().get("id")
    except Exception as e:
        print(f"[!] 태그 처리 오류 ({tag_name}): {e}")
    return None


def publish_to_wordpress(article_data, category_name):
    url = f"{WP_URL}/wp-json/wp/v2/posts"
    auth = (WP_USERNAME, WP_APP_PASSWORD)

    category_id = CATEGORY_MAP.get(category_name, 4)

    # 태그 ID 변환
    tag_ids = []
    for tag in article_data.get("tags", [])[:5]:
        tid = get_or_create_tag(tag)
        if tid:
            tag_ids.append(tid)

    post_payload = {
        "title": article_data.get("title"),
        "content": article_data.get("content_html"),
        "slug": article_data.get("slug"),
        "status": "publish",
        "categories": [category_id],
        "tags": tag_ids,
        "meta": {
            "rank_math_focus_keyword": article_data.get("focus_keyword", ""),
            "rank_math_description": article_data.get("meta_description", "")
        }
    }

    try:
        response = requests.post(url, json=post_payload, auth=auth, timeout=30)
        if response.status_code in (200, 201):
            post_info = response.json()
            post_id = post_info.get("id")
            post_link = post_info.get("link")
            print(f"[✔] 글 발행 성공! ID: {post_id} | URL: {post_link}")
            return {
                "id": post_id,
                "title": article_data.get("title"),
                "link": post_link,
                "date": datetime.datetime.now().isoformat()
            }
        else:
            print(f"[!] WordPress 발행 실패 (Status: {response.status_code}): {response.text}")
    except Exception as e:
        print(f"[!] WordPress API 요청 실패: {e}")
    return None


def main():
    print("=" * 60)
    print("🚀 트립가자(tripgaja.co.kr) 자동 포스팅 시작")
    print(f"⏰ 실행 시간: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 1. 포스팅할 주제 선정
    topic_item = get_next_topic()
    category = topic_item.get("category", "동남아 한달살기")
    print(f"📌 주제: {topic_item.get('topic')}")
    print(f"📁 카테고리: {category}")

    # 2. 본문 및 메타데이터 생성
    print("[*] 본문 콘텐츠 생성 중...")
    article_data = generate_article_content(topic_item)
    print(f"📝 글 제목: {article_data.get('title')}")
    print(f"🔑 포커스 키워드: {article_data.get('focus_keyword')}")

    # 3. 워드프레스 발행
    print("[*] 워드프레스 REST API 전송 중...")
    published_info = publish_to_wordpress(article_data, category)

    if published_info:
        # 4. 발행 이력 기록
        history = load_json(HISTORY_FILE, [])
        history.insert(0, published_info)
        save_json(HISTORY_FILE, history)
        print(f"[✔] 이력 파일 갱신 완료: 총 {len(history)}개 포스팅 기록")
        print("🎉 자동 포스팅 완료!")
    else:
        print("[✖] 포스팅 발행 실패. 큐 복구를 위해 확인이 필요합니다.")
        sys.exit(1)


if __name__ == "__main__":
    main()
