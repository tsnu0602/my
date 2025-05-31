import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf

st.set_page_config(layout="wide")
st.title("Top 50 시가총액 종목의 시가총액 변화")

# 샘플로 S&P 500 상위 50개 종목 (티커 수동 지정 or 크롤링 가능)
top_50_tickers = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B", "UNH", "JNJ",
    "V", "XOM", "PG", "MA", "LLY", "AVGO", "HD", "MRK", "PEP", "ABBV",
    "COST", "KO", "BAC", "ADBE", "WMT", "CSCO", "PFE", "TMO", "ACN", "MCD",
    "CRM", "ORCL", "INTC", "DHR", "ABT", "NKE", "VZ", "TXN", "WFC", "QCOM",
    "MS", "LIN", "AMGN", "NEE", "UPS", "PM", "RTX", "CVX", "BMY", "IBM"
]

# 기간 선택
period = st.selectbox("기간 선택", ["1mo", "3mo", "6mo", "1y", "2y"], index=2)

# 시가총액 데이터를 가져옴
@st.cache_data
def get_market_caps(tickers, period="6mo"):
    data = {}
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        if not hist.empty:
            try:
                shares = stock.info.get("sharesOutstanding", None)
                if shares:
                    hist["Market Cap"] = hist["Close"] * shares
                    data[ticker] = hist[["Market Cap"]]
            except Exception as e:
                print(f"Error for {ticker}: {e}")
    return data

market_caps = get_market_caps(top_50_tickers, period)

# 시각화
st.subheader(f"기간별 시가총액 변화 ({period})")
selected = st.multiselect("종목 선택", options=top_50_tickers, default=top_50_tickers[:10])

if selected:
    df_plot = pd.DataFrame()
    for ticker in selected:
        if ticker in market_caps:
            temp = market_caps[ticker].copy()
            temp["Date"] = temp.index
            temp["Ticker"] = ticker
            df_plot = pd.concat([df_plot, temp])

    fig = px.line(
        df_plot,
        x="Date",
        y="Market Cap",
        color="Ticker",
        title="시가총액 변화",
        labels={"Market Cap": "시가총액 (USD)"}
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("하나 이상의 종목을 선택하세요.")
