import streamlit as st
import openai
import requests
import yfinance as yf
import plotly.graph_objs as go
import datetime

# ✅ API 키 로딩
openai.api_key = st.secrets["openai_api_key"]
NEWS_API_KEY = st.secrets["newsdata_api_key"]

# ✅ 종목 선택
st.set_page_config(page_title="📈 종목 분석 통합 대시보드", layout="centered")
st.title("📊 주가 + 뉴스 + GPT 분석")

stocks = {
    "Apple": "AAPL",
    "Tesla": "TSLA",
    "Amazon": "AMZN",
    "Google": "GOOGL",
    "Microsoft": "MSFT"
}
stock_name = st.selectbox("분석할 종목 선택", list(stocks.keys()))
ticker = stocks[stock_name]

# ✅ 날짜 선택
end_date = datetime.date.today()
start_date = st.date_input("시작 날짜", end_date - datetime.timedelta(days=90))

# ✅ 주가 데이터
with st.spinner("📉 주가 데이터 불러오는 중..."):
    stock_data = yf.download(ticker, start=start_date, end=end_date)

if stock_data.empty or "Close" not in stock_data.columns:
    st.error("❌ 유효한 주가 데이터를 불러올 수 없습니다.")
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

# ✅ 뉴스 함수
def get_news(query="Apple", language="en", country="us"):
    url = f"https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}&q={query}&language={language}&country={country}"
    try:
        res = requests.get(url)
        if res.status_code != 200:
            st.error(f"❌ 뉴스 API 오류: {res.status_code} - {res.text}")
            return []
        return res.json().get("results", [])
    except Exception as e:
        st.error(f"⚠️ 뉴스 요청 중 오류 발생: {e}")
        return []

# ✅ GPT 분석 함수
def gpt_analysis(title, content):
    prompt = f"""
    다음은 {stock_name} 관련 뉴스입니다.

    제목: {title}
    내용: {content}

    이 뉴스가 주식에 어떤 영향을 줄 수 있을지 분석하고, 향후 투자 전략에 대해 최소 300자 이상 서술해 주세요.
    """
    try:
        client = openai.OpenAI(api_key=openai.api_key)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "당신은 숙련된 금융 분석가입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"GPT 분석 실패: {e}"

# ✅ 뉴스 & 분석
st.subheader(f"📰 {stock_name} 관련 뉴스 & GPT 분석")

news_items = get_news(query=f"{stock_name} stock")
if not news_items:
    st.warning("📭 관련 뉴스가 없습니다.")
else:
    seen_titles = set()
    for article in news_items:
        title = article.get("title", "")
        if title in seen_titles:
            continue
        seen_titles.add(title)

        st.markdown(f"### {title}")
        st.write(article.get("description", "내용 없음"))
        st.markdown(f"[🔗 기사 보기]({article.get('link', '#')})")
        st.caption(f"🕒 {article.get('pubDate', '날짜 없음')}")
        
        with st.spinner("🤖 GPT 분석 중..."):
            analysis = gpt_analysis(title, article.get("description", ""))
            st.success(analysis)
        st.markdown("---")
