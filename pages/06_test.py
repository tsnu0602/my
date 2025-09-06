import streamlit as st
import requests
import yfinance as yf
import plotly.graph_objs as go
import datetime

# API 키 설정
NEWS_API_KEY = st.secrets.get("newsdata_api_key", "")

# 기본 설정
st.set_page_config(page_title="📈 종목 분석 대시보드", layout="centered")
st.title("📊 주가 + 뉴스 통합 대시보드")

# 종목 선택
stocks = {
    "Apple": "AAPL",
    "Tesla": "TSLA",
    "Amazon": "AMZN",
    "Google": "GOOGL",
    "Microsoft": "MSFT"
}
stock_name = st.selectbox("🔎 분석할 종목을 선택하세요", list(stocks.keys()))
ticker = stocks[stock_name]

# 날짜 선택
today = datetime.date.today()
default_start = today - datetime.timedelta(days=90)
start_date = st.date_input("시작 날짜", default_start, max_value=today - datetime.timedelta(days=1))

# 주가 데이터 불러오기
with st.spinner("📉 주가 데이터를 불러오는 중..."):
    try:
        stock_data = yf.download(ticker, start=start_date, end=today)
    except Exception as e:
        st.error(f"❌ 주가 데이터를 불러오는 데 실패했습니다: {e}")
        stock_data = None

st.subheader(f"💹 {stock_name} 주가 차트")

if stock_data is None or stock_data.empty:
    st.warning("📭 주가 데이터가 없습니다.")
else:
    # 'Close' 또는 'Adj Close' 컬럼 체크
    price_col = None
    if "Close" in stock_data.columns:
        price_col = "Close"
    elif "Adj Close" in stock_data.columns:
        price_col = "Adj Close"

    if price_col is None:
        st.warning(f"⚠️ 주가 데이터에 'Close' 또는 'Adj Close' 컬럼이 없습니다. 현재 컬럼: {list(stock_data.columns)}")
    else:
        # 컬럼이 실제로 존재하는지 재확인
        if price_col in stock_data.columns:
            # 결측치 제거 - 존재하면 호출, 없으면 안 함
            stock_data = stock_data.dropna(subset=[price_col])
        else:
            st.warning(f"⚠️ '{price_col}' 컬럼이 데이터에 없습니다.")
        
        if stock_data.empty:
            st.warning("📭 주가 데이터가 결측치 제거 후 없습니다.")
        else:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data[price_col], mode="lines", name=price_col))
            fig.update_layout(
                title=f"{stock_name} ({ticker}) 주가 차트",
                xaxis_title="날짜",
                yaxis_title="가격 (USD)",
                template="plotly_white",
                xaxis_rangeslider_visible=True
            )
            st.plotly_chart(fig)

# 뉴스 불러오기 함수
def get_news(query="Apple", language="en"):
    if not NEWS_API_KEY:
        st.error("❌ 뉴스 API 키가 설정되지 않았습니다.")
        return []
    url = f"https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}&q={query}&language={language}"
    try:
        res = requests.get(url, timeout=10)
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
        title = article.get("title", "제목 없음")
        if not title or title in seen_titles:
            continue
        seen_titles.add(title)

        description = article.get("description", "설명이 제공되지 않았습니다.")
        pub_date = article.get("pubDate", "날짜 없음")
        link = article.get("link", "#")

        st.markdown(f"### {title}")
        st.write(description)
        st.caption(f"🕒 {pub_date}")
        st.markdown(f"[🔗 원문 보기]({link})")
        st.markdown("---")
