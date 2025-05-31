import streamlit as st
import yfinance as yf
import pandas as pd

# 표시할 종목 리스트 (상위 50개 정도 예시)
symbols = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "BRK-B", "JPM", "V",
    "UNH", "HD", "MA", "PYPL", "BAC", "DIS", "ADBE", "CMCSA", "NFLX", "XOM",
    "PFE", "KO", "PEP", "CSCO", "T", "VZ", "ABT", "MRK", "CRM", "INTC",
    "WMT", "CVX", "ACN", "AVGO", "COST", "ORCL", "TXN", "NEE", "QCOM", "MDT",
    "LIN", "TMO", "UPS", "PM", "BA", "IBM", "MMM", "CAT", "RTX", "GE"
]

@st.cache_data(show_spinner=False)
def load_data():
    data = []
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            data.append({
                "종목": info.get("shortName", symbol),
                "티커": symbol,
                "시가총액": info.get("marketCap", 0),
                "PER": info.get("forwardPE", None),
                "EPS": info.get("trailingEps", None),
                "PBR": info.get("priceToBook", None),
                "ROE": info.get("returnOnEquity", None),
            })
        except:
            data.append({
                "종목": symbol,
                "티커": symbol,
                "시가총액": 0,
                "PER": None,
                "EPS": None,
                "PBR": None,
                "ROE": None,
            })
    df = pd.DataFrame(data)
    df = df.sort_values(by="시가총액", ascending=False).reset_index(drop=True)
    df["시가총액순위"] = df.index + 1
    return df

def show_marketcap_page(df):
    st.title("📈 시가총액 Top 기업 분석")
    min_rank, max_rank = st.slider(
        "시가총액 순위 범위 선택",
        min_value=1, max_value=len(df),
        value=(1, 20)
    )
    selected = df[(df["시가총액순위"] >= min_rank) & (df["시가총액순위"] <= max_rank)]
    st.write(f"{min_rank}위 부터 {max_rank}위 까지 기업")
    st.dataframe(selected[["시가총액순위", "종목", "티커", "시가총액"]], use_container_width=True)

def show_growth_value_page(df):
    st.title("🚀 성장가치 높은 기업 모음")
    filtered = df[
        (df["PER"].notnull()) & (df["PER"] <= 30)
    ].copy()
    filtered["ROE(%)"] = (filtered["ROE"] * 100).round(2)
    filtered = filtered.sort_values(by="PER").reset_index(drop=True)
    st.dataframe(filtered[["종목", "티커", "시가총액", "PER", "EPS", "PBR", "ROE(%)"]], use_container_width=True)

def main():
    df = load_data()
    page = st.sidebar.radio("페이지 선택", ["시가총액 분석", "성장가치 기업"])
    if page == "시가총액 분석":
        show_marketcap_page(df)
    else:
        show_growth_value_page(df)

if __name__ == "__main__":
    main()
