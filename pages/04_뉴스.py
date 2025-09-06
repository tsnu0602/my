import streamlit as st
import requests
import yfinance as yf
import plotly.graph_objs as go
import datetime

# === 기본 설정 ===
st.set_page_config(page_title="📈 종목 분석 대시보드", layout="centered")
st.title("📊 주가 + 뉴스 통합 대시보드")

# === 종목 선택 ===
stocks = {
    "Apple": "AAPL",
    "Tesla": "TSLA",
    "Amazon": "AMZN",
    "Google": "GOOGL",
    "Microsoft": "MSFT"
}
stock_name = st.selectbox("🔎 분석할 종목을 선택하세요", list(stocks.keys()))
ticker = stocks[stock_name]

# === 날짜 선택 ===
end_date = datetime.date.today()
start_date = st.date_input("시작 날짜 선택", end_date - datetime.timedelta(days=90))

# === yfinance에서 주가 데이터 로드 ===
@st.cache_data
def load_stock_data(ticker, start, end):
    try:
        data = yf.download(ticker, start=start, end=end, auto_adjust=True, threads=False)
        return data
    except Exception as e:
        st.error(f"❌ 주가 데이터 로드 실패: {e}")
        return None

stock_data = load_stock_data(ticker, start_date, end_date)

# === 주가 차트 그리기 ===
if stock_data is None or stock_data.empty:
    st.warning("⚠️ 주가 데이터를 불러오지 못했습니다.")
else:
    # 종가 컬럼 확인
    price_col = "Close" if "Close" in stock_data.columns else None
    if price_col is None:
        st.error("❌ 'Close' 컬럼이 없습니다.")
    else:
        stock_data = stock_data.reset_index()
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=stock_data["Date"],
            y=stock_data[price_col],
            mode="lines",
            name="종가"
        ))
        fig.update_layout(
            title=f"{stock_name} ({ticker}) 주가 차트",
            xaxis_title="날짜",
            yaxis_title="가격 (USD)",
            template="plotly_white",
            xaxis_rangeslider_visible=True
        )
        st.plotly_chart(fig)

# === 뉴스 API 설정 ===
NEWS_API_KEY = st.secrets["newsdata_api_key"]

def get_news(query, language="en", country="us"):
    url = f"https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}&q={query}&language={language}&country={country}"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            st.error(f"❌ 뉴스 API 오류: {response.status_code} - {response.text}")
            return []
        news_json = response.json()
        return news_json.get("results", [])
    except Exception as e:
        st.error(f"⚠️ 뉴스 요청 중 오류 발생: {e}")
        return []

# === 뉴스 출력 ===
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
