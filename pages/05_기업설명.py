import streamlit as st
import yfinance as yf
import pandas as pd
from googletrans import Translator

# 종목 리스트
symbols = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "BRK-B", "JPM", "V",
    "UNH", "HD", "MA", "PYPL", "BAC", "DIS", "ADBE", "CMCSA", "NFLX", "XOM",
    "PFE", "KO", "PEP", "CSCO", "T", "VZ", "ABT", "MRK", "CRM", "INTC",
    "WMT", "CVX", "ACN", "AVGO", "COST", "ORCL", "TXN", "NEE", "QCOM", "MDT",
    "LIN", "TMO", "UPS", "PM", "BA", "IBM", "MMM", "CAT", "RTX", "GE"
]

# 번역기 초기화
translator = Translator()

def translate_text(text, dest='ko'):
    try:
        translated = translator.translate(text, dest=dest)
        return translated.text
    except Exception as e:
        return f"번역 실패: {e}"

# 데이터 로드
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
                "설명": info.get("longBusinessSummary", "설명 없음")
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
                "설명": "설명 없음"
            })
    df = pd.DataFrame(data)
    df = df.sort_values(by="시가총액", ascending=False).reset_index(drop=True)
    df["시가총액순위"] = df.index + 1
    return df

# 시가총액 페이지
def show_marketcap_page(df):
    st.title("📈 시가총액 Top 기업 분석")
    min_rank, max_rank = st.slider(
        "시가총액 순위 범위 선택",
        min_value=1, max_value=len(df),
        value=(1, 20)
    )
    selected = df[(df["시가총액순위"] >= min_rank) & (df["시가총액순위"] <= max_rank)]
    st.write(f"📊 {min_rank}위부터 {max_rank}위까지 기업 리스트")
    st.dataframe(selected[["시가총액순위", "종목", "티커", "시가총액"]], use_container_width=True)

    # ✅ 선택한 기업 설명 번역 표시
    selected_ticker = st.selectbox("🔍 기업 설명 보기", selected["티커"])
    company_info = df[df["티커"] == selected_ticker].iloc[0]
    st.markdown(f"### 🏢 {company_info['종목']} ({company_info['티커']})")

    original_desc = company_info["설명"]
    translated_desc = translate_text(original_desc)

    with st.expander("📘 기업 설명 원문 (영어)"):
        st.write(original_desc)

    st.write("📖 한글 번역:")
    st.success(translated_desc)

# 성장가치 페이지
def show_growth_value_page(df):
    st.title("🚀 성장가치 높은 기업 모음")
    filtered = df[
        (df["PER"].notnull()) & (df["PER"] <= 30)
    ].copy()
    filtered["ROE(%)"] = (filtered["ROE"] * 100).round(2)
    filtered = filtered.sort_values(by="PER").reset_index(drop=True)
    st.dataframe(filtered[["종목", "티커", "시가총액", "PER", "EPS", "PBR", "ROE(%)"]], use_container_width=True)

# 메인
def main():
    st.set_page_config(page_title="미국 주식 기업 분석", layout="wide")
    df = load_data()
    page = st.sidebar.radio("페이지 선택", ["시가총액 분석", "성장가치 기업"])
    if page == "시가총액 분석":
        show_marketcap_page(df)
    else:
        show_growth_value_page(df)

if __name__ == "__main__":
    main()
