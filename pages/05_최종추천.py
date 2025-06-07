import streamlit as st
import datetime
import yfinance as yf
import plotly.graph_objects as go
import requests
from openai import OpenAI

# 🔐 API 키 가져오기 (secrets.toml에 저장된 키)
OPENAI_API_KEY = st.secrets["openai_api_key"]
NEWSDATA_API_KEY = st.secrets["newsdata_api_key"]

# ✅ OpenAI 객체 생성
client = OpenAI(api_key=OPENAI_API_KEY)

# 🔘 종목 선택
st.title("📊 종목 뉴스 & 주가 분석 with GPT")
stock_map = {
    "Apple": "AAPL",
    "Tesla": "TSLA",
    "Amazon": "AMZN",
    "Google": "GOOGL",
    "Microsoft": "MSFT"
}
stock_name = st.selectbox("분석할 종목을 선택하세요", list(stock_map.keys()))
ticker = stock_map[stock_name]

# 📆 날짜 범위 설정
end_date = datetime.date.today()
start_date = st.date_input("시작 날짜", value=end_date - datetime.timedelta(days=90))

# 📈 주가 데이터 불러오기
try:
    data = yf.download(ticker, start=start_date, end=end_date)
    if data.empty:
        st.warning("❗ 주가 데이터를 불러올 수 없습니다. 날짜를 조정하거나 나중에 시도해보세요.")
    else:
        data = data.dropna(subset=["Close"])
        data.reset_index(inplace=True)

        # 📊 Plotly 그래프
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data["Date"], y=data["Close"], mode='lines', name='종가'))
        fig.update_layout(title=f"{stock_name} 주가 추이", xaxis_title="날짜", yaxis_title="종가")
        st.plotly_chart(fig)
except Exception as e:
    st.error(f"📉 주가 데이터 오류: {e}")

# 📰 뉴스 불러오기 함수
def fetch_news(query):
    url = f"https://newsdata.io/api/1/news?apikey={NEWSDATA_API_KEY}&q={query}&language=en"
    try:
        response = requests.get(url)
        news = response.json()
        return news.get("results", [])
    except Exception as e:
        st.error(f"뉴스 불러오기 실패: {e}")
        return []

# 🔍 뉴스 분석
st.subheader("📰 뉴스 기반 GPT 분석")
news_items = fetch_news(stock_name)

if not news_items:
    st.warning("관련 뉴스를 찾을 수 없습니다.")
else:
    for article in news_items[:3]:
        title = article.get("title", "")
        desc = article.get("description", "")
        pub_date = article.get("pubDate", "")

        st.markdown(f"### 🗞 {title}")
        st.caption(pub_date)
        st.write(desc)

        # GPT 분석
        prompt = f"""
        다음은 {stock_name}에 대한 뉴스 기사입니다.

        제목: {title}
        내용: {desc}

        이 뉴스가 {stock_name}의 주가에 미칠 영향을 분석하고,
        투자자에게 도움이 될 만한 분석을 300자 이상으로 작성하세요.
        """

        try:
            completion = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "당신은 금융 시장 분석가입니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            analysis = completion.choices[0].message.content.strip()
            st.success(analysis)
        except Exception as e:
            st.error(f"GPT 분석 실패: {e}")
        st.markdown("---")
