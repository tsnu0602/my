import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
import datetime

st.title("주가 차트 테스트")

stocks = {"Apple": "AAPL", "Tesla": "TSLA"}
stock_name = st.selectbox("종목 선택", list(stocks.keys()))
ticker = stocks[stock_name]

end_date = datetime.date.today()
start_date = st.date_input("시작 날짜", end_date - datetime.timedelta(days=90))

if start_date >= end_date:
    st.error("시작 날짜는 종료 날짜보다 이전이어야 합니다.")
else:
    @st.cache_data
    def load_data(ticker, start, end):
        df = yf.download(ticker, start=start, end=end, auto_adjust=True, threads=False)
        return df

    df = load_data(ticker, start_date, end_date)
    if df.empty:
        st.warning("주가 데이터가 없습니다.")
    else:
        st.write(df.head())
        price_col = "Close" if "Close" in df.columns else ("Adj Close" if "Adj Close" in df.columns else None)
        if price_col is None:
            st.error("Close 또는 Adj Close 컬럼이 없습니다.")
        else:
            df = df.reset_index()
            fig = go.Figure(go.Scatter(x=df["Date"], y=df[price_col], mode="lines"))
            fig.update_layout(title=f"{stock_name} 주가", xaxis_title="날짜", yaxis_title="가격")
            st.plotly_chart(fig)
