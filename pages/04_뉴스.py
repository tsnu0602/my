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
today = datetime.date.today()
default_start = today - datetime.timedelta(days=90)
start_date = st.date_input("시작 날짜", default_start, max_value=today - datetime.timedelta(days=1))

# ✅ 주가 데이터 불러오기
with st.spinner("📉 주가 데이터를 불러오는 중..."):
    try:
        stock_data = yf.download(ticker, start=start_date, end=today)
    except Exception as e:
        st.error(f"❌ 주가 데이터를 불러오는 데 실패했습니다: {e}")
        stock_data = None

# ✅ 주가 차트 출력
if stock_data is None or stock_data.empty:
    st.warning("📭 주가 데이터가 없습니다.")
elif "Close" not in stock_data.columns:
    st.warning(f"⚠️ 'Close' 컬럼이 없습니다. 현재 컬럼: {stock_data.columns.tolist()}")
else:
    stock_data = stock_data.dropna(subset=["Close"]).reset_index()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=stock_data["Date"], y=stock_data["Close"], mode="lines", name="종가"))
    fig.update_layout(
        title=f"{stock_name} ({ticker}) 주가 차트",
        xaxis_title="날짜",
        yaxis_title="가격 (USD)",
        template="plotly_white",
        xaxis_rangeslider_visible=True
    )
    st.plotly_chart(fig)

# ✅ 뉴스 불러오기 함수
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

# ✅ GPT 분석 함수
def gpt_analysis(title, content):
    if not content.strip():
        return "⚠️ 기사 내용이 부족하여 GPT 분석을 수행할 수 없습니다."

    prompt = f"""
    다음은 {stock_name}에 대한 뉴스 기사입니다.

    제목: {title}
    내용: {content}

    이 뉴스가 {stock_name} 주식에 미칠 영향과 향후 투자 전략을 최소 300자 이상으로 분석해 주세요.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "당신은 금융 전문 애널리스트입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ GPT 분석 실패: {e}"

# ✅ 뉴스 섹션
st.subheader(f"📰 {stock_name} 관련 뉴스 및 GPT 분석")

news_items = get_news(query=f"{stock_name} stock")
if not news_items:
    st.info("📭 관련 뉴스가 없습니다.")
else:
    seen_titles = set()
    for article in news_items:
        title = article.get("title", "제목 없음")
        description = article.get("description", "")
        if not title or title in seen_titles:
            continue
        seen_titles.add(title)

        st.markdown(f"### {title}")
        st.write(description or "📌 설명이 제공되지 않았습니다.")
        st.caption(f"🕒 {article.get('pubDate', '날짜 없음')}")
        st.markdown(f"[🔗 원문 보기]({article.get('link', '#')})")

        with st.spinner("🤖 GPT 분석 중..."):
            analysis = gpt_analysis(title, description)
        st.success(analysis)
        st.markdown("---")
