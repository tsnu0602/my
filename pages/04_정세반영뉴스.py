import streamlit as st
st.set_page_config(layout="wide")  # <-- 반드시 import 직후, 가장 먼저 호출

import requests
import pandas as pd
import openai

# API 키 입력 받기 (secrets 혹은 입력창)
BING_API_KEY = st.secrets.get("BING_API_KEY") or st.text_input("Bing API Key 입력", type="password")
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY") or st.text_input("OpenAI API Key 입력", type="password")
openai.api_key = OPENAI_API_KEY

st.title("🌍 글로벌 정세 및 뉴스 분석 + AI 요약")

st.markdown("""
### 🧭 왜 정세 분석이 중요한가요?

세계 경제와 정치 상황은 기업 가치와 시가총액에 큰 영향을 줍니다. 예를 들어:

- **금리 인상** → 기술주의 할인율 증가 → 시가총액 하락  
- **전쟁·지정학 리스크** → 에너지/방산 종목 급등  
- **환율·무역분쟁** → 수출 중심 기업 주가 변동  
- **정치적 변화** → 산업 정책 변화로 섹터별 영향  

아래에서 주요 이슈별 뉴스를 검색하고, AI 요약 기능을 통해 빠르게 핵심만 파악해보세요.
""")

topic = st.selectbox("🔍 보고 싶은 글로벌 이슈를 선택하세요", [
    "미국 금리", "우크라이나 전쟁", "중국 경기", "환율", "기술주 조정", "원유 가격", "인플레이션", "반도체 산업"
])

def get_news(query):
    headers = {"Ocp-Apim-Subscription-Key": BING_API_KEY}
    params = {"q": query, "count": 5, "mkt": "ko-KR"}
    try:
        res = requests.get("https://api.bing.microsoft.com/v7.0/news/search", headers=headers, params=params)
        if res.status_code != 200:
            st.error(f"뉴스 API 오류: {res.status_code}")
            return []
        articles = res.json().get("value", [])
        return [
            {
                "제목": a["name"],
                "요약": a["description"],
                "링크": a["url"],
                "출처": a.get("provider", [{}])[0].get("name", ""),
                "내용": a.get("description", "")
            } for a in articles
        ]
    except Exception as e:
        st.error(f"뉴스를 불러오는 중 오류 발생: {e}")
        return []

st.markdown(f"### 🔎 '{topic}' 관련 최신 뉴스")
articles = get_news(topic)

if articles:
    for idx, a in enumerate(articles):
        with st.expander(f"🔹 {a['제목']}"):
            st.markdown(f"**출처**: {a['출처']}  \n**요약**: {a['요약']}  \n[원문 보기]({a['링크']})")

            if OPENAI_API_KEY and st.button(f"AI 요약 보기 (뉴스 {idx+1})", key=f"summary_btn_{idx}"):
                with st.spinner("AI가 요약 중입니다..."):
                    try:
                        response = openai.ChatCompletion.create(
                            model="gpt-4",
                            messages=[
                                {"role": "system", "content": "아래 뉴스 내용을 간결하고 분석적으로 요약해줘."},
                                {"role": "user", "content": a['내용']}
                            ]
                        )
                        summary = response.choices[0].message.content.strip()
                        st.success("📄 AI 요약 결과:")
                        st.write(summary)
                    except Exception as e:
                        st.error(f"OpenAI 요약 실패: {e}")
else:
    st.warning("관련 뉴스를 불러오지 못했습니다. API 키를 확인하세요.")

st.markdown("### 💡 해석 가이드")
if topic == "미국 금리":
    st.info("미국 금리가 오르면 기술주, 성장주는 시가총액이 하락할 가능성이 높습니다. 반면 은행주는 수익성이 개선되어 상승할 수 있습니다.")
elif topic == "우크라이나 전쟁":
    st.info("전쟁 장기화 시 방산주, 에너지주는 수혜를 볼 수 있으며, 글로벌 리스크 확대는 전체 시장 하락으로 이어질 수 있습니다.")
elif topic == "원유 가격":
    st.info("원유 가격이 상승하면 에너지 기업은 수혜, 항공·운송 업종은 부담을 받을 수 있습니다.")
elif topic == "반도체 산업":
    st.info("공급망 이슈나 수요 회복은 반도체 시총에 큰 영향을 줍니다. 삼성전자, TSMC, 엔비디아 등 주목.")

st.markdown("☑️ 이 뉴스를 보고 어떤 종목이 영향을 받을지 직접 분석해보세요.")
