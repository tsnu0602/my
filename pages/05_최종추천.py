import streamlit as st
import requests

st.set_page_config(layout="wide")
st.title("🌍 글로벌 이슈 기반 종목 추천 및 뉴스 분석")

API_KEY = "9f946554ab7f4bee8adbd2135abfa423"

issues = {
    "미국 금리 인상": {
        "query": "미국 금리 인상",
        "추천 종목": ["JPMorgan Chase", "Bank of America"],
        "이유": "금리 상승은 은행 수익성 개선 → 금융주 수혜"
    },
    "기술주 조정": {
        "query": "기술주 조정",
        "추천 종목": ["Apple", "NVIDIA", "Microsoft"],
        "이유": "고평가 기술주는 금리 변화에 민감함 → 조정 우려"
    },
    "우크라이나 전쟁": {
        "query": "우크라이나 전쟁",
        "추천 종목": ["Lockheed Martin", "Exxon Mobil"],
        "이유": "전쟁은 방산, 에너지주 상승 요인"
    },
    "중국 경기 부진": {
        "query": "중국 경기 부진",
        "추천 종목": ["Alibaba", "TSMC"],
        "이유": "중국 관련 종목은 경기 침체 시 타격"
    },
}

# 선택
selected = st.selectbox("🔍 현재 주목하고 있는 글로벌 이슈를 선택하세요", list(issues.keys()))
query = issues[selected]["query"]

# 뉴스 검색
st.subheader(f"📰 '{query}' 관련 실시간 뉴스")
url = "https://api.bing.microsoft.com/v7.0/news/search"
headers = {"Ocp-Apim-Subscription-Key": API_KEY}
params = {"q": query, "count": 5, "mkt": "ko-KR"}

try:
    res = requests.get(url, headers=headers, params=params)
    res.raise_for_status()
    articles = res.json().get("value", [])
    for article in articles:
        st.markdown(f"### [{article['name']}]({article['url']})")
        st.caption(article.get("provider", [{}])[0].get("name", ""))
        st.write(article.get("description", ""))
        st.markdown("---")
except Exception as e:
    st.error("뉴스를 불러오는데 문제가 발생했습니다.")
    st.exception(e)

# 추천 종목 및 이유
st.subheader("✅ 종목 추천 및 분석")
st.markdown("**추천 종목:** " + ", ".join(issues[selected]["추천 종목"]))
st.info("추천 이유: " + issues[selected]["이유"])
