import streamlit as st
import yfinance as yf
import pandas as pd

symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]

def load_data():
    data = []
    for symbol in symbols:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        data.append({
            "종목": info.get("shortName", symbol),
            "티커": symbol,
            "PER": info.get("forwardPE", None),
            "EPS": info.get("trailingEps", None),
            "PBR": info.get("priceToBook", None),
            "ROE": info.get("returnOnEquity", None),
            "시가총액": info.get("marketCap", 0)
        })
    return pd.DataFrame(data)

page = st.sidebar.radio("페이지 선택", ["시가총액 분석", "성장가치 기업"])

if page == "시가총액 분석":
    st.write("시가총액 분석 페이지(미구현)")

else:
    st.title("성장가치 기업")
    df = load_data()

    # PER 30 이하 필터링
    growth_df = df[df["PER"].notnull() & (df["PER"] <= 30)]
    growth_df["ROE(%)"] = (growth_df["ROE"] * 100).round(2)
    st.dataframe(growth_df)
