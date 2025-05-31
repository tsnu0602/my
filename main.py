import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

st.title("📈 yfinance 기반 주식 추천 및 시가총액 분석")

st.markdown("""
### 추천등급 매핑 (영어 → 한국어)
- **strong_buy** → 강력 매수  
- **buy** → 매수  
- **hold** → 중립  
- **underperform** → 성능 저하  
- **sell** → 매도  
- **N/A** → 정보 없음

---

- 상단 슬라이더로 시가총액 순위 범위를 지정하세요 (예: 1위부터 200위까지)
- 선택 범위 내 종목들의 추천 등급과 시가총액 데이터를 보여줍니다.
""")

# 샘플로 NYSE 시가총액 상위 50개 종목 티커 (필요시 확장 가능)
symbols = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "BRK-B", "JPM", "V",
    "UNH", "HD", "MA", "PYPL", "BAC", "DIS", "ADBE", "CMCSA", "NFLX", "XOM",
    "PFE", "KO", "PEP", "CSCO", "T", "VZ", "ABT", "MRK", "CRM", "INTC",
    "WMT", "CVX", "ACN", "AVGO", "COST", "ORCL", "TXN", "NEE", "QCOM", "MDT",
    "LIN", "TMO", "UPS", "PM", "BA", "IBM", "MMM", "CAT", "RTX", "GE"
]

data = []
with st.spinner("📡 주식 정보 수집 중... (최대 50개)"):
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            market_cap = info.get("marketCap", 0)
            name = info.get("shortName", symbol)
            rec = info.get("recommendationKey", "N/A")
            price = info.get("currentPrice", 0)
            pe = info.get("forwardPE", None)

            data.append({
                "종목": name,
                "티커": symbol,
                "추천등급(원문)": rec,
                "현재주가($)": price,
                "PER": pe,
                "시가총액": market_cap
            })
        except Exception as e:
            st.error(f"{symbol} 데이터 오류: {e}")

df = pd.DataFrame(data)

df = df.sort_values(by="시가총액", ascending=False).reset_index(drop=True)
df["시가총액순위"] = df.index + 1

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

df["추천등급"] = df["추천등급(원문)"].apply(rec_to_korean)

min_rank, max_rank = st.slider(
    "시가총액 순위 범위 선택",
    min_value=1,
    max_value=len(df),
    value=(1, min(50, len(df))),
    step=1
)

filtered_df = df[(df["시가총액순위"] >= min_rank) & (df["시가총액순위"] <= max_rank)].reset_index(drop=True)

st.subheader(f"선택된 시가총액 순위 범위: {min_rank}위 ~ {max_rank}위")
st.dataframe(filtered_df[["시가총액순위", "종목", "티커", "추천등급", "현재주가($)", "PER", "시가총액"]], use_container_width=True)

# 시가총액 그래프 그리기 (기업명 가독성 개선)
fig, ax = plt.subplots(figsize=(10, 6))

def shorten_name(name, max_len=15):
    return (name[:max_len] + '...') if len(name) > max_len else name

labels = [shorten_name(name) for name in filtered_df["종목"]]

bars = ax.barh(labels, filtered_df["시가총액"] / 1e9, color="#1f77b4", edgecolor="black", alpha=0.85)

ax.xaxis.set_major_formatter(mtick.FormatStrFormatter('%.1fB'))
ax.invert_yaxis()
ax.set_xlabel("시가총액 (십억 달러)", fontsize=12, fontweight='bold')
ax.set_title("선택된 기업 시가총액 순위별 막대그래프", fontsize=14, fontweight='bold', pad=15)
ax.grid(axis='x', linestyle='--', alpha=0.5)

for bar in bars:
    width = bar.get_width()
    ax.text(width + 0.5, bar.get_y() + bar.get_height()/2,
            f'{width:.1f}B', va='center', fontsize=10, color='black')

plt.tight_layout()
st.pyplot(fig)
