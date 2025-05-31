import streamlit as st
import yfinance as yf
import pandas as pd

st.title("📈 yfinance 기반 주식 추천 리스트")
st.markdown("yfinance에서 수집한 추천등급(`recommendationKey`) 기준으로 정렬된 종목 리스트입니다.")

# 분석 대상 종목 리스트 (자유롭게 수정 가능)
symbols = ["AAPL", "MSFT", "GOOGL", "NVDA", "TSLA", "AMZN", "META", "NFLX", "BABA", "INTC"]

data = []

with st.spinner("📡 주식 정보 수집 중..."):
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            rec = info.get("recommendationKey", "N/A")
            price = info.get("currentPrice", 0)
            pe = info.get("forwardPE", 0)
            market_cap = info.get("marketCap", 0)
            name = info.get("shortName", symbol)

            data.append({
                "종목": name,
                "티커": symbol,
                "추천등급": rec,
                "현재주가($)": price,
                "PER": pe,
                "시가총액(십억$)": round(market_cap / 1e9, 2) if market_cap else None
            })

        except Exception as e:
            st.error(f"{symbol} 데이터 오류: {e}")

# 추천 우선순위 정렬 기준 정의
recommendation_order = {
    "strong_buy": 1,
    "buy": 2,
    "hold": 3,
    "underperform": 4,
    "sell": 5,
    "N/A": 6
}

# 정렬 및 출력
df = pd.DataFrame(data)
df["추천순위"] = df["추천등급"].map(recommendation_order)
df = df.sort_values(by=["추천순위", "PER"]).reset_index(drop=True)

st.success("✅ 종목 추천 결과를 아래에 표시했습니다.")
st.dataframe(df.drop(columns=["추천순위"]), use_container_width=True)
