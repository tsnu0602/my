import streamlit as st
import requests
import yfinance as yf
import plotly.graph_objs as go
import datetime

NEWS_API_KEY = st.secrets["newsdata_api_key"]

st.set_page_config(page_title="📈 종목 분석 대시보드", layout="centered")
st.title("📊 주가 + 뉴스 통합 대시보드")

stocks = {
    "Apple": "AAPL",
    "Tesla": "TSLA",
    "Amazon": "AMZN",
    "Google": "GOOGL",
    "Microsoft": "MSFT"
}
stock_name = st.selectbox("🔎 분석할 종목을 선택하세요", list(stocks.keys()))
ticker = stocks[stock_name]

today = datetime.date.today()
default_start = today - datetime.timedelta(days=90)
start_date = st.date_input("시작 날짜", default_start)

start_date_str = start_date.strftime("%Y-%m-%d")
end_date_str = today.strftime("%Y-%m-%d")

with st.spinner("📉 주가 데이터를 불러오는 중..."):
    try:
        stock_data = yf.download(ticker, start=start_date_str, end=end_date_str)
    except Exception as e:
        st.error(f"❌ 주가 데이터를 불러오는 데 실패했습니다: {e}")
        stock_data = None

st.subheader(f"💹 {stock_name} 주가 차트")

if stock_data is None or stock_data.empty:
    st.warning("📭 주가 데이터가 없습니다.")
else:
    if 'Close' in stock_data.columns:
        price_col = 'Close'
    elif 'Adj Close' in stock_data.columns:
        price_col = 'Adj Close'
    else:
        st.warning("주가 데이터에 'Close' 또는 'Adj Close' 컬럼이 없습니다.")
        price_col = None

    if price_col:
        stock_data = stock_data.dropna(subset=[price_col])
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data[price_col], mode='lines', name=price_col))
        fig.update_layout(title=f"{stock_name} ({ticker}) 주가 차트", xaxis_title="날짜", yaxis_title="가격 (USD)", template="plotly_white", xaxis_rangeslider_visible=True)
        st.plotly_chart(fig)

def get_news(query="Apple", language="en"):
    url = f"https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}&q={query}&language={language}"
    try:
        res = requests.get(url)
        if res.status_code != 200:
            st.error(f"❌ 뉴스 API 오류: {res.status_code} - {res.text}")
            return []
        return res.json().get("results", [])
    except Exception as e:
        st.error(f"⚠️ 뉴스 요청 오류: {e}")
        return []

st.subheader(f"📰 {stock_name} 관련 뉴스")

news_items = get_news(query=f"{stock_name} stock")
if not news_items:
    st.info("📭 관련 뉴스가 없습니다.")
else:
    for article in news_items:
        title = article.get("title", "제목 없음")
        description = article.get("description", "")
        st.markdown(f"### {title}")
        st.write(description or "📌 설명이 제공되지 않았습니다.")
        st.caption(f"🕒 {article.get('pubDate', '날짜 없음')}")
        st.markdown(f"[🔗 원문 보기]({article.get('link', '#')})")
        st.markdown("---")
