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
            print(f"Error fetching data for {ticker}: {e}")
    return data

market_caps = get_market_caps(top_50_tickers, start_date, end_date)

st.subheader("📈 시가총액 변화 차트")
selected = st.multiselect("종목 선택", options=top_50_tickers, default=top_50_tickers[:10])

if selected:
    df_plot = pd.DataFrame()
    for ticker in selected:
        if ticker in market_caps:
            temp = market_caps[ticker].copy()
            temp["Date"] = temp.index
            temp["Ticker"] = ticker
            df_plot = pd.concat([df_plot, temp])

    if not df_plot.empty:
        fig = px.line(
            df_plot,
            x="Date",
            y="Market Cap",
            color="Ticker",
            title=f"{start_date} ~ {end_date} 시가총액 변화",
            labels={"Market Cap": "시가총액 (USD)"}
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("선택한 기간에 데이터가 없습니다.")
else:
    st.warning("하나 이상의 종목을 선택하세요.")

st.subheader("📊 고평가/저평가 분석")

analysis_results = []

for ticker in top_50_tickers:
    if ticker in market_caps:
        df = market_caps[ticker]
        if not df.empty:
            avg_cap = df["Market Cap"].mean()
            current_cap = df["Market Cap"].iloc[-1]
            change_ratio = (current_cap - avg_cap) / avg_cap

            if change_ratio > 0.3:
                status = "고평가"
                reason = f"현재 시가총액이 5년 평균보다 {change_ratio:.0%} 높음"
            elif change_ratio < -0.3:
                status = "저평가"
                reason = f"현재 시가총액이 5년 평균보다 {abs(change_ratio):.0%} 낮음"
            else:
                status = "적정"
                reason = "현재 시가총액은 평균과 유사함"

            analysis_results.append({
                "종목": ticker,
                "상태": status,
                "현재 시가총액": f"${current_cap:,.0f}",
                "5년 평균": f"${avg_cap:,.0f}",
                "변동률": f"{change_ratio:.0%}",
                "판단 근거": reason
            })

if analysis_results:
    df_analysis = pd.DataFrame(analysis_results)
    st.dataframe(df_analysis, use_container_width=True)
else:
    st.warning("데이터가 부족하여 분석할 수 없습니다.")
