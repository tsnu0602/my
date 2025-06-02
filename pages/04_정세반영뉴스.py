import streamlit as st
import requests
import pandas as pd

# Bing News API 설정
API_KEY = "YOUR_BING_API_KEY"  # ← 여기에 Bing API 키를 입력하세요
ENDPOINT = "https://api.bing.microsoft.com/v7.0/news/search"

st.set_page_config(layout="wide")
st.title("🌍 글로벌 정세 및 뉴스 분석")

st.markdown("""
### 🧭 왜 정세 분석이 중요한가요?

세계 경제와 정치 상황은 기업 가치와 시가총액에 큰 영향을 줍니다. 예를 들어:

- **금리 인상** → 기술주의 할인율 증가 → 시가총액 하락  
- **전쟁·지정학 리스크** → 에너지/방산 종목 급등  
- **환율·무역분쟁** → 수출 중심 기업 주가 변동  
- **정치적 변화** → 산업 정책 변화로 섹터별 영향  

아래에서 주요 이슈별 뉴스를 검색하고 종목 분석에 반영해보세요.
""")

# 키워드 선택
topic = st.selectbox("🔍 보고 싶은 글로벌 이슈를 선택하세요", [
    "미국 금리", "우크라이나 전쟁", "중국 경기", "환율", "기술주 조정", "원유 가격", "인플레이션", "반도체 산업"
])

# 뉴스 검색 함수
def get_news(query):
    headers = {"Ocp-Apim-Subscription-Key": API_KEY}
    params = {"q": query, "count": 5, "mkt": "ko-KR"}
    try:
        res = requests.get(ENDPOINT, headers=headers, params=params)
        articles = res.json().get("value", [])
        return [
            {
                "제목": a["name"],
                "요약": a["description"],
                "링크": a["url"],
                "출처": a["provider"][0]["name"] if "provider" in a else ""
            } for a in articles
        ]
    except Exception as e:
        st.error(f"뉴스를 불러오는 중 오류 발생: {e}")
        return []

# 뉴스 출력
st.markdown(f"### 🔎 '{topic}' 관련 최신 뉴스")
articles = get_news(topic)

if articles:
    for a in articles:
        st.markdown(f"#### 🔹 [{a['제목']}]({a['링크']})")
        st.markdown(f"_{a['출처']}_")
        st.markdown(f"{a['요약']}")
        st.markdown("---")
else:
    st.warning("관련 뉴스를 불러오지 못했습니다.")

# 해석 가이드
st.markdown("### 💡 해석 가이드")
if topic == "미국 금리":
    st.info("미국 금리가 오르면 기술주, 성장주는 시가총액이 하락할 가능성이 높습니다. 반면 은행주는 수익성이 개선되어 상승할 수 있습니다.")
elif topic == "우크라이나 전쟁":
    st.info("전쟁 장기화 시 방산주, 에너지주는 수혜를 볼 수 있으며, 글로벌 리스크 확대는 전체 시장 하락으로 이어질 수 있습니다.")
elif topic == "원유 가격":
    st.info("원유 가격이 상승하면 에너지 기업은 수혜, 항공·운송 업종은 부담을 받을 수 있습니다.")
elif topic == "반도체 산업":
    st.info("공급망 이슈나 수요 회복은 반도체 시총에 큰 영향을 줍니다. 삼성전자, TSMC, 엔비디아 등 주목.")

# 사용자 분석용 힌트
st.markdown("☑️ 이 뉴스를 보고 어떤 종목이 영향을 받을지 직접 분석해보세요.")
