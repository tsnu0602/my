import streamlit as st
import openai
import yfinance as yf
import requests
import datetime
import plotly.graph_objs as go

# ✅ API 키 (Streamlit Cloud에서는 Settings → Secrets에 입력)
openai.api_key = st.secrets["openai_api_key"]
NEWS_API_KEY = st.secrets["newsdata_api_key"]

# ✅ 종목 선택
st.title("📊 종목 통합 분석: 주가, 뉴스, GPT 해석")
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
start_date = st.date_input("시작 날짜", end_date - datetime.timedelta(days=90))

# ✅ 주가 데이터 가져오기
with st.spinner("📈 주가 데이터를 불러오는 중..."):
    stock_data = yf.download(ticker, start=start_date, end=end_date)

if stock_data.empty:
    st.error("❌ 주가 데이터를 불러오지 못했습니다. 다른 날짜를 선택하거나 나중에 다시 시도하세요.")
else:
    # ✅ 주가 차트 출력
    st.subheader(f"{stock_name} 주가 차트")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data["Close"], mode='lines', name='종가'))
    fig.update_layout(title=f"{stock_name} ({ticker})", xaxis_title="날짜", yaxis_title="종가 (USD)")
    st.plotly_chart(fig)

# ✅ 뉴스 가져오기 함수
def get_news(query):
    url = f"https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}&q={query}&language=en"
    try:
        res = requests.get(url)
        if res.status_code == 200:
            return res.json().get("results", [])
        else:
            st.error(f"뉴스 로딩 실패: {res.status_code}")
            return []
    except Exception as e:
        st.error(f"뉴스 요청 오류: {e}")
        return []

# ✅ GPT 분석 함수 (openai>=1.0.0 호환)
def analyze_with_gpt(title, description):
    prompt = f"""
    다음은 {stock_name}에 대한 뉴스입니다.

    제목: {title}
    내용: {description}

    이 뉴스가 주가에 어떤 영향을 줄 수 있을지 300자 이상으로 분석하고, 투자자가 참고해야 할 요점을 알려주세요.
    """

    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "당신은 금융 및 주식 시장 분석 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ GPT 분석 실패: {e}"

# ✅ 뉴스 + GPT 분석 출력
st.subheader("📰 관련 뉴스 및 GPT 분석")
news_items = get_news(stock_name)

if news_items:
    for article in news_items[:3]:
        st.markdown(f"#### {article.get('title', '제목 없음')}")
        st.write(article.get("description", "설명 없음"))
        st.caption(f"🕒 {article.get('pubDate', '날짜 없음')}")
        with st.spinner("GPT가 분석 중입니다..."):
            result = analyze_with_gpt(article.get("title", ""), article.get("description", ""))
        st.success(result)
        st.markdown("---")
else:
    st.warning("📭 관련 뉴스를 찾을 수 없습니다.")
