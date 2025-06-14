import streamlit as st
import yfinance as yf
import datetime
import plotly.graph_objs as go

st.title("📈 종목 주가 차트 확인")

stock_map = {
    "Apple": "AAPL",
    "Tesla": "TSLA",
    "Amazon": "AMZN",
    "Google": "GOOGL",
    "Microsoft": "MSFT"
}

stock_name = st.selectbox("종목을 선택하세요", list(stock_map.keys()))
ticker = stock_map[stock_name]

end_date = datetime.date.today()
start_date = st.date_input("시작 날짜 선택", end_date - datetime.timedelta(days=90))

with st.spinner(f"{ticker} 주가 데이터를 불러오는 중..."):
    df = yf.download(ticker, start=start_date, end=end_date)

if df.empty:
    st.error("❌ 선택한 기간에 주가 데이터가 없습니다.")
else:
    df = df.dropna(subset=["Close"])  # 종가 없는 데이터 제거
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode="lines", name="종가"))
    fig.update_layout(
        title=f"{stock_name} ({ticker}) 주가 차트",
        xaxis_title="날짜",
        yaxis_title="가격 (USD)",
        xaxis_rangeslider_visible=True
    )
    st.plotly_chart(fig)
