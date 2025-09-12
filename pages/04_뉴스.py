import streamlit as st
import requests

# ✅ API 키 설정 (secrets.toml에 저장되어 있어야 함)
NEWS_API_KEY = st.secrets["newsdata_api_key"]

# ✅ 기본 설정
st.set_page_config(page_title="📰 뉴스", layout="centered")
st.title("📰 뉴스 기반 종목 정보 (분석 제외)")

# ✅ 종목 선택
stocks = ["Apple", "Tesla", "Amazon", "Google", "Microsoft"]
stock_name = st.selectbox("🔎 뉴스 확인할 종목 선택", stocks)

# ✅ 뉴스 불러오기 함수
def get_news(query="Apple", language="en", country="us"):
    url = f"https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}&q={query}&language={language}&country={country}"
    try:
        res = requests.get(url)
        if res.status_code != 200:
            st.error(f"❌ 뉴스 API 오류: {res.status_code} - {res.text}")
            return []
        return res.json().get("results", [])
    except Exception as e:
        st.error(f"⚠️ 뉴스 요청 오류: {e}")
        return []

# ✅ 뉴스 출력
st.subheader(f"📰 {stock_name} 관련 뉴스")

news_items = get_news(query=f"{stock_name} stock")
if not news_items:
    st.info("📭 관련 뉴스가 없습니다.")
else:
    seen_titles = set()
    for article in news_items:
        title = article.get("title", "제목 없음")
        if title in seen_titles:
            continue
        seen_titles.add(title)

        st.markdown(f"### {title}")
        st.write(article.get("description", "설명 없음"))
        st.caption(f"🕒 {article.get('pubDate', '날짜 없음')}")
        st.markdown(f"[🔗 원문 보기]({article.get('link', '#')})")
        st.markdown("---")
