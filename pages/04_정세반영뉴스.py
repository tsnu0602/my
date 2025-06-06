import streamlit as st
import openai
import yfinance as yf
import requests
import datetime
import plotly.graph_objs as go

# 🔐 API 키
openai.api_key = st.secrets["openai_api_key"]
NEWS_API_KEY = st.secrets["newsdata_api_key"]

# 📈 종목 선택
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

# 📅 날짜 선택
end_date = datetime.date.today()
start_date = st.date_input("시작 날짜 선택", end_date - datetime.timedelta(days=90))

# 📊 주가 데이터 가져오기
st.subheader("📈 주가 차트")
try:
    stock_data = yf.download(ticker, start=start_date, end=end_date)

    # ✅ 데이터 확인 및 처리
    if stock_data.empty:
        st.warning("❗ 주가 데이터를 가져올 수 없습니다. 날짜 범위를 다시 선택해 주세요.")
    elif "Close" not in stock_data.columns:
        st.warning("❗ 'Close' 열이 존재하지 않습니다. 주가 데이터를 불러오지 못했습니다.")
    else:
        stock_data = stock_data.dropna(subset=["Close"])
        stock_data.reset_index(inplace=True)

        # ✅ 차트 그리기
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=stock_data["Date"], y=stock_data["Close"], mode="lines", name="종가"))
        fig.update_layout(title=f"{stock_name} ({ticker}) 주가 차트", xaxis_title="날짜", yaxis_title="가격")
        st.plotly_chart(fig)
except Exception as e:
    st.error(f"🚨 주가 데이터 오류: {e}")
