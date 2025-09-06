import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
import datetime

# 페이지 레이아웃 넓게 설정 (특히 모바일에서 유용)
st.set_page_config(page_title="주가 차트 대시보드", layout="wide")

st.title("📈 주가 차트 대시보드")

# 종목 선택
stocks = {
    "Apple": "AAPL",
    "Tesla": "TSLA",
    "Amazon": "AMZN",
    "Google": "GOOGL",
    "Microsoft": "MSFT"
}
stock_name = st.selectbox("분석할 종목 선택", list(stocks.keys()))
ticker = stocks[stock_name]

# 날짜 선택
end_date = datetime.date.today()
start_date = st.date_input("시작 날짜 선택", end_date - datetime.timedelta(days=90))
if start_date >= end_date:
    st.error("시작 날짜는 종료 날짜보다 이전이어야 합니다.")
    st.stop()

# yfinance 데이터 로드 캐싱
@st.cache_data(show_spinner=False)
def load_data(ticker, start, end):
    try:
        df = yf.download(ticker, start=start, end=end, auto_adjust=True, threads=False)
        return df
    except Exception as e:
        st.error(f"주가 데이터 로드 중 오류 발생: {e}")
        return None

df = load_data(ticker, start_date, end_date)

if df is None or df.empty:
    st.warning("해당 기간에 주가 데이터가 없습니다.")
else:
    # Close 컬럼 없으면 Adj Close 컬럼 사용
    if "Close" in df.columns:
        price_col = "Close"
    elif "Adj Close" in df.columns:
        price_col = "Adj Close"
    else:
        st.error("'Close' 또는 'Adj Close' 컬럼이 데이터에 없습니다.")
        st.stop()

    # 결측치 제거 및 인덱스 초기화
    df = df.dropna(subset=[price_col]).reset_index()

    # 데이터 미리보기 (필요시 주석처리 가능)
    st.write(f"### {stock_name} ({ticker}) 주가 데이터 미리보기")
    st.dataframe(df[["Date", price_col]].head())

    # 그래프 그리기
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Date"], y=df[price_col], mode="lines", name="종가"))
    fig.update_layout(
        title=f"{stock_name} ({ticker}) 주가 차트",
        xaxis_title="날짜",
        yaxis_title="가격 (USD)",
        template="plotly_white",
        xaxis_rangeslider_visible=True
    )
    st.plotly_chart(fig, use_container_width=True)
