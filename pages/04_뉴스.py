import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
import datetime

st.title("📊 주가 그래프 테스트 (수정완료)")

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

# 날짜 선택 (기본: 최근 6개월)
end_date = datetime.date.today()
start_date = st.date_input("시작 날짜 선택", end_date - datetime.timedelta(days=365))

# 주가 데이터 가져오기
stock_data = yf.download(ticker, start=start_date, end=end_date)

if not stock_data.empty:
    # Close 보정
    if "Close" not in stock_data.columns and "Adj Close" in stock_data.columns:
        stock_data["Close"] = stock_data["Adj Close"]

    # NaN 제거
    stock_data = stock_data.dropna().reset_index()

    # 데이터 확인용 출력
    st.write("📋 불러온 데이터", stock_data.head())

    # 그래프
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=stock_data["Date"],
        y=stock_data["Close"],
        mode='lines+markers',   # 선 + 점 표시 (확실히 보이게)
        name='종가'
    ))
    fig.update_layout(
        title=f"{stock_name} ({ticker}) 주가 차트",
        xaxis_title="날짜",
        yaxis_title="가격",
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("📉 주가 데이터를 불러올 수 없습니다. 다른 날짜를 선택해 보세요.")
