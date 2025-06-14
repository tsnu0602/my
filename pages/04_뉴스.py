import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import datetime

st.set_page_config(page_title="📈 주가 차트", layout="centered")

st.title("📈 종목 주가 차트")

# 종목 선택
stocks = {
    "Apple": "AAPL",
    "Tesla": "TSLA",
    "Amazon": "AMZN",
    "Google": "GOOGL",
    "Microsoft": "MSFT"
}
selected = st.selectbox("종목 선택", list(stocks.keys()))
ticker = stocks[selected]

# 날짜 선택
end = datetime.date.today()
start = st.date_input("시작 날짜", end - datetime.timedelta(days=90))

# 데이터 불러오기
with st.spinner("주가 데이터 불러오는 중..."):
    data = yf.download(ticker, start=start, end=end)

# 데이터 확인 및 처리
if data.empty:
    st.error("❌ 주가 데이터를 불러오지 못했습니다. 날짜 범위나 종목을 확인하세요.")
else:
    data = data.dropna(subset=["Close"])
    data.reset_index(inplace=True)  # datetime index를 칼럼으로 변경

    # 차트 생성
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], mode='lines', name='종가'))

    fig.update_layout(
        title=f"{selected} ({ticker}) 주가 차트",
        xaxis_title="날짜",
        yaxis_title="가격 (USD)",
        xaxis_rangeslider_visible=True,
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)
