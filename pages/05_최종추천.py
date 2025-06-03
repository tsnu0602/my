import streamlit as st
import openai
import requests
import yfinance as yf
from datetime import datetime, timedelta

# 🔐 API 키 불러오기
openai.api_key = st.secrets["openai_api_key"]
newsdata_key = st.secrets["newsdata_api_key"]

# 관심 종목 예시
STOCK_LIST = {
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "NVDA": "Nvidia",
    "GOOGL": "Alphabet",
    "AMZN": "Amazon"
}

def get_news(ticker):
    url = f"https://newsdata.io/api/1/news?apikey={newsdata_key}&q={ticker}&language=en&category=business"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return [f"- [{a['title']}]({a['link']})" for a in data.get("results", [])[:3]]
    except Exception as e:
        return [f"뉴스 로딩 실패: {e}"]

def get_gpt_analysis(ticker, news_list):
    news_text = "\n".join(news_list)
    prompt = f"""
    다음은 {ticker} 관련 최근 뉴스입니다:\n{news_text}
    이 정보를 바탕으로 {ticker} 종목에 대한 현재 투자 기회를 분석해 주세요.
    추천 여부와 이유를 포함해 투자 관점에서 300자 이상 설명해 주세요.
    """
    try:
        res = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return res.choices[0].message.content.strip()
    except Exception as e:
        return f"GPT 분석 실패: {e}"

def plot_stock(ticker):
    end = datetime.today()
    start = end - timedelta(days=365)
    df = yf.download(ticker, start=start, end=end)
    if df.empty:
        st.warning("주가 데이터를 불러올 수 없습니다.")
        return
    st.line_chart(df["Close"])

# Streamlit 페이지
st.title("📰 뉴스 기반 종목 추천")
selected = st.selectbox("📌 종목 선택", list(STOCK_LIST.keys()), format_func=lambda x: f"{x} - {STOCK_LIST[x]}")

with st.spinner("🔎 뉴스와 분석을 불러오는 중..."):
    news = get_news(selected)
    analysis = get_gpt_analysis(selected, news)

st.subheader(f"📈 {selected} 주가 차트")
plot_stock(selected)

st.subheader("🗞 관련 뉴스")
for item in news:
    st.markdown(item)

st.subheader("💡 GPT 투자 분석")
st.write(analysis)
