import streamlit as st
import openai
import yfinance as yf
import requests
import datetime
import plotly.graph_objs as go

# ✅ API 키 불러오기
openai.api_key = st.secrets["openai_api_key"]
NEWS_API_KEY = st.secrets["newsdata_api_key"]

# ✅ 종목 선택
st.title("📊 종목별 주가, 뉴스 및 GPT 분석")
stock_map = {
    "Apple": "AAPL",
    "Tesla": "TSLA",
    "Amazon": "AMZN",
    "Google": "GOOGL",
    "Microsoft": "MSFT"
}
stock_name = st.selectbox("분석할 종목을 선택하세요", list(stock_map.keys()))
ticker = stock_map[stock_name]

# ✅ 날짜 선택
end_date = datetime.date.today()
start_date = st.date_input("시작 날짜 선택", end_date - datetime.timedelta(days=90))

# ✅ 주가 데이터 가져오기 (예외 및 빈 데이터 처리 포함)
try:
    stock_data = yf.download(ticker, start=start_date, end=end_date)

    if stock_data.empty:
        st.warning("⚠️ 주가 데이터를 불러오지 못했습니다. 날짜 범위나 네트워크를 확인하세요.")
        fig = go.Figure()
        fig.update_layout(title="❌ 주가 데이터 없음", xaxis_title="날짜", yaxis_title="종가")
        st.plotly_chart(fig)
    else:
        stock_data = stock_data.dropna(subset=["Close"])
        stock_data.reset_index(inplace=True)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=stock_data["Date"], y=stock_data["Close"], mode='lines', name='종가'))
        fig.update_layout(title=f"{stock_name} ({ticker}) 주가 차트", xaxis_title="날짜", yaxis_title="종가")
        st.plotly_chart(fig)
except Exception as e:
    st.error(f"📉 주가 데이터를 불러오는 중 오류 발생: {e}")

# ✅ 뉴스 불러오기 함수
def fetch_news(keyword):
    url = f"https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}&q={keyword}&language=en"
    try:
        response = requests.get(url)
        return response.json().get("results", [])
    except Exception as e:
        st.error(f"뉴스 로딩 오류: {e}")
        return []

# ✅ 뉴스 및 GPT 분석
st.subheader("📰 관련 뉴스 및 GPT 분석")

news_list = fetch_news(stock_name)
if news_list:
    for news in news_list[:3]:
        st.markdown(f"#### {news['title']}")
        st.write(news.get("description", "설명 없음"))
        st.caption(news.get("pubDate", "날짜 정보 없음"))

        # GPT 분석
        prompt = f"""
        다음은 {stock_name}에 대한 뉴스 기사입니다.

        제목: {news['title']}
        내용: {news.get('description', '')}

        이 뉴스가 주가에 어떤 영향을 줄지 예측하고, 투자자에게 의미 있는 분석을 300자 이상으로 작성하세요.
        """
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "당신은 금융 시장 분석가입니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            analysis = completion.choices[0].message["content"].strip()
            st.success(analysis)
        except Exception as e:
            st.error(f"GPT 분석 오류: {e}")
        st.markdown("---")
else:
    st.warning("관련 뉴스를 찾을 수 없습니다.")
