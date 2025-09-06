import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
import datetime

# 페이지 레이아웃을 넓게 설정
st.set_page_config(layout="wide")

# 종목 선택
stocks = {"Apple": "AAPL", "Tesla": "TSLA", "Amazon": "AMZN"}
stock_name = st.selectbox("종목 선택", list(stocks.keys()))
ticker = stocks[stock_name]

# 날짜 선택
end_date = datetime.date.today()
start_date = st.date_input("시작 날짜", end_date - datetime.timedelta(days=90))

if start_date >= end_date:
    st.error("시작 날짜는 종료 날짜보다 이전이어야 합니다.")
else:
    # 주가 데이터 로드
    @st.cache_data
    def load_data(ticker, start, end):
        df = yf.download(ticker, start=start, end=end, auto_adjust=True, threads=False)
        return df

    df = load_data(ticker, start_date, end_date)

    if df.empty:
        st.warning("주가 데이터가 없습니다.")
    else:
        # 'Close' 컬럼이 없으면 'Adj Close'로 대체
        price_col = "Close" if "Close" in df.columns else "Adj Close"

        # 결측치 제거
        df = df.dropna(subset=[price_col]).reset_index()

        # Plotly 차트 생성
        fig = go.Figure(go.Scatter(x=df["Date"], y=df[price_col], mode="lines", name=stock_name))
        fig.update_layout(
            title=f"{stock_name} ({ticker}) 주가 차트",
            xaxis_title="날짜",
            yaxis_title="가격 (USD)",
            template="plotly_white",
            xaxis_rangeslider_visible=True
        )

        # 차트 표시
        st.plotly_chart(fig, use_container_width=True)
