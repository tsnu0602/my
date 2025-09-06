import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
import datetime
import pandas as pd

st.set_page_config(page_title="📈 주가 차트 테스트", layout="centered")
st.title("주가 차트 테스트")

ticker = st.text_input("티커 입력", "AAPL")
start_date = st.date_input("시작 날짜", datetime.date.today() - datetime.timedelta(days=90))
end_date = st.date_input("종료 날짜", datetime.date.today())

def find_price_column(df):
    candidates = ['Close', 'close', 'Adj Close', 'adj close', 'AdjClose']
    for c in candidates:
        if c in df.columns:
            return c
    return None

if ticker and start_date < end_date:
    with st.spinner("데이터 불러오는 중..."):
        try:
            stock_data = yf.download(ticker, start=start_date, end=end_date)
            st.write("데이터 컬럼:", stock_data.columns.tolist())

            # MultiIndex 컬럼이면 레벨 낮추기
            if isinstance(stock_data.columns, pd.MultiIndex):
                stock_data.columns = stock_data.columns.get_level_values(-1)
                st.write("MultiIndex 해제 후 컬럼:", stock_data.columns.tolist())

            price_col = find_price_column(stock_data)
            if price_col is None:
                st.error("주가 컬럼을 찾을 수 없습니다. 컬럼명 리스트: " + ", ".join(stock_data.columns))
            else:
                stock_data = stock_data.dropna(subset=[price_col])
                if stock_data.empty:
                    st.warning("데이터가 없습니다.")
                else:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data[price_col], mode='lines', name=price_col))
                    fig.update_layout(title=f"{ticker} 주가", xaxis_title="날짜", yaxis_title="가격 (USD)")
                    st.plotly_chart(fig)
        except Exception as e:
            st.error(f"데이터 처리 오류: {e}")
else:
    st.info("유효한 티커와 날짜를 입력하세요.")
