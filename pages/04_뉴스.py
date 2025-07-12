import streamlit as st
import requests

# API 키 불러오기
NEWS_API_KEY = st.secrets["newsdata_api_key"]

# 뉴스 검색 함수
def get_news(query="Apple", language="en", country="us"):
    url = f"https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}&q={query}&language={language}&country={country}"

    try:
        response = requests.get(url)
        
        if response.status_code != 200:
            st.error(f"❌ 뉴스 API 오류 발생: {response.status_code} - {response.text}")
            return []
        
        data = response.json()
        if "results" not in data or not data["results"]:
            st.warning("🔍 뉴스 결과가 없습니다.")
            return []

        return data["results"]

    except Exception as e:
        st.error(f"⚠️ 뉴스 요청 중 오류 발생: {e}")
        return []

# 테스트 UI
st.title("📰 NewsData.io 뉴스 테스트")

stock = st.text_input("🔎 검색할 종목 이름", "Apple")

if st.button("뉴스 불러오기"):
    news_items = get_news(stock)

    if news_items:
        for news in news_items[:3]:
            st.subheader(news.get("title", "제목 없음"))
            st.write(news.get("description", "내용 없음"))
            st.caption(news.get("pubDate", "날짜 정보 없음"))
            st.markdown("---")
    else:
        st.info("결과가 없거나 오류가 있었습니다.")
