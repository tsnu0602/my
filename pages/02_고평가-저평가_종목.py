import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf
from datetime import date

st.set_page_config(layout="wide")
st.title("Top 50 시가총액 종목 분석")

top_50_tickers = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B", "UNH", "JNJ",
    "V", "XOM", "PG", "MA", "LLY", "AVGO", "HD", "MRK", "PEP", "ABBV",
    "COST", "KO", "BAC", "ADBE", "WMT", "CSCO", "PFE", "TMO", "ACN", "MCD",
    "CRM", "ORCL", "INTC", "DHR", "ABT", "NKE", "VZ", "TXN", "WFC", "QCOM",
    "MS", "LIN", "AMGN", "NEE", "UPS", "PM", "RTX", "CVX", "BMY", "IBM"
]

# 날짜 선택
st.sidebar.header("기간 설정")
start_date = st.sidebar.date_input("시작일", date.today().replace(year=date.today().year - 5))
end_date = st.sidebar.date_input("종료일", date.today())

if start_date >= end_date:
    st.sidebar.error("시작일은 종료일보다 이전이어야 합니다.")

# 시가총액 데이터 가져오기
@st.cache_data(show_spinner=True)
def get_market_caps(tickers, start, end):
    data = {}
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(start=start, end=end)
            shares = stock.info.get("sharesOutstanding", None)
            if shares and not hist.empty:
                hist["Market Cap"] = hist["Close"] * shares
                data[ticker] = hist[["Market Cap"]]
        except Exception as e:
            print(f"Error
