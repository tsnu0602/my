import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
import datetime

st.title("📊 주가 그래프 테스트 (수정판)")

# 종목 선택
stock_map = {
    "Apple": "AAPL",
    "Tesla": "TSLA",
    "Amazon": "AMZN",
    "Google": "GOOGL",
    "Microsoft": "MSFT"
}
stock_name = st.selectbox("분석할 종목을 선택하세요", list(stock_map.keys()))
ticker = stock_map[stock_name]

# 날짜 선택 (기본: 최근 180일)
end_date = datetime.date.today()
start_date = st.date_input("시작 날짜 선택", end_date - datetime.timedelta(days=180))

# 주가 데이터 가져오기
stock_data = yf.download(ticker, start=start_date, end=end_date)

if not stock_data.empty:
    # Close 컬럼 보정
    if "Close" not in stock_data.columns and "Adj Close" in stock_data.columns:
        stock_data["Close"] = stock_data["Adj Close"]

    # NaN 제거 + 인덱스 초기화
    stock_data = stock_data.dropna().reset_index()

    # 주가 차트 출력
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=stock_data["Date"], y=stock_data['Close'], mode='lines', name='종가'))
    fig.update_layout(title=f"{stock_name} ({ticker}) 주가 차트", xaxis_title="날짜", yaxis_title="가격")
    st.plotly_chart(fig)
else:
    st.error("📉 주가 데이터를 불러올 수 없습니다. 다른 날짜를 선택해 보세요.")
