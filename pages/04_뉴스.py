# ✅ 주가 차트 출력 (안정성 보강)
st.subheader(f"💹 {stock_name} 주가 차트")

# ▶️ 데이터 존재 여부 확인
if stock_data is None or stock_data.empty:
    st.warning("📭 주가 데이터가 없습니다.")
else:
    # ▶️ 사용 가능한 종가 컬럼 확인
    price_col = None
    if "Close" in stock_data.columns:
        price_col = "Close"
    elif "Adj Close" in stock_data.columns:
        price_col = "Adj Close"

    # ▶️ 종가 컬럼이 없을 때 경고
    if price_col is None:
        st.warning(f"⚠️ 'Close' 또는 'Adj Close' 컬럼이 없습니다. 현재 컬럼: {list(stock_data.columns)}")
    # ▶️ 'Date' 컬럼이 없을 경우 reset_index로 생성
    else:
        try:
            if 'Date' not in stock_data.columns:
                stock_data = stock_data.reset_index()

            if price_col not in stock_data.columns:
                st.error(f"❌ '{price_col}' 컬럼이 데이터에 없습니다.")
            else:
                stock_data = stock_data.dropna(subset=[price_col])
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
        except Exception as e:
            st.error(f"❌ 차트 렌더링 중 오류 발생: {e}")
