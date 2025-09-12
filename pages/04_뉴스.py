import streamlit as st
import datetime
import requests
import yfinance as yf
import plotly.graph_objs as go

# OpenAI import 부분은 옵션으로 넣음 (뉴스 분석이 필요할 때 쓸 경우)
try:
    import openai
    OPENAI_AVAILABLE = True
    openai.api_key = st.secrets.get("openai_api_key", "")
except ImportError:
    OPENAI_AVAILABLE = False

# NEWSDATA API 키 불러오기
NEWS_API_KEY = st.secrets.get("newsdata_api_key", "")

# 앱 제목
st.set_page_config(page_title="뉴스 + 주가 + 분석", layout="wide")
st.title("📊 주가 + 뉴스 통합 분석")

# 종목 선택
stock_map = {
    "Apple": "AAPL",
    "Tesla": "TSLA",
    "Amazon": "AMZN",
    "Google": "GOOGL",
    "Microsoft": "MSFT"
}
stock_name = st.selectbox("분석할 종목 선택", list(stock_map.keys()))
ticker = stock_map.get(stock_name, "")

# 날짜 선택
end_date = datetime.date.today()
start_date = st.date_input("시작 날짜", end_date - datetime.timedelta(days=90))

# --- 주가 데이터 가져오기 및 차트 그리기 ---
st.subheader("📈 주가 차트")

stock_data = None
try:
    stock_data = yf.download(ticker, start=start_date, end=end_date)
except Exception as e:
    st.error(f"주가 데이터 불러오기 실패: {e}")

if stock_data is None or stock_data.empty:
    st.warning("❗ 주가 데이터가 없습니다. 날짜 또는 종목을 확인해 주세요.")
else:
    # 컬럼명 출력해 디버깅
    st.write("컬럼들:", stock_data.columns.tolist())

    # 'Close' 컬럼 없으면 'Adj Close'를 복사해서 사용
    if "Close" not in stock_data.columns and "Adj Close" in stock_data.columns:
        stock_data["Close"] = stock_data["Adj Close"]
    if "Close" not in stock_data.columns:
        st.warning("⚠️ 'Close' 컬럼이 존재하지 않아서 그래프를 그릴 수 없습니다.")
        st.dataframe(stock_data.head())
    else:
        stock_data = stock_data.dropna(subset=["Close"]).reset_index()
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=stock_data["Date"],
            y=stock_data["Close"],
            mode="lines",
            name="종가"
        ))
        fig.update_layout(
            title=f"{stock_name} ({ticker}) 주가 차트",
            xaxis_title="날짜",
            yaxis_title="가격",
            template="plotly_white",
            xaxis_rangeslider_visible=True
        )
        st.plotly_chart(fig, use_container_width=True)

# --- 뉴스 불러오기 함수 ---
def fetch_news(query="Apple", language="en"):
    if not NEWS_API_KEY:
        st.error("뉴스 API 키가 설정되어 있지 않습니다.")
        return []
    url = f"https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}&q={query}&language={language}"
    try:
        res = requests.get(url)
        if res.status_code != 200:
            st.error(f"뉴스 API 오류: {res.status_code}")
            return []
        data = res.json()
        results = data.get("results", [])
        return results
    except Exception as e:
        st.error(f"뉴스 불러오는 중 오류: {e}")
        return []

# --- 뉴스 & (선택적) GPT 분석 출력 ---
st.subheader("📰 뉴스 & 분석")

news_items = fetch_news(query=stock_name)

if not news_items:
    st.info("관련 뉴스가 없습니다.")
else:
    seen_titles = set()
    for article in news_items[:5]:
        title = article.get("title", "")
        if not title:
            continue
        if title in seen_titles:
            continue
        seen_titles.add(title)

        st.markdown(f"### {title}")
        st.write(article.get("description", "설명 없음"))
        st.caption(f"🕒 {article.get('pubDate', '날짜 없음')}")
        st.markdown(f"[🔗 원문 보기]({article.get('link', '#')})")

        # GPT 분석 부분은 모듈이 설치되어 있고 키가 설정된 경우만 실행
        if OPENAI_AVAILABLE and openai.api_key:
            with st.spinner("🤖 GPT 분석 중..."):
                prompt = f"""
                다음은 {stock_name} 관련 뉴스입니다.

                제목: {title}
                내용: {article.get('description', '')}

                이 뉴스가 {stock_name} 주가에 미칠 영향과 향후 투자 전략을 최소 300자 이상으로 작성해 주세요.
                """
                try:
                    client = openai.OpenAI(api_key=openai.api_key)
                    response = client.chat.completions.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": "당신은 금융 분석가입니다."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7
                    )
                    analysis = response.choices[0].message.content.strip()
                    st.success(analysis)
                except Exception as e:
                    st.error(f"GPT 분석 실패: {e}")
        else:
            st.info("GPT 분석을 위해 OpenAI 모듈 또는 API 키가 제대로 설정되어야 합니다.")
        st.markdown("---")
