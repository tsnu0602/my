import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
import datetime

st.title("📈 주가 그래프")

# 종목 선택
stock_map = {
    "Apple": "AAPL",
    "Tesla": "TSLA",
    "Amazon": "AMZN",
    "Google": "GOOGL",
    "Microsoft": "MSFT"
}
stock_name = st.selectbox("종목 선택", list(stock_map.keys()))
ticker = stock_map[stock_name]

# 날짜 범위: 최근 1년
end_date = datetime.date.today()
start_date = st.date_input("시작 날짜 선택", end_date - datetime.timedelta(days=365))

# 데이터 가져오기
stock_data = yf.download(ticker, start=start_date, end=end_date)
if stock_data.empty:
    st.error("데이터 없음. 날짜를 늘려보세요.")
else:
    if "Close" not in stock_data.columns and "Adj Close" in stock_data.columns:
        stock_data["Close"] = stock_data["Adj Close"]

    stock_data = stock_data.dropna(subset=["Close"]).reset_index()
    st.write("총 데이터 개수:", len(stock_data))
    st.write(stock_data.head())

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=stock_data["Date"],
        y=stock_data["Close"],
        mode="lines+markers",
        name="종가"
    ))
    fig.update_layout(title=f"{stock_name} ({ticker}) 주가 차트", xaxis_title="날짜", yaxis_title="가격")
    st.plotly_chart(fig, use_container_width=True)
