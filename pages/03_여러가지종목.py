import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

def rec_to_korean(rec):
    mapping = {
        "strong_buy": "강력 매수",
        "buy": "매수",
        "hold": "중립",
        "underperform": "성능 저하",
        "sell": "매도",
        "N/A": "정보 없음"
    }
    return mapping.get(rec, "정보 없음")

rec_priority = {
    "strong_buy": 5,
    "buy": 4,
    "hold": 3,
    "underperform": 2,
    "sell": 1,
    "N/A": 0
}

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

            market_cap = info.get("marketCap", 0)
            name = info.get("shortName", symbol)
            rec = info.get("recommendationKey", "N/A")
            price = info.get("currentPrice", 0)
            pe = info.get("forwardPE", None)
            eps = info.get("trailingEps", None)
            pbr = info.get("priceToBook", None)
            roe = info.get("returnOnEquity", None)  # 0~1 사이 비율

            data.append({
                "종목": name,
                "티커": symbol,
                "추천등급(원문)": rec,
                "현재주가($)": price,
                "PER": pe,
                "EPS": eps,
                "PBR": pbr,
                "ROE": roe,
                "시가총액": market_cap
            })
        except:
            data.append({
                "종목": symbol,
                "티커": symbol,
                "추천등급(원문)": "N/A",
                "현재주가($)": None,
                "PER": None,
                "EPS": None,
                "PBR": None,
                "ROE": None,
                "시가총액": 0
            })
    df = pd.DataFrame(data)
    return df

df = load_data()
df["추천등급"] = df["추천등급(원문)"].apply(rec_to_korean)
df["우선순위"] = df["추천등급(원문)"].map(rec_priority).fillna(0)
df = df.sort_values(by="시가총액", ascending=False).reset_index(drop=True)
df["시가총액순위"] = df.index + 1

page = st.sidebar.radio("페이지 선택", ["시가총액 분석", "추천등급 순 정렬", "성장가치 기업"])

def shorten_name(name, max_len=15):
    return (name[:max_len] + '...') if len(name) > max_len else name

if page == "성장가치 기업":
    st.title("🚀 성장가치 높은 기업 모음 (주요 재무 지표)")
    st.markdown("""
    - PER이 낮고, 추천등급이 좋은 기업들을 필터링했습니다.
    - 시가총액은 낮아도 성장 잠재력이 높은 기업들입니다.
    - 주요 지표: PER, EPS, PBR, ROE
    """)

    growth_df = df[
        (df["PER"].notna()) &
        (df["PER"] <= 30) &
        (df["추천등급(원문)"].isin(["strong_buy", "buy"]))
    ].sort_values(by="PER").reset_index(drop=True)

    # ROE를 %로 바꾸고 소수점 2자리로
    growth_df["ROE(%)"] = (growth_df["ROE"] * 100).round(2)

    if growth_df.empty:
        st.write("조건에 맞는 기업이 없습니다.")
    else:
        st.dataframe(growth_df[["종목", "티커", "추천등급", "현재주가($)", "PER", "EPS", "PBR", "ROE(%)", "시가총액"]], use_container_width=True)
