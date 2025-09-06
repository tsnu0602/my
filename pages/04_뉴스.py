import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
import requests
import datetime

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
end_date = datetime.date.today()
start_date = st.date_input("시작 날짜 선택", end_date - datetime.timedelta(days=90))

# 주가 데이터 로드
@st.cache_data
def load_stock_data(ticker, start, end):
    try:
        data = yf.download(ticker, start=start, end=end, auto_adjust=True)
        return data
    except Exception as e:
        st.error(f"주가 데이터 로드 실패: {e}")
        return None

stock_data = load_stock_data(ticker, start_date, end_date)

# 주가 차트 표시
if stock_data is not None and not stock_data.empty:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['Close'], mode='lines', name='종가'))
    fig.update_layout(title=f"{stock_name} ({ticker}) 주가 차트", xaxis_title="날짜", yaxis_title="가격 (USD)")
    st.plotly_chart(fig)
else:
    st.warning("주가 데이터를 불러오지 못했습니다.")

# 뉴스 데이터 로드
NEWS_API_KEY = st.secrets["newsdata_api_key"]

def get_news(query):
    url = f"https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}&q={query}&language=en"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get("results", [])
        else:
            st.error(f"뉴스 API 호출 실패: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"뉴스 데이터 로드 실패: {e}")
        return []

news_items = get_news(stock_name)

# 뉴스 표시
if news_items:
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
else:
    st.info("관련 뉴스가 없습니다.")
