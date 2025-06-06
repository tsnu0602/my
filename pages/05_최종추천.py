import streamlit as st
import openai
import yfinance as yf
import requests
import datetime
import plotly.graph_objs as go

# API 키
openai.api_key = st.secrets["openai_api_key"]
NEWS_API_KEY = st.secrets["newsdata_api_key"]

st.title("📈 종목 선택 - 주가 + 뉴스 + GPT 분석")

stock_map = {
    "Apple": "AAPL",
    "Tesla": "TSLA",
    "Amazon": "AMZN",
    "Google": "GOOGL",
    "Microsoft": "MSFT"
}

stock_name = st.selectbox("분석할 종목을 선택하세요", list(stock_map.keys()))
ticker = stock_map[stock_name]

# 날짜 범위 선택
end_date = datetime.date.today()
start_date = st.date_input("시작 날짜", end_date - datetime.timedelta(days=90))

# 주가 데이터
data = yf.download(ticker, start=start_date, end=end_date)
if data.empty:
    st.error("❌ 주가 데이터를 불러오지 못했습니다. 날짜를 다시 선택해 주세요.")
else:
    st.subheader(f"📉 {stock_name} ({ticker}) 주가 차트")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='종가'))
    fig.update_layout(title=f"{ticker} 주가", xaxis_title="날짜", yaxis_title="가격")
    st.plotly_chart(fig)

# 뉴스 검색
st.subheader("📰 관련 뉴스 & GPT 분석")

def fetch_news(keyword):
    url = f"https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}&q={keyword}&language=en"
    try:
        r = requests.get(url)
        return r.json().get("results", [])
    except:
        return []

news_items = fetch_news(stock_name)

if not news_items:
    st.warning("뉴스를 불러오지 못했습니다.")
else:
    for news in news_items[:2]:  # 2개만 표시
        title = news.get("title", "제목 없음")
        desc = news.get("description", "설명 없음")
        st.markdown(f"#### 📰 {title}")
        st.caption(news.get("pubDate", "날짜 없음"))
        st.write(desc)

        # GPT 분석 요청
        prompt = f"""
다음 뉴스는 {stock_name} 관련 기사입니다.

제목: {title}
내용: {desc}

이 뉴스가 주가에 어떤 영향을 줄 수 있을지, 투자자 입장에서 의미 있는 분석을 300자 이상으로 제공해 주세요.
        """

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "당신은 전문 금융 애널리스트입니다."},
                    {"role": "user", "content": prompt}
                ]
            )
            answer = response["choices"][0]["message"]["content"]
            st.success(answer)
        except Exception as e:
            st.error(f"GPT 분석 실패: {e}")
