import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
import datetime

st.title("📈 주가 그래프 안정화 버전")

# 종목 선택
stocks = {"Apple": "AAPL", "Tesla": "TSLA", "Amazon": "AMZN", "Google": "GOOGL", "Microsoft": "MSFT"}
stock_name = st.selectbox("종목 선택", list(stocks.keys()))
ticker = stocks[stock_name]

# 날짜 선택 (최근 1년)
end_date = datetime.date.today()
start_date = st.date_input("시작 날짜", end_date - datetime.timedelta(days=365))

# 데이터 가져오기
stock_data = yf.download(ticker, start=start_date, end=end_date)

# 컬럼 확인
st.write("데이터 컬럼:", stock_data.columns)

if stock_data.empty:
    st.error("주가 데이터가 없습니다. 날짜 범위를 늘려보세요.")
else:
    # Close 컬럼 존재 여부 체크
    if "Close" in stock_data.columns:
        price_col = "Close"
    elif "Adj Close" in stock_data.columns:
        price_col = "Adj Close"
    else:
        st.error("Close 컬럼과 Adj Close 컬럼 모두 존재하지 않습니다.")
        st.stop()

    # NaN 제거 + 인덱스 초기화
    stock_data = stock_data.dropna(subset=[price_col]).reset_index()
    st.write("데이터 예시:", stock_data.head())

    # 그래프 그리기
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=stock_data.index,
        y=stock_data[price_col],
        mode="lines+markers",
        name="종가"
    ))
    fig.update_layout(
        title=f"{stock_name} ({ticker}) 주가 차트",
        xaxis_title="날짜",
        yaxis_title="가격"
    )
    st.plotly_chart(fig, use_container_width=True)
