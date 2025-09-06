import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
import datetime

st.set_page_config(page_title="📈 주가 차트 테스트", layout="centered")
st.title("주가 차트 테스트")

ticker = st.text_input("티커 입력", "AAPL")
start_date = st.date_input("시작 날짜", datetime.date.today() - datetime.timedelta(days=90))
end_date = st.date_input("종료 날짜", datetime.date.today())

if ticker and start_date < end_date:
    with st.spinner("데이터 불러오는 중..."):
        try:
            stock_data = yf.download(ticker, start=start_date, end=end_date)
            st.write("데이터 컬럼:", stock_data.columns)
            if isinstance(stock_data.columns, pd.MultiIndex):
                st.warning("MultiIndex 컬럼입니다. 단일 레벨로 변환합니다.")
                stock_data.columns = stock_data.columns.get_level_values(-1)
            stock_data.columns = [col.capitalize() for col in stock_data.columns]  # 'close' -> 'Close' 등 통일
            
            # 'Close' 컬럼 체크
            if 'Close' not in stock_data.columns:
                st.error("'Close' 컬럼이 데이터에 없습니다.")
            else:
                stock_data = stock_data.dropna(subset=['Close'])
                if stock_data.empty:
                    st.warning("데이터가 없습니다.")
                else:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['Close'], mode='lines', name='Close'))
                    fig.update_layout(title=f"{ticker} 주가", xaxis_title="날짜", yaxis_title="가격 (USD)")
                    st.plotly_chart(fig)
        except Exception as e:
            st.error(f"데이터 처리 오류: {e}")
else:
    st.info("유효한 티커와 날짜를 입력하세요.")
