import streamlit as st
import openai
import requests
import yfinance as yf
import plotly.graph_objs as go
import datetime

# ✅ API 키 설정
openai.api_key = st.secrets["openai_api_key"]
NEWS_API_KEY = st.secrets["newsdata_api_key"]

# ✅ 기본 설정
st.set_page_config(page_title="📈 종목 분석 대시보드", layout="centered")
st.title("📊 주가 + 뉴스 + GPT 분석 통합")

# ✅ 종목 선택
stocks = {
    "Apple": "AAPL",
    "Tesla": "TSLA",
    "Amazon": "AMZN",
    "Google": "GOOGL",
    "Microsoft": "MSFT"
}
stock_name = st.selectbox("🔎 분석할 종목을 선택하세요", list(stocks.keys()))
ticker = stocks[stock_name]

# ✅ 날짜 선택
end_date = datetime.date.today()
start_date = st.date_input("시작 날짜", end_date - datetime.timedelta(days=90))

# ✅ 주가 데이터 불러오기
@st.cache_data
def load_stock_data(ticker, start_date, end_date):
    try:
        data = yf.download(ticker, start=start_date, end=end_date)
        if data.empty:
            st.warning("📭 주가 데이터가 없습니다.")
            return None
        return data
    except Exception as e:
        st.error(f"❌ 주가 데이터를 불러오는 데 실패했습니다: {e}")
        return None

stock_data = load_stock_data(ticker, start_date, end_date)

# ✅ 데이터 구조 확인
if stock_data is not None:
    st.write("📋 불러온 주가 데이터 미리보기:")
    st.write(stock_data.head())
    st.write("✅ 컬럼 목록:", stock_data.columns.tolist())

# ✅ 주가 차트 출력
if stock_data is not None and not stock_data.empty:
    # 종가 컬럼 확인
    price_col = None
    if "Close" in stock_data.columns:
        price_col = "Close"
    elif "Adj Close" in stock_data.columns:
        price_col = "Adj Close"

    if price_col is None:
        st.warning(f"⚠️ '{price_col}' 컬럼이 없습니다. 현재 컬럼: {stock_data.columns.tolist()}")
    else:
        stock_data = stock_data.dropna(subset=[price_col]).reset_index()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=stock_data["Date"], y=stock_data[price_col], mode="lines", name="종가"))
        fig.update_layout(
            title=f"{stock_name} ({ticker}) 주가 차트",
            xaxis_title="날짜",
            yaxis_title="가격 (USD)",
            template="plotly_white",
            xaxis_rangeslider_visible=True
        )
        st.plotly_chart(fig)

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

# ✅ 뉴스 섹션
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
