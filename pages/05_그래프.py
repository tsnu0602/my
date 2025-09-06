import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
import datetime

st.set_page_config(page_title="📈 주가 차트 테스트", layout="centered")
st.title("🧪 주가 차트 확인")

# 종목 선택
stock_name = st.selectbox("종목을 선택하세요", ["Apple", "Tesla", "Amazon", "Google", "Microsoft"])
stocks = {
    "Apple": "AAPL",
    "Tesla": "TSLA",
    "Amazon": "AMZN",
    "Google": "GOOGL",
    "Microsoft": "MSFT"
}
ticker = stocks[stock_name]

# 날짜 선택
end_date = datetime.date.today()
start_date = end_date - datetime.timedelta(days=90)

# 데이터 불러오기
stock_data = yf.download(ticker, start=start_date, end=end_date)

# 데이터 확인 출력
st.write("📋 불러온 주가 데이터:")
st.write(stock_data.head())
st.write("✅ 컬럼 목록:", stock_data.columns.tolist())

# 차트 그리기
if stock_data.empty:
    st.warning("⚠️ 주가 데이터가 비어 있습니다.")
else:
    # 종가 컬럼 선택
    price_col = None
    if "Close" in stock_data.columns:
        price_col = "Close"
    elif "Adj Close" in stock_data.columns:
        price_col = "Adj Close"

    if not price_col:
        st.error("❌ 'Close' 또는 'Adj Close' 컬럼이 없습니다.")
    else:
        stock_data = stock_data.dropna(subset=[price_col]).reset_index()

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=stock_data["Date"],
            y=stock_data[price_col],
            mode="lines",
            name=price_col
        ))
        fig.update_layout(
            title=f"{stock_name} ({ticker}) 주가 차트",
            xaxis_title="날짜",
            yaxis_title="가격 (USD)",
            template="plotly_white",
            xaxis_rangeslider_visible=True
        )
        st.plotly_chart(fig)

