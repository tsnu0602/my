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
    # Close 또는 Adj Close 컬럼 중 하나라도 있는지 확인
    price_col = None
    if "Close" in stock_data.columns:
        price_col = "Close"
    elif "Adj Close" in stock_data.columns:
        price_col = "Adj Close"

    if price_col is None:
        st.warning(f"⚠️ 'Close' 또는 'Adj Close' 컬럼이 없습니다. 현재 컬럼: {list(stock_data.columns)}")
    else:
        try:
            # 컬럼 존재할 때만 dropna 처리 (price_col 변수 사용)
            clean_data = stock_data.dropna(subset=[price_col]).reset_index()
            st.write(clean_data[[ "Date", price_col]].head())

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=clean_data["Date"],
                y=clean_data[price_col],
                mode="lines",
                name=price_col
            ))
            fig.update_layout(
                title=f"{stock_name} ({ticker}) 주가 차트",
                xaxis_title="날짜",
                yaxis_title="가격 (USD)",
                template="plotly_white",
                xaxis_rangeslider_visible=True
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"⚠️ 주가 차트 그리기 중 오류 발생: {e}")

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
    seen_titles = set()
    for article in news_items:
        title = article.get("title", "")
        description = article.get("description", "")
        if not title or title in seen_titles:
            continue
        seen_titles.add(title)

        st.markdown(f"### {title}")
        st.write(description or "📌 설명이 제공되지 않았습니다.")
        st.caption(f"🕒 {article.get('pubDate', '날짜 없음')}")
        st.markdown(f"[🔗 원문 보기]({article.get('link', '#')})")
        st.markdown("---")
