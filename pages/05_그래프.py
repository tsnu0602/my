import streamlit as st
import plotly.graph_objs as go
import datetime
import pandas as pd
import numpy as np
import requests

# 페이지 설정
st.set_page_config(page_title="뉴스 + 주가 (차트)", layout="wide")
st.title("📰 뉴스 + 📉 차트 대시보드")

# 종목 목록
stocks = {
    "Apple": "AAPL",
    "Tesla": "TSLA",
    "Amazon": "AMZN",
    "Google": "GOOGL",
    "Microsoft": "MSFT"
}
stock_name = st.selectbox("🔎 분석할 종목 선택", list(stocks.keys()))
ticker = stocks[stock_name]

# 날짜 설정
end_date = datetime.date.today()
start_date = st.date_input("📅 시작 날짜 선택", end_date - datetime.timedelta(days=90))
if start_date >= end_date:
    st.error("⚠️ 시작 날짜는 종료 날짜보다 이전이어야 합니다.")
    st.stop()

# ✅ 더미 주가 데이터 생성 함수
@st.cache_data
def generate_mock_stock_data(start_date, end_date):
    dates = pd.date_range(start=start_date, end=end_date, freq='B')  # 평일만
    np.random.seed(42)
    prices = np.cumsum(np.random.normal(0, 1, len(dates))) + 100  # 모의 주가
    df = pd.DataFrame({'Date': dates, 'Close': prices})
    return df

mock_data = generate_mock_stock_data(start_date, end_date)

# ✅ 주가 차트 표시
if mock_data.empty:
    st.warning("📭 주가 데이터가 없습니다.")
else:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=mock_data["Date"],
        y=mock_data["Close"],
        mode="lines",
        name=f"{stock_name} 종가 (모의)"
    ))
    fig.update_layout(
        title=f"{stock_name} 주가 차트 (모의 데이터)",
        xaxis_title="날짜",
        yaxis_title="가격 (USD)",
        template="plotly_white",
        xaxis_rangeslider_visible=True
    )
    st.plotly_chart(fig, use_container_width=True)

# ✅ 뉴스 API 설정
NEWS_API_KEY = st.secrets["newsdata_api_key"]

def get_news(query):
    url = f"https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}&q={query}&language=en"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get("results", [])
        else:
            st.error(f"❌ 뉴스 API 오류: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"❌ 뉴스 요청 실패: {e}")
        return []

# ✅ 뉴스 섹션
st.subheader(f"📰 {stock_name} 관련 뉴스")
news_items = get_news(stock_name)

if not news_items:
    st.info("📭 관련 뉴스가 없습니다.")
else:
    for article in news_items:
        title = article.get("title", "제목 없음")
        description = article.get("description", "설명 없음")
        link = article.get("link", "#")
        pub_date = article.get("pubDate", "날짜 없음")

        st.markdown(f"### {title}")
        st.write(description)
        st.caption(f"🕒 {pub_date}")
        st.markdown(f"[🔗 원문 보기]({link})")
        st.markdown("---")
